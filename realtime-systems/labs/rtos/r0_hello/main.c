/* R0: the smallest RTOS program that shows scheduling.
 *   Two tasks of equal priority print and then sleep for a fixed time.  A third, higher-priority task ends the run.
 * Read the output with the tick count in mind: nothing here runs "at the same time" -- the CPU is shared. */
#include "FreeRTOS.h"
#include "task.h"
#include "bsp.h"

extern uint32_t lab_ms(void);

static void worker(void *arg) {
    const char *name = arg;
    for (int i = 0; i < 5; i++) {
        kprintf("[%4lu ms] us=%lu %s: iteration %d\n", (unsigned long)lab_ms(), (unsigned long)now_us(), name, i);
        vTaskDelay(pdMS_TO_TICKS(100));                 /* block for 100 ms: the other task (or idle) runs meanwhile */
    }
    vTaskDelete(NULL);
}

static void reaper(void *arg) {
    vTaskDelay(pdMS_TO_TICKS(700));
    kprintf("[%4lu ms] done. free heap=%lu bytes\n", (unsigned long)lab_ms(), (unsigned long)xPortGetFreeHeapSize());
    bsp_exit(0);
}

int main(void) {
    kprintf("R0: FreeRTOS on QEMU mps2-an385, tick = %d Hz\n", (int)configTICK_RATE_HZ);
    xTaskCreate(worker, "A", configMINIMAL_STACK_SIZE, "task A", 2, NULL);
    xTaskCreate(worker, "B", configMINIMAL_STACK_SIZE, "task B", 2, NULL);
    xTaskCreate(reaper, "reaper", configMINIMAL_STACK_SIZE, NULL, 3, NULL);
    vTaskStartScheduler();
    for (;;) { }
}
