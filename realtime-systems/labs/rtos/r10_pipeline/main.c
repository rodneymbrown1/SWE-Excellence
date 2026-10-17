/* R10 -- capstone: a small sample -> filter -> control -> actuator pipeline with three planted defects.
 *
 *   TIMER1 ISR  ~1 kHz  reads the "IMU" (one raw sample per 997 us: a sensor runs on its own oscillator, not on our tick)
 *   filter      prio 4  turns each raw sample into an attitude estimate and publishes it in the shared struct `att`
 *   control     prio 3  100 Hz: reads `att`, computes a command, posts it
 *   actuator    prio 5  applies the newest command
 *   logger      prio 6  every 50 ms formats a telemetry report
 *
 * REQUIREMENTS (the contract this system is supposed to meet):
 *   R-1  no IMU sample is lost between the interrupt and the filter
 *   R-2  the attitude estimate is published <= 3 ms after its IMU interrupt, for 99.9% of samples
 *   R-3  control reads one consistent attitude estimate per cycle
 *   R-4  every task meets its period
 *
 * The first look below says everything is fine.  It is not.  Find out why, with evidence, before you change code.
 */
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"
#include "bsp.h"

#ifndef DUMP
#define DUMP 0
#endif
#ifndef REVEAL
#define REVEAL 0
#endif
#ifndef DUMP_TRACE
#define DUMP_TRACE 0
#endif
#define RUN_SAMPLES 3000         /* about 3 s at 997 us per sample */
#define IMU_PERIOD_US 997
#define RAW_DEPTH 4

typedef struct { uint32_t seq, t_us; int32_t gyro; } raw_t;
typedef struct { uint32_t seq, t_us; int32_t angle; int32_t angle_inv; } att_t;      /* invariant: angle_inv == ~angle */
typedef struct { uint32_t seq, t_us; int32_t value; } cmd_t;

static QueueHandle_t q_raw, q_cmd;
static volatile att_t att;                          /* written by filter, read by control */

/* counters (nothing prints most of these -- you have to go and look) */
static volatile uint32_t produced, filtered, commanded, actuated, dropped_raw, torn, isr_late, ctrl_cycles, ctrl_late;
static uint32_t lat_us[3200], nlat;                /* per-sample latency: IMU interrupt -> estimate published */
static volatile uint32_t done;

static void imu_isr(void) {
    static uint32_t last, seq;
    uint32_t now = now_us();
    if (last && now - last > 1500) isr_late++;                 /* the 1 kHz interrupt was delayed */
    last = now;
    BaseType_t woken = pdFALSE;
    raw_t r = { seq++, now, (int32_t)(seq * 7) };
    produced++;
    if (xQueueSendFromISR(q_raw, &r, &woken) != pdTRUE) {
        dropped_raw++;
    }
    if (seq >= RUN_SAMPLES) { timer1_stop(); done = 1; }
    portYIELD_FROM_ISR(woken);
}

static void filter(void *arg) {
    raw_t r;
    for (;;) {
        xQueueReceive(q_raw, &r, portMAX_DELAY);
        burn_us(400);                                          /* the filter maths */
        if (r.seq % 250 == 249) burn_us(6000);                 /* rare slow path: recalibration */
        int32_t a = r.gyro * 3;
        att.angle = a;
        att.angle_inv = ~a;
        att.t_us = r.t_us;
        att.seq = r.seq;
        filtered++;
        if (nlat < 3200) lat_us[nlat++] = now_us() - r.t_us;
    }
}

static void control(void *arg) {
    TickType_t last = xTaskGetTickCount();
    uint32_t prev = now_us();
    for (;;) {
        vTaskDelayUntil(&last, pdMS_TO_TICKS(10));
        uint32_t t0 = now_us();
        if (t0 - prev > 11000) ctrl_late++;                    /* period overshoot > 10% */
        prev = t0;
        int32_t a = att.angle;                                 /* read 1 */
        uint32_t s1 = att.seq;
        burn_us(150);                                          /* compute with 'a' */
        uint32_t ts = att.t_us;                                /* read 2: assumes it describes the same sample as 'a' */
        uint32_t s2 = att.seq;
        if (s1 != s2) torn++;
        cmd_t c = { s2, ts, a / 2 };
        xQueueOverwrite(q_cmd, &c);
        commanded++; ctrl_cycles++;
    }
}

static void actuator(void *arg) {
    cmd_t c;
    for (;;) {
        xQueueReceive(q_cmd, &c, portMAX_DELAY);
        burn_us(200);                                          /* apply the command */
        actuated++;
    }
}

static void logger(void *arg) {
    TickType_t last = xTaskGetTickCount();
    for (;;) {
        vTaskDelayUntil(&last, pdMS_TO_TICKS(50));
        burn_us(3000);                                         /* format a telemetry report (CPU work, no I/O) */
    }
}

static void manager(void *arg) {
    kprintf("R10: pipeline, %d IMU samples\n", RUN_SAMPLES);
    q_raw = xQueueCreate(RAW_DEPTH, sizeof(raw_t));
    q_cmd = xQueueCreate(1, sizeof(cmd_t));
    TaskHandle_t h[4];
    xTaskCreate(filter,   "filter",   2 * configMINIMAL_STACK_SIZE, NULL, 4, &h[0]);
    xTaskCreate(control,  "control",  2 * configMINIMAL_STACK_SIZE, NULL, 3, &h[1]);
    xTaskCreate(actuator, "actuator", 2 * configMINIMAL_STACK_SIZE, NULL, 5, &h[2]);
    xTaskCreate(logger,   "logger",   2 * configMINIMAL_STACK_SIZE, NULL, 6, &h[3]);
    for (int i = 0; i < 4; i++) vTaskSetTaskNumber(h[i], (UBaseType_t)(i + 1));
    vTaskDelay(1);
    trace_reset();
    timer1_start(IMU_PERIOD_US, imu_isr);
    while (!done) vTaskDelay(10);
    vTaskDelay(pdMS_TO_TICKS(100));

    uint64_t sum = 0; for (uint32_t i = 0; i < nlat; i++) sum += lat_us[i];
    kprintf("\n--- first look (what a dashboard would show) ---\n");
    kprintf("samples produced   : %lu\n", (unsigned long)produced);
    kprintf("estimates published: %lu\n", (unsigned long)filtered);
    kprintf("commands applied   : %lu\n", (unsigned long)actuated);
    kprintf("mean latency       : %lu us\n", (unsigned long)(nlat ? sum / nlat : 0));
    kprintf("control cycles     : %lu (expected ~%d)\n", (unsigned long)ctrl_cycles, (RUN_SAMPLES * IMU_PERIOD_US / 1000 + 100) / 10);
    if (REVEAL) {                                              /* answer key: the counters nothing prints */
        kprintf("[reveal] dropped_raw=%lu torn=%lu isr_late=%lu ctrl_late=%lu filtered=%lu\n", (unsigned long)dropped_raw, (unsigned long)torn,
                (unsigned long)isr_late, (unsigned long)ctrl_late, (unsigned long)filtered);
    }
    if (DUMP) { for (uint32_t i = 0; i < nlat; i++) kprintf("L %lu\n", (unsigned long)lat_us[i]); }
    if (DUMP_TRACE) { kprintf("N 1 filter\nN 2 control\nN 3 actuator\nN 4 logger\n"); trace_dump(); }
    bsp_exit(0);
}

int main(void) {
    xTaskCreate(manager, "manager", 3 * configMINIMAL_STACK_SIZE, NULL, 7, NULL);
    vTaskStartScheduler();
    for (;;) { }
}
