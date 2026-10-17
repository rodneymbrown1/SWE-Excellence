# FreeRTOS quick map {.appendix data-part="APPENDICES"}

Names and behaviour follow the FreeRTOS kernel book (v10.6.2-era text) and the kernel V11.3.2 used by the labs. Check your port's documentation for anything not listed.

## Which call from where

| Purpose | From a task | From an interrupt | Blocks? |
|---|---|---|---|
| create a task | `xTaskCreate` / `xTaskCreateStatic` | — | no |
| delay | `vTaskDelay(n)` | — | yes |
| periodic delay | `xTaskDelayUntil(&last, n)` (`vTaskDelayUntil`) | — | yes |
| queue send / receive | `xQueueSend`, `xQueueReceive` (with timeout) | `xQueueSendFromISR`, `xQueueReceiveFromISR` | task: yes; ISR: never |
| latest-value mailbox | `xQueueOverwrite` (queue length 1) | `xQueueOverwriteFromISR` | no |
| mutex | `xSemaphoreCreateMutex`, `xSemaphoreTake`, `xSemaphoreGive` | **not allowed** | yes (inheritance) |
| binary semaphore (signal) | `xSemaphoreCreateBinary`, `Take`, `Give` | `xSemaphoreGiveFromISR` | yes; **no inheritance** |
| task notification | `xTaskNotifyGive`, `ulTaskNotifyTake` | `vTaskNotifyGiveFromISR` | take: yes |
| event group | `xEventGroupSetBits`, `WaitBits` | `xEventGroupSetBitsFromISR` (deferred) | wait: yes |
| critical section | `taskENTER_CRITICAL` / `taskEXIT_CRITICAL` | `taskENTER_CRITICAL_FROM_ISR` | no (masks interrupts) |
| suspend scheduler | `vTaskSuspendAll` / `xTaskResumeAll` | — | no |
| software timer | `xTimerCreate`, `xTimerStart` | `…FromISR` | callbacks run in the **timer task** |
| heap | `pvPortMalloc`, `vPortFree`; `xPortGetMinimumEverFreeHeapSize`; `vPortGetHeapStats` | — | — |
| stack margin | `uxTaskGetStackHighWaterMark` | — | — |
| run-time stats | `uxTaskGetSystemState` with `configGENERATE_RUN_TIME_STATS` | — | — |

## Task states

Running · Ready · Blocked (delay or event) · Suspended. The scheduler always picks the highest-priority Ready task; equal priorities rotate each tick if `configUSE_TIME_SLICING` is 1.

## Settings that change behaviour (see `FreeRTOSConfig.h`)

| Setting | Effect |
|---|---|
| `configUSE_PREEMPTION` | 0 = cooperative |
| `configUSE_TIME_SLICING` | 0 = equal priorities run until they block |
| `configTICK_RATE_HZ` | the tick; every delay is a multiple |
| `configTICK_TYPE_WIDTH_IN_BITS` | 16 or 32 (or 64 on some ports); wrap time |
| `configMAX_PRIORITIES` | number of levels; 0 is idle |
| `configKERNEL_INTERRUPT_PRIORITY`, `configMAX_SYSCALL_INTERRUPT_PRIORITY` | which interrupts may call kernel `FromISR` functions |
| `configCHECK_FOR_STACK_OVERFLOW` | 1 or 2 plus `vApplicationStackOverflowHook` |
| `configUSE_MALLOC_FAILED_HOOK` | `vApplicationMallocFailedHook` |
| `configASSERT` | what happens when the kernel detects misuse |
| `configUSE_TIMERS`, `configTIMER_TASK_PRIORITY` | the timer service task and its priority |
| `configSUPPORT_STATIC_ALLOCATION` | allow no-heap objects |
| trace macros (`traceTASK_SWITCHED_IN`, …) | hooks for tracing (lab R3, R8) |

## Gotchas found in this project

| Gotcha | Where |
|---|---|
| `xTaskDelayUntil` with a `last` in the future does not block | ch. 3, lab R3 |
| `xTaskCatchUpTicks` must **not** be called with the scheduler suspended | lab R7 |
| a binary semaphore has **no owner**, so no inheritance | ch. 13, lab R3, R9 |
| stack depth is in **words** | ch. 6, 14 |
| stack overflow is detected at the **next context switch**, after the damage | ch. 14, lab R6 |
| the kernel's "free heap" can be large while the largest block is small | ch. 14, lab R6 |
| `vTaskDelete(NULL)` needs the idle task to run to free memory | ch. 6 |
| run-time-stats clock should be 10–100× faster than the tick (the lab uses 1 MHz ≈ 1000×) | ch. 20, lab R8 |
