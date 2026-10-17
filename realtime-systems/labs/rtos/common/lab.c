/* lab.c -- hooks every lab needs. */
#include "FreeRTOS.h"
#include "task.h"
#include "bsp.h"

void vAssertCalled(const char *file, int line) {
    kprintf("\n*** configASSERT failed at %s:%d ***\n", file, line);
    bsp_exit(3);
}
volatile int lab_malloc_fatal = 1;          /* labs that WANT to see a failed allocation set this to 0 */
volatile uint32_t lab_malloc_failures;
void vApplicationMallocFailedHook(void) {
    lab_malloc_failures++;
    if (!lab_malloc_fatal) return;
    kprintf("\n*** pvPortMalloc failed: heap exhausted (min ever free = %lu bytes) ***\n", (unsigned long)xPortGetMinimumEverFreeHeapSize());
    bsp_exit(4);
}
volatile int lab_overflow_fatal = 1;        /* labs that WANT to survive the report set this to 0 */
volatile uint32_t lab_overflow_reports;
void vApplicationStackOverflowHook(TaskHandle_t t, char *name) {
    (void)t;
    lab_overflow_reports++;
    if (lab_overflow_reports <= 2) kprintf("  >>> stack overflow hook: task '%s' (reported at context switch, tick %lu)\n", name, (unsigned long)xTaskGetTickCount());
    if (lab_overflow_fatal) bsp_exit(5);
}

#ifdef LAB_TRACE
void trace_switch_in_hook(void) {
    TaskHandle_t h = xTaskGetCurrentTaskHandle();
    trace_record(EV_SWITCH_IN, h ? (uint8_t)uxTaskGetTaskNumber(h) : 0, 0);
}
#endif

/* Milliseconds since the scheduler started, from the tick count (for human-readable logs). */
uint32_t lab_ms(void) { return (uint32_t)(xTaskGetTickCount() * 1000UL / configTICK_RATE_HZ); }
