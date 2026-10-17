/* R3: a Pathfinder-shaped priority inversion, on a real kernel.
 *
 *   bc_sched  (prio 6)  every 50 ms checks that bus_dist finished its previous cycle; if not it "resets" (counts + logs)
 *   bus_dist  (prio 5)  H: every 50 ms: 1 ms work, take LOCK, 2 ms, give LOCK, 1 ms           (deadline = 50 ms)
 *   comms     (prio 4)  M: every 100 ms: 40 ms of CPU-bound work (no lock)
 *   met       (prio 3)  L: every 200 ms: 2 ms, take LOCK, hold it for 10 ms of work, give LOCK, 2 ms
 *
 * Phase 1: LOCK is a binary semaphore (no priority inheritance).   Phase 2: LOCK is a mutex (basic priority inheritance).
 * The only difference between the phases is one line.  Set TRACE_PHASE to 1 or 2 to dump a trace of that phase's first 120 ms.
 */
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"
#include "bsp.h"

#ifndef TRACE_PHASE
#define TRACE_PHASE 0
#endif

static SemaphoreHandle_t lock;
static volatile uint32_t bus_done;               /* completed bus_dist jobs */
static volatile uint32_t resets;
static uint32_t H_resp[40], H_jobs, H_miss;
static TickType_t start_tick;

static void bc_sched(void *arg) {
    TickType_t last = start_tick;               /* NOTE: 'last' must never be in the future -- vTaskDelayUntil would not block */
    uint32_t k = 0;
    vTaskDelayUntil(&last, pdMS_TO_TICKS(5));   /* align so the checks fall just after bus_dist's deadlines (5 + 50k ms) */
    for (;;) {
        vTaskDelayUntil(&last, pdMS_TO_TICKS(50));
        k++;
        if (bus_done < k) {
            resets++;
            kprintf("  [%4lu ms] bc_sched: bus_dist did not finish its cycle -> RESET #%lu\n", (unsigned long)((last - start_tick)), (unsigned long)resets);
        }
    }
}

static void bus_dist(void *arg) {
    TickType_t last = start_tick;
    vTaskDelayUntil(&last, pdMS_TO_TICKS(5));      /* offset 5 ms */
    for (;;) {
        TickType_t rel = last;
        burn_us(1000);
        xSemaphoreTake(lock, portMAX_DELAY);
        burn_us(2000);
        xSemaphoreGive(lock);
        burn_us(1000);
        uint32_t R = (xTaskGetTickCount() - rel) * 1000UL / configTICK_RATE_HZ;
        if (H_jobs < 40) H_resp[H_jobs] = R;
        H_jobs++; if (R > 50) H_miss++;
        bus_done++;
        vTaskDelayUntil(&last, pdMS_TO_TICKS(50));
    }
}

static void comms(void *arg) {
    TickType_t last = start_tick;
    vTaskDelayUntil(&last, pdMS_TO_TICKS(6));
    for (;;) { burn_us(40000); vTaskDelayUntil(&last, pdMS_TO_TICKS(100)); }
}

static void met(void *arg) {
    TickType_t last = start_tick;
    for (;;) {
        burn_us(2000);
        xSemaphoreTake(lock, portMAX_DELAY);
        burn_us(10000);                           /* inside the critical section */
        xSemaphoreGive(lock);
        burn_us(2000);
        vTaskDelayUntil(&last, pdMS_TO_TICKS(200));
    }
}

static void phase(int n, const char *title) {
    kprintf("\n=== Phase %d: %s ===\n", n, title);
    lock = (n == 1) ? xSemaphoreCreateBinary() : xSemaphoreCreateMutex();
    if (n == 1) xSemaphoreGive(lock);             /* a binary semaphore starts empty; give it once so it can be taken */
    bus_done = resets = H_jobs = H_miss = 0;
    vTaskDelay(1);
    start_tick = xTaskGetTickCount();
    if (n == TRACE_PHASE) trace_reset();
    TaskHandle_t h[4];
    xTaskCreate(bc_sched, "bc_sched", 2 * configMINIMAL_STACK_SIZE, NULL, 6, &h[0]);
    xTaskCreate(bus_dist, "bus_dist", 2 * configMINIMAL_STACK_SIZE, NULL, 5, &h[1]);
    xTaskCreate(comms,    "comms",    2 * configMINIMAL_STACK_SIZE, NULL, 4, &h[2]);
    xTaskCreate(met,      "met",      2 * configMINIMAL_STACK_SIZE, NULL, 3, &h[3]);
    for (int i = 0; i < 4; i++) vTaskSetTaskNumber(h[i], (UBaseType_t)(i + 1));
    vTaskDelay(pdMS_TO_TICKS(1005));
    for (int i = 0; i < 4; i++) vTaskDelete(h[i]);
    kprintf("bus_dist: %lu jobs, response times of the first 6 (ms):", (unsigned long)H_jobs);
    for (int i = 0; i < 6; i++) kprintf(" %lu", (unsigned long)H_resp[i]);
    kprintf("\nbus_dist deadline misses (response > 50 ms): %lu     resets: %lu\n", (unsigned long)H_miss, (unsigned long)resets);
    vSemaphoreDelete(lock);
    if (n == TRACE_PHASE) {
        kprintf("N 1 bc_sched\nN 2 bus_dist\nN 3 comms\nN 4 met\n");
        trace_dump();
    }
}

static void manager(void *arg) {
    kprintf("R3: priority inversion. H=bus_dist(5) M=comms(4) L=met(3); H and L share LOCK.\n");
    phase(1, "LOCK = binary semaphore (no priority inheritance)");
    phase(2, "LOCK = mutex (priority inheritance)");
    bsp_exit(0);
}

int main(void) {
    xTaskCreate(manager, "manager", 3 * configMINIMAL_STACK_SIZE, NULL, 7, NULL);
    vTaskStartScheduler();
    for (;;) { }
}
