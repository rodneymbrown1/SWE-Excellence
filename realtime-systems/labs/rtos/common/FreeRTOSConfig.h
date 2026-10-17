/* FreeRTOSConfig.h -- shared by all RTOS labs.  A lab overrides a setting by defining it BEFORE including this
 * file (see each lab's Makefile: -DLAB_xxx) or by editing the #ifndef blocks below.  Every setting that changes
 * timing or safety is commented, because "what is configured" is the first thing to read in an unfamiliar system. */
#ifndef FREERTOS_CONFIG_H
#define FREERTOS_CONFIG_H
#include <stdint.h>
extern void vAssertCalled(const char *file, int line);

/* --- scheduler --------------------------------------------------------------------------------------------- */
#define configUSE_PREEMPTION                      1
#ifndef configUSE_TIME_SLICING
#define configUSE_TIME_SLICING                    1     /* equal-priority ready tasks share the CPU each tick */
#endif
#define configUSE_PORT_OPTIMISED_TASK_SELECTION   0
#define configUSE_TICKLESS_IDLE                   0
#define configCPU_CLOCK_HZ                        ( 25000000UL )
#ifndef configTICK_RATE_HZ
#define configTICK_RATE_HZ                        ( 1000 )
#endif
#define configMAX_PRIORITIES                      ( 8 )
#define configMINIMAL_STACK_SIZE                  ( 128 )    /* words (4 bytes each) */
#define configMAX_TASK_NAME_LEN                   ( 12 )
#ifndef configTICK_TYPE_WIDTH_IN_BITS
#define configTICK_TYPE_WIDTH_IN_BITS             TICK_TYPE_WIDTH_32_BITS
#endif
#define configIDLE_SHOULD_YIELD                   1
#define configUSE_TASK_NOTIFICATIONS              1
#define configTASK_NOTIFICATION_ARRAY_ENTRIES     1

/* --- synchronisation ------------------------------------------------------------------------------------- */
#define configUSE_MUTEXES                         1     /* mutexes have priority INHERITANCE; binary semaphores do not */
#define configUSE_RECURSIVE_MUTEXES               1
#define configUSE_COUNTING_SEMAPHORES             1
#define configQUEUE_REGISTRY_SIZE                 8
#define configUSE_QUEUE_SETS                      0

/* --- memory -------------------------------------------------------------------------------------------- */
#define configSUPPORT_DYNAMIC_ALLOCATION          1
#define configSUPPORT_STATIC_ALLOCATION           0
#ifndef configTOTAL_HEAP_SIZE
#define configTOTAL_HEAP_SIZE                     ( ( size_t ) ( 48 * 1024 ) )
#endif
#define configAPPLICATION_ALLOCATED_HEAP          0

/* --- safety nets ---------------------------------------------------------------------------------------- */
#ifndef configCHECK_FOR_STACK_OVERFLOW
#define configCHECK_FOR_STACK_OVERFLOW            2     /* 0 off, 1 SP check at switch, 2 also checks a fill pattern */
#endif
#define configUSE_MALLOC_FAILED_HOOK              1
#define configASSERT( x )                         do { if( ( x ) == 0 ) vAssertCalled( __FILE__, __LINE__ ); } while( 0 )

/* --- hooks / software timers -------------------------------------------------------------------------- */
#define configUSE_IDLE_HOOK                       0
#ifndef configUSE_TICK_HOOK
#define configUSE_TICK_HOOK                       0
#endif
#define configUSE_TIMERS                          1
#define configTIMER_TASK_PRIORITY                 ( configMAX_PRIORITIES - 1 )
#define configTIMER_QUEUE_LENGTH                  8
#define configTIMER_TASK_STACK_DEPTH              ( configMINIMAL_STACK_SIZE * 2 )

/* --- observability -------------------------------------------------------------------------------------- */
#define configUSE_TRACE_FACILITY                  1     /* adds uxTCBNumber etc. and uxTaskGetSystemState() */
#define configUSE_STATS_FORMATTING_FUNCTIONS      0
#ifndef configGENERATE_RUN_TIME_STATS
#define configGENERATE_RUN_TIME_STATS             0
#endif
#if configGENERATE_RUN_TIME_STATS
extern uint32_t now_us(void);
#define portCONFIGURE_TIMER_FOR_RUN_TIME_STATS()  /* TIMER0 already free-running at 25 MHz */
#define portGET_RUN_TIME_COUNTER_VALUE()          now_us()   /* 1 MHz = 1000x the tick: within the book's "10-100x faster" advice, slightly above */
#endif
#ifdef LAB_TRACE
struct tskTaskControlBlock;
extern struct tskTaskControlBlock * volatile pxCurrentTCB;
extern void trace_switch_in_hook(void);
#define traceTASK_SWITCHED_IN()                   trace_switch_in_hook()
#endif

/* --- interrupt priorities (Cortex-M3, 3 implemented bits are the TOP bits of the byte) -------------------------- */
#define configKERNEL_INTERRUPT_PRIORITY           ( 7 << 5 )   /* 0xE0: SysTick and PendSV: lowest urgency of all */
#define configMAX_SYSCALL_INTERRUPT_PRIORITY      ( 5 << 5 )   /* 0xA0: interrupts at this value or LESS urgent may call FromISR APIs */

/* --- API subset ------------------------------------------------------------------------------------------ */
#define INCLUDE_vTaskPrioritySet                  1
#define INCLUDE_uxTaskPriorityGet                 1
#define INCLUDE_vTaskDelete                       1
#define INCLUDE_vTaskSuspend                      1
#define INCLUDE_xTaskDelayUntil                   1
#define INCLUDE_vTaskDelay                        1
#define INCLUDE_xTaskGetSchedulerState            1
#define INCLUDE_xTaskGetCurrentTaskHandle         1
#define INCLUDE_uxTaskGetStackHighWaterMark       1
#define INCLUDE_xTaskGetIdleTaskHandle            1
#define INCLUDE_eTaskGetState                     1
#define INCLUDE_xTimerPendFunctionCall            1
#define INCLUDE_xTaskGetHandle                    1

/* --- map FreeRTOS port handlers to the vector-table names --------------------------------------------------- */
#define vPortSVCHandler    SVC_Handler
#define xPortPendSVHandler PendSV_Handler
#define xPortSysTickHandler SysTick_Handler
#endif
