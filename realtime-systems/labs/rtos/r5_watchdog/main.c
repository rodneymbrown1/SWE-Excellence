/* R5: who feeds the watchdog?  Three designs, one injected fault.
 *
 * A watchdog is a down-counter that resets the CPU unless software reloads ("feeds") it in time.  Here it is emulated
 * by the TIMER1 interrupt (1 ms steps, timeout 400 ms); on expiry it writes a reset request (SYSRESETREQ).
 *
 *   build with MODE=1 : the timer ISR feeds the dog                       (what the Toyota slides criticise: "kicked by a timer ISR")
 *   build with MODE=2 : the lowest-priority task feeds the dog            (the naive RTOS design from the Memfault article)
 *   build with MODE=3 : a supervisor feeds ONLY if every task checked in  (the "task watchdog" design)
 *
 * Fault: after 15 cycles the `control` task blocks forever on a lock that nobody will ever release (a deadlock).
 * Question for each mode: does the system notice?  After a reset, the next boot reads the saved diagnostics (.noinit).
 */
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"
#include "event_groups.h"
#include "bsp.h"

#ifndef WDG_MODE
#define WDG_MODE 3
#endif
#define WDG_TIMEOUT_MS 400
#define CHK_SENSOR  (1u << 0)
#define CHK_CONTROL (1u << 1)
#define CHK_LOGGER  (1u << 2)
#define CHK_ALL     (CHK_SENSOR | CHK_CONTROL | CHK_LOGGER)
#define MAGIC 0xD06F00D5u

typedef struct { uint32_t magic, missing, tick, mode; } postmortem_t;
static postmortem_t pm __attribute__((section(".noinit")));

static volatile uint32_t wdt_counter = WDG_TIMEOUT_MS;
static volatile uint32_t last_missing;
static EventGroupHandle_t checkins;
static SemaphoreHandle_t deadlock_lock;
static volatile uint32_t sensor_n, control_n, logger_n, feeds;

static void wdt_feed(void) { wdt_counter = WDG_TIMEOUT_MS; feeds++; }

static void wdt_isr(void) {                        /* runs every 1 ms */
    static uint32_t ms;
    ms++; (void)ms;
#if WDG_MODE == 1
    if (ms % 10 == 0) wdt_feed();                  /* MODE 1: feed from the interrupt -- feeds even if every task is dead */
#endif
    if (--wdt_counter == 0) {
        pm.magic = MAGIC; pm.missing = last_missing; pm.tick = (uint32_t)xTaskGetTickCountFromISR(); pm.mode = WDG_MODE;
        *(volatile uint32_t *)0xE000ED0C = 0x05FA0004;   /* AIRCR.SYSRESETREQ */
        for (;;) { }
    }
}

static void sensor(void *a) {
    TickType_t last = xTaskGetTickCount();
    for (;;) { burn_us(300); sensor_n++; xEventGroupSetBits(checkins, CHK_SENSOR); vTaskDelayUntil(&last, pdMS_TO_TICKS(10)); }
}

static void control(void *a) {
    TickType_t last = xTaskGetTickCount();
    for (;;) {
        if (control_n == 15) xSemaphoreTake(deadlock_lock, portMAX_DELAY);   /* FAULT: waits for a lock nobody holds a way out of */
        burn_us(500); control_n++; xEventGroupSetBits(checkins, CHK_CONTROL);
        vTaskDelayUntil(&last, pdMS_TO_TICKS(20));
    }
}

static void logger(void *a) {
    TickType_t last = xTaskGetTickCount();
    for (;;) { burn_us(200); logger_n++; xEventGroupSetBits(checkins, CHK_LOGGER); vTaskDelayUntil(&last, pdMS_TO_TICKS(100)); }
}

static void ghost(void *a) {                       /* takes the lock and never returns it */
    xSemaphoreTake(deadlock_lock, portMAX_DELAY);
    vTaskSuspend(NULL);
}

static void dog_feeder(void *a) {                  /* lowest priority (modes 2 and 3) */
    TickType_t last = xTaskGetTickCount();
    for (;;) {
        vTaskDelayUntil(&last, pdMS_TO_TICKS(150)); /* longer than the slowest task period (100 ms) */
#if WDG_MODE == 2
        wdt_feed();                                 /* MODE 2: "I got to run, so the system must be fine" */
#elif WDG_MODE == 3
        uint32_t bits = xEventGroupClearBits(checkins, CHK_ALL);   /* returns the bits as they were before clearing */
        if ((bits & CHK_ALL) == CHK_ALL) wdt_feed();
        else last_missing = CHK_ALL & ~bits;        /* remember WHO is missing, for the post-mortem; do not feed */
#endif
    }
}

static void reporter(void *a) {
    vTaskDelay(pdMS_TO_TICKS(1500));
    kprintf("[%4lu ms] end of run (no watchdog reset happened)\n", (unsigned long)(xTaskGetTickCount()));
    kprintf("  sensor cycles=%lu  control cycles=%lu  logger cycles=%lu  watchdog feeds=%lu\n",
            (unsigned long)sensor_n, (unsigned long)control_n, (unsigned long)logger_n, (unsigned long)feeds);
    kprintf("  -> control stopped at cycle 15 (t ~ 300 ms) and the system never noticed.\n");
    bsp_exit(0);
}

int main(void) {
    if (pm.magic == MAGIC) {
        kprintf("BOOT: previous run ended in a WATCHDOG RESET (mode %lu) at tick %lu\n", (unsigned long)pm.mode, (unsigned long)pm.tick);
        kprintf("      tasks that had NOT checked in: %s%s%s\n", (pm.missing & CHK_SENSOR) ? "sensor " : "", (pm.missing & CHK_CONTROL) ? "control " : "",
                (pm.missing & CHK_LOGGER) ? "logger " : "");
        pm.magic = 0;
        bsp_exit(0);
    }
    kprintf("R5: watchdog mode %d (1 = feed from ISR, 2 = feed from low-priority task, 3 = feed only if all tasks checked in)\n", WDG_MODE);
    checkins = xEventGroupCreate();
    deadlock_lock = xSemaphoreCreateMutex();
    xTaskCreate(ghost,      "ghost",   configMINIMAL_STACK_SIZE, NULL, 1, NULL);
    xTaskCreate(sensor,     "sensor",  configMINIMAL_STACK_SIZE, NULL, 4, NULL);
    xTaskCreate(control,    "control", configMINIMAL_STACK_SIZE, NULL, 3, NULL);
    xTaskCreate(logger,     "logger",  configMINIMAL_STACK_SIZE, NULL, 2, NULL);
    xTaskCreate(dog_feeder, "dog",     configMINIMAL_STACK_SIZE, NULL, 1, NULL);
    xTaskCreate(reporter,   "report",  configMINIMAL_STACK_SIZE * 2, NULL, 5, NULL);
    timer1_start(1000, wdt_isr);
    vTaskStartScheduler();
    for (;;) { }
}
