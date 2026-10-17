/* R1: time is not free.  Three measurements on a 1 kHz tick:
 *   (a) "do work, then vTaskDelay(10 ms)"            -> the period is work + 10 ms, and the error accumulates (drift)
 *   (b) "do work, then vTaskDelayUntil(&last, 10 ms)" -> the period is 10 ms; the error does not accumulate
 *   (c) vTaskDelay(1) called at different phases within a tick -> anywhere from ~0 to 1 tick
 * All times come from the 25 MHz hardware timer (now_us), not from the tick count. */
#include "FreeRTOS.h"
#include "task.h"
#include "bsp.h"

#define N       100
#define PERIOD  10          /* ms */
#define WORK_US 3000

static uint32_t stamp[N + 1];

static void report(const char *label) {
    uint32_t mn = 0xFFFFFFFFu, mx = 0, sum = 0;
    for (int i = 1; i < N; i++) { uint32_t d = stamp[i] - stamp[i - 1]; if (d < mn) { mn = d; }
        if (d > mx) { mx = d; } sum += d; }
    uint32_t total = stamp[N - 1] - stamp[0];
    kprintf("%-26s interval us: min=%5lu mean=%5lu max=%5lu | after %d iterations: elapsed=%lu us, ideal=%lu us, drift=%ld us\n",
            label, (unsigned long)mn, (unsigned long)(sum / (N - 1)), (unsigned long)mx, N - 1,
            (unsigned long)total, (unsigned long)((N - 1) * PERIOD * 1000UL), (long)(total - (N - 1) * PERIOD * 1000L));
}

static void experiment(void *arg) {
    (void)arg;
    kprintf("R1: tick = %d Hz (1 tick = %d us); work per iteration = %d us; wanted period = %d ms\n\n",
            (int)configTICK_RATE_HZ, (int)(1000000UL / configTICK_RATE_HZ), WORK_US, PERIOD);

    for (int i = 0; i < N; i++) { stamp[i] = now_us(); burn_us(WORK_US); vTaskDelay(pdMS_TO_TICKS(PERIOD)); }
    report("(a) work + vTaskDelay");

    TickType_t last = xTaskGetTickCount();
    for (int i = 0; i < N; i++) { stamp[i] = now_us(); burn_us(WORK_US); vTaskDelayUntil(&last, pdMS_TO_TICKS(PERIOD)); }
    report("(b) work + vTaskDelayUntil");

    /* (c) call vTaskDelay(1) at 40 different phases within a tick */
    uint32_t mn = 0xFFFFFFFFu, mx = 0;
    for (int phase_us = 0; phase_us < 1000; phase_us += 25) {
        vTaskDelay(1);                             /* synchronise to a tick boundary */
        burn_us((uint32_t)phase_us);               /* move to a known phase inside the tick */
        uint32_t t0 = now_us();
        vTaskDelay(1);
        uint32_t d = now_us() - t0;
        if (d < mn) { mn = d; }
        if (d > mx) { mx = d; }
    }
    kprintf("(c) vTaskDelay(1) lasted between %lu us and %lu us (one tick = 1000 us)\n", (unsigned long)mn, (unsigned long)mx);
    kprintf("\nLesson: a delay of N ticks is 'at least N-1 ticks plus the rest of the current one'. Use vTaskDelayUntil for periods.\n");
    bsp_exit(0);
}

int main(void) {
    xTaskCreate(experiment, "exp", 2 * configMINIMAL_STACK_SIZE, NULL, 2, NULL);
    vTaskStartScheduler();
    for (;;) { }
}
