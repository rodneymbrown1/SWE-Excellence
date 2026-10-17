/* R6: memory is a budget you must read, not assume.
 *   Part 1  stack high-water marks: how close is each task to its limit?
 *   Part 2  heap fragmentation: "free: 21 KB" but "malloc(8 KB) fails"
 *   Part 3  stack overflow: what the kernel's check (configCHECK_FOR_STACK_OVERFLOW = 2) does and does not do
 */
#include "FreeRTOS.h"
#include "task.h"
#include "bsp.h"

extern volatile int lab_malloc_fatal;
#define NB 40
#define BLK 1000

static void part1(void) {
    kprintf("Part 1: stack high-water marks (words free at the worst point so far; stack depth given at creation)\n");
    UBaseType_t n = uxTaskGetNumberOfTasks();
    TaskStatus_t *st = pvPortMalloc(n * sizeof(TaskStatus_t));
    n = uxTaskGetSystemState(st, n, NULL);
    for (UBaseType_t i = 0; i < n; i++)
        kprintf("  %-10s prio %lu  min-ever-free stack = %4lu words (%lu bytes)\n", st[i].pcTaskName, (unsigned long)st[i].uxCurrentPriority,
                (unsigned long)st[i].usStackHighWaterMark, (unsigned long)st[i].usStackHighWaterMark * 4);
    vPortFree(st);
    kprintf("  (the tasks were created with %d words: any task near zero is one code change from an overflow)\n\n", (int)(2 * configMINIMAL_STACK_SIZE));
}

static void show_heap(const char *when) {
    HeapStats_t h;
    vPortGetHeapStats(&h);
    kprintf("  %-28s free total=%5lu B   largest free block=%5lu B   free blocks=%2lu   min ever free=%5lu B\n", when,
            (unsigned long)h.xAvailableHeapSpaceInBytes, (unsigned long)h.xSizeOfLargestFreeBlockInBytes,
            (unsigned long)h.xNumberOfFreeBlocks, (unsigned long)h.xMinimumEverFreeBytesRemaining);
}

static void part2(void) {
    kprintf("Part 2: heap_4 fragmentation (heap = %lu bytes; %d blocks of %d bytes)\n", (unsigned long)configTOTAL_HEAP_SIZE, NB, BLK);
    void *b[NB]; int got = 0;
    for (int i = 0; i < NB; i++) { b[i] = pvPortMalloc(BLK); if (b[i]) got++; }
    kprintf("  allocated %d blocks\n", got);
    show_heap("after allocating");
    for (int i = 0; i < NB; i += 2) { vPortFree(b[i]); b[i] = NULL; }          /* free every second block */
    show_heap("after freeing every other");
    lab_malloc_fatal = 0;                          /* this lab WANTS to see the failure and keep running */
    void *big = pvPortMalloc(8 * 1000);
    kprintf("  pvPortMalloc(8000) -> %s   (total free is large, but no single hole is)\n", big ? "OK" : "NULL (FAILED)");
    for (int i = 1; i < NB; i += 2) { vPortFree(b[i]); b[i] = NULL; }          /* free the rest: neighbours coalesce */
    show_heap("after freeing the rest");
    big = pvPortMalloc(8 * 1000);
    kprintf("  pvPortMalloc(8000) -> %s\n", big ? "OK (blocks coalesced)" : "NULL");
    vPortFree(big);
    kprintf("\n");
}

extern volatile int lab_overflow_fatal;
extern volatile uint32_t lab_overflow_reports;
static volatile uint32_t sink;
static uint32_t eat_stack(uint32_t depth) {
    volatile uint32_t pad[32];                    /* 128 bytes of stack per level */
    for (int i = 0; i < 32; i++) pad[i] = depth + (uint32_t)i;
    if (depth == 0) return pad[0];
    return eat_stack(depth - 1) + pad[depth % 32];   /* recursion: the pattern the Power-of-10 rules forbid */
}

static volatile uint32_t victim_done;
static void victim(void *arg) {
    kprintf("  victim: stack is 128 words (512 bytes); recursing 8 levels (~1.2 KB) ...\n");
    sink = eat_stack(8);
    kprintf("  victim: returned from the recursion. The stack is already overrun, and NOTHING has noticed.\n");
    victim_done = 1;
    vTaskDelay(1);                                /* the first context switch after the overflow: now the kernel looks */
    for (;;) vTaskDelay(10);
}

static void manager(void *arg) {
    part1();
    part2();
    kprintf("Part 3: stack overflow (configCHECK_FOR_STACK_OVERFLOW = %d)\n", (int)configCHECK_FOR_STACK_OVERFLOW);
    lab_overflow_fatal = 0;
    uint8_t *canary = pvPortMalloc(2048);          /* allocated first => sits just BELOW the next allocation (the victim's stack) */
    for (int i = 0; i < 2048; i++) canary[i] = 0xA5;
    xTaskCreate(victim, "victim", 128, NULL, 6, NULL);
    vTaskDelay(pdMS_TO_TICKS(100));
    int bad = 0;
    for (int i = 0; i < 2048; i++) if (canary[i] != 0xA5) bad++;
    kprintf("  overflow hook calls: %lu.  Bytes of the neighbouring heap block that were silently overwritten: %d of 2048\n", (unsigned long)lab_overflow_reports, bad);
    kprintf("  The check only runs at a context switch, so it reports AFTER the damage; method 2 also only inspects the last 20 bytes of the stack.\n");
    bsp_exit(0);
}

int main(void) {
    xTaskCreate(manager, "manager", 2 * configMINIMAL_STACK_SIZE, NULL, 5, NULL);
    vTaskStartScheduler();
    for (;;) { }
}
