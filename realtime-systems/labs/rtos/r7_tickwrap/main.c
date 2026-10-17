/* R7: every counter wraps.  This build uses a 16-bit tick (configTICK_TYPE_WIDTH_IN_BITS = TICK_TYPE_WIDTH_16_BITS):
 * at 1 kHz it wraps every 65.536 s.  (A 32-bit tick wraps every 49.7 days -- same bug, longer fuse.)
 *
 * We jump the tick count to just before the wrap with xTaskCatchUpTicks() so you do not wait a minute.
 * Then: (1) a kernel delay across the wrap, (2) application code that compares ticks naively, (3) the safe comparison.
 */
#include "FreeRTOS.h"
#include "task.h"
#include "bsp.h"

static int naive_expired(TickType_t now, TickType_t deadline) { return now >= deadline; }
static int safe_expired(TickType_t now, TickType_t deadline) { return (int16_t)(TickType_t)(now - deadline) >= 0; }

static void test(void *arg) {
    kprintf("R7: sizeof(TickType_t) = %d bytes; wraps after %lu ticks\n", (int)sizeof(TickType_t), (unsigned long)portMAX_DELAY + 1UL);
    xTaskCatchUpTicks((TickType_t)(65500 - xTaskGetTickCount()));      /* "fast-forward" the clock to tick 65500 (it suspends the scheduler itself) */
    kprintf("tick count is now %lu (wraps in %lu ms)\n\n", (unsigned long)xTaskGetTickCount(), (unsigned long)(65536UL - xTaskGetTickCount()));

    /* (1) the kernel handles wrap in its own delays */
    TickType_t last = xTaskGetTickCount();
    uint32_t t0 = now_us();
    for (int i = 0; i < 6; i++) {
        vTaskDelayUntil(&last, pdMS_TO_TICKS(20));
        kprintf("  periodic wake %d: tick=%5lu  elapsed=%lu us\n", i, (unsigned long)xTaskGetTickCount(), (unsigned long)(now_us() - t0));
    }

    /* (2) application code: "do this for 100 ticks", started 30 ticks before the wrap */
    xTaskCatchUpTicks((TickType_t)(65506 - xTaskGetTickCount() % 65536 + (xTaskGetTickCount() > 65506 ? 65536 : 0)));
    TickType_t start = xTaskGetTickCount();
    TickType_t deadline = (TickType_t)(start + 100);
    kprintf("\n(2) start=%lu deadline=%lu (wrapped=%s)\n", (unsigned long)start, (unsigned long)deadline, deadline < start ? "yes" : "no");
    uint32_t n_naive = 0; uint32_t t1 = now_us();
    while (!naive_expired(xTaskGetTickCount(), deadline)) { n_naive++; vTaskDelay(1); }
    kprintf("    naive  (now >= deadline): loop ran %lu times, lasted %lu us   <- 100 ticks requested\n", (unsigned long)n_naive, (unsigned long)(now_us() - t1));

    xTaskCatchUpTicks((TickType_t)(65506 - xTaskGetTickCount() % 65536 + (xTaskGetTickCount() > 65506 ? 65536 : 0)));   /* same start for the safe version */
    start = xTaskGetTickCount();
    deadline = (TickType_t)(start + 100);
    uint32_t n_safe = 0; t1 = now_us();
    while (!safe_expired(xTaskGetTickCount(), deadline)) { n_safe++; vTaskDelay(1); }
    kprintf("    start=%lu deadline=%lu\n", (unsigned long)start, (unsigned long)deadline);
    kprintf("    safe   ((int16)(now-deadline) >= 0): loop ran %lu times, lasted %lu us\n", (unsigned long)n_safe, (unsigned long)(now_us() - t1));
    kprintf("\nAlso in the kernel API: xTaskCheckForTimeOut() does this comparison correctly for you.\n");
    bsp_exit(0);
}

int main(void) {
    xTaskCreate(test, "test", 2 * configMINIMAL_STACK_SIZE, NULL, 3, NULL);
    vTaskStartScheduler();
    for (;;) { }
}
