/* R8: see the system.  The R2 task set (C = 1,2,3 ms; T = 4,6,12 ms) plus a timer interrupt every 2 ms that costs 250 us.
 * Three views of the same run:
 *   1. measured worst-case response times      vs   RTA without the interrupt   vs   RTA with the interrupt as a top-priority "task"
 *   2. kernel run-time statistics (CPU share per task)
 *   3. (make TRACE=1) a context-switch trace you can turn into a timeline with tools/trace2gantt.py
 */
#include "FreeRTOS.h"
#include "task.h"
#include "bsp.h"

#ifndef DUMP_TRACE
#define DUMP_TRACE 0
#endif
#define RING 1024
#define ISR_COST_US 250
static uint32_t tick_us[RING];
void vApplicationTickHook(void) { tick_us[xTaskGetTickCount() % RING] = now_us(); }

static volatile uint32_t isr_count;
static void noisy_isr(void) {
    trace_record(EV_ISR, 1, 0);
    isr_count++;
    burn_us(ISR_COST_US);                           /* the cost of the interrupt handler's own work */
}

typedef struct { const char *name; uint32_t C_us, T_ms; UBaseType_t prio; uint32_t jobs, misses, maxR, seen; TickType_t start; } ptask_t;

static void periodic(void *arg) {
    ptask_t *p = arg;
    TickType_t last = p->start, T = pdMS_TO_TICKS(p->T_ms);
    for (;;) {
        uint32_t release = tick_us[last % RING];
        burn_us(p->C_us);
        uint32_t R = now_us() - release;
        if (p->seen++ > 0) { p->jobs++; if (R > p->maxR) p->maxR = R; if (R > p->T_ms * 1000UL) p->misses++; }
        vTaskDelayUntil(&last, T);
    }
}

static void manager(void *arg) {
    ptask_t t[3] = { { .name = "t1", .C_us = 1000, .T_ms = 4, .prio = 4 }, { .name = "t2", .C_us = 2000, .T_ms = 6, .prio = 3 }, { .name = "t3", .C_us = 3000, .T_ms = 12, .prio = 2 } };
    TaskHandle_t h[3];
    kprintf("R8: tasks C/T = 1/4, 2/6, 3/12 ms, plus an interrupt every 2 ms costing %d us\n\n", ISR_COST_US);
    vTaskDelay(1);
    TickType_t start = xTaskGetTickCount();
    for (int i = 0; i < 3; i++) t[i].start = start;
    timer1_start(2000, noisy_isr);
    for (int i = 0; i < 3; i++) { xTaskCreate(periodic, t[i].name, configMINIMAL_STACK_SIZE, &t[i], t[i].prio, &h[i]); vTaskSetTaskNumber(h[i], (UBaseType_t)(i + 1)); }
    trace_reset();
    vTaskDelay(pdMS_TO_TICKS(2400));
    timer1_stop();
    /* stop the periodic tasks, then report */
    for (int i = 0; i < 3; i++) vTaskSuspend(h[i]);

    const uint32_t pred_no_isr[3] = { 1000, 3000, 10000 }, pred_isr[3] = { 1250, 3500, 11500 };
    kprintf("1. response times (us)\n   task   deadline  measured max   RTA without ISR   RTA with ISR   misses\n");
    for (int i = 0; i < 3; i++)
        kprintf("   %-5s %8lu %13lu %17lu %14lu %8lu\n", t[i].name, (unsigned long)t[i].T_ms * 1000, (unsigned long)t[i].maxR,
                (unsigned long)pred_no_isr[i], (unsigned long)pred_isr[i], (unsigned long)t[i].misses);
    kprintf("   interrupts fired: %lu\n\n", (unsigned long)isr_count);

    UBaseType_t n = uxTaskGetNumberOfTasks();
    TaskStatus_t *st = pvPortMalloc(n * sizeof(TaskStatus_t));
    uint32_t total = 0;
    n = uxTaskGetSystemState(st, n, &total);
    kprintf("2. kernel run-time statistics (time spent in each task; interrupt time is charged to the task it interrupted)\n");
    for (UBaseType_t i = 0; i < n; i++)
        kprintf("   %-8s %5lu.%lu%%\n", st[i].pcTaskName, (unsigned long)(st[i].ulRunTimeCounter * 100ULL / total), (unsigned long)((st[i].ulRunTimeCounter * 1000ULL / total) % 10));
    vPortFree(st);
    kprintf("   (expected: t1 25%%, t2 33%%, t3 25%% from C/T alone; the interrupt adds 12.5%%, mostly charged to whoever it interrupted)\n");
    if (DUMP_TRACE) {
        kprintf("N 1 t1\nN 2 t2\nN 3 t3\n");
        trace_dump();
    }
    bsp_exit(0);
}

int main(void) {
    xTaskCreate(manager, "manager", 3 * configMINIMAL_STACK_SIZE, NULL, 6, NULL);
    vTaskStartScheduler();
    for (;;) { }
}
