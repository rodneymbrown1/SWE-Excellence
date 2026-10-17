/* R2: predict, then measure.  Periodic tasks with rate-monotonic priorities (shorter period = higher priority).
 *
 * Phase 1 (set A): C = 1,2,3 ms   T = 4,6,12 ms   U = 0.833  (above the Liu-Layland bound 0.780 for n=3)
 * Phase 2 (set B): C = 2,4 ms     T = 5,7 ms      U = 0.971  (RTA says the second task can miss)
 *
 * For every job we record its response time = completion time - release time, where the release time is the
 * hardware-timer reading taken inside the tick interrupt of the tick the job was released on.
 * Prediction (rtcalc.py / RTA):  set A: R = 1, 3, 10 ms   set B: R = 2, 8 ms (8 > deadline 7: MISS).
 */
#include "FreeRTOS.h"
#include "task.h"
#include "bsp.h"

#define RING 1024
static uint32_t tick_us[RING];                      /* time of each tick, from the hardware timer */
void vApplicationTickHook(void) { tick_us[xTaskGetTickCount() % RING] = now_us(); }

typedef struct { const char *name; uint32_t C_us; uint32_t T_ms; UBaseType_t prio;
                 uint32_t jobs, misses, maxR, sumR; TaskHandle_t h; TickType_t start; uint32_t seen; } ptask_t;

static void periodic(void *arg) {
    ptask_t *p = arg;
    TickType_t last = p->start;                      /* every task is released on the SAME tick: the critical instant */
    TickType_t T = pdMS_TO_TICKS(p->T_ms);
    for (;;) {
        /* 'last' is the tick this job was released on */
        uint32_t release = tick_us[last % RING];
        burn_us(p->C_us);
        uint32_t R = now_us() - release;
        if (p->seen++ > 0) {                         /* skip job 0: it also pays for task creation (a start-up transient) */
            p->jobs++; p->sumR += R; if (R > p->maxR) p->maxR = R;
            if (R > p->T_ms * 1000UL) p->misses++;   /* deadline = period */
        }
        vTaskDelayUntil(&last, T);
    }
}

static void run_set(const char *title, ptask_t *ts, int n, uint32_t ms) {
    kprintf("%s\n", title);
    for (int i = 0; i < n; i++) { ts[i].jobs = ts[i].misses = ts[i].maxR = ts[i].sumR = ts[i].seen = 0; }
    vTaskDelay(1);                                   /* start on a tick boundary so all tasks are released together */
    TickType_t start = xTaskGetTickCount();
    for (int i = 0; i < n; i++) ts[i].start = start;
    for (int i = 0; i < n; i++) xTaskCreate(periodic, ts[i].name, configMINIMAL_STACK_SIZE, &ts[i], ts[i].prio, &ts[i].h);
    vTaskDelay(pdMS_TO_TICKS(ms));
    for (int i = 0; i < n; i++) vTaskDelete(ts[i].h);
    kprintf("  task   C(us)  T(ms)  jobs  max R(us)  mean R(us)  misses\n");
    for (int i = 0; i < n; i++)
        kprintf("  %-5s %6lu %6lu %5lu %10lu %11lu %7lu\n", ts[i].name, (unsigned long)ts[i].C_us, (unsigned long)ts[i].T_ms,
                (unsigned long)ts[i].jobs, (unsigned long)ts[i].maxR, (unsigned long)(ts[i].jobs ? ts[i].sumR / ts[i].jobs : 0), (unsigned long)ts[i].misses);
    kprintf("\n");
}

static void manager(void *arg) {
    (void)arg;
    ptask_t a[3] = { { .name = "t1", .C_us = 1000, .T_ms = 4, .prio = 4 }, { .name = "t2", .C_us = 2000, .T_ms = 6, .prio = 3 }, { .name = "t3", .C_us = 3000, .T_ms = 12, .prio = 2 } };
    ptask_t b[2] = { { .name = "t1", .C_us = 2000, .T_ms = 5, .prio = 4 }, { .name = "t2", .C_us = 4000, .T_ms = 7, .prio = 3 } };
    run_set("Set A: predicted max R = 1000, 3000, 10000 us (no misses)", a, 3, 2400);
    run_set("Set B: predicted max R = 2000, 8000 us; t2 deadline is 7000 us -> MISS", b, 2, 2450);
    bsp_exit(0);
}

int main(void) {
    xTaskCreate(manager, "manager", 2 * configMINIMAL_STACK_SIZE, NULL, 6, NULL);
    vTaskStartScheduler();
    for (;;) { }
}
