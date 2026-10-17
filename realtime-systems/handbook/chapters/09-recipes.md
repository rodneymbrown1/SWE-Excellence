# Measuring recipes {.chapter data-part="PART 6 · REFERENCE"}

<p class="lede">Snippets that were run in the labs ([RAN]{.ran}) or are standard practice ([MANUAL]{.manual}, not executed here). Each answers one question with the least disturbance. Adapt names to your framework.</p>

## Time source

| Need | Recipe |
|---|---|
| Microsecond timestamps | a free-running hardware timer: read it, subtract (unsigned). Know its width and wrap. [RAN]{.ran} `now_us()` in `labs/rtos/common/bsp.c` |
| Cycle counts on Cortex-M | `DWT->CYCCNT` after `CoreDebug->DEMCR |= TRCENA` and `DWT->CTRL |= CYCCNTENA`; 32-bit, wraps in 2³²/f_cpu. [MANUAL]{.manual} (not tested in the emulator) |
| Zero-overhead period/jitter | toggle a GPIO at the start and end of the job; watch on a logic analyser or oscilloscope. [MANUAL]{.manual} |

## Release, completion, miss counters per periodic task [RAN]{.ran}

```c
typedef struct { uint32_t releases, completions, misses, max_us; } stat_t;
static void job(stat_t *s, TickType_t release_tick) {
    s->releases++;
    uint32_t t0 = tick_time_us[release_tick % RING];     /* time of the release tick (tick hook fills it) */
    do_work();
    uint32_t r = now_us() - t0;                           /* response time, incl. waiting for the CPU */
    s->completions++;
    if (r > s->max_us) s->max_us = r;
    if (r > DEADLINE_US) s->misses++;
}
/* a gap between releases and completions = skipped or running late: count both */
```

## Latency histogram (cheap, bounded memory) [RAN]{.ran}

```c
static uint32_t bucket[16];                 /* bucket i counts latencies in [2^i, 2^(i+1)) microseconds */
static void record(uint32_t us) { int i = 0; while (us > 1 && i < 15) { us >>= 1; i++; } bucket[i]++; }
/* dump the buckets after the test; p99.9 is the bucket where the cumulative count reaches 99.9% */
```

For a precise percentile table dump raw samples and use `labs/tools/lathist.py`.

## Context-switch trace [RAN]{.ran}

```c
/* FreeRTOSConfig.h */
#define traceTASK_SWITCHED_IN()  trace_switch_in_hook()
/* hook: record (time, task number) into a ring buffer; dump on error; render with labs/tools/trace2gantt.py */
```

Give tasks numbers (`vTaskSetTaskNumber`) so the trace is readable. Keep the buffer in the product; make the scheduler's own error handler dump it (the Pathfinder lesson).

## Queue visibility [RAN]{.ran}

```c
if (xQueueSendToBackFromISR(q, &m, &woken) != pdTRUE) dropped++;     /* count what you cannot deliver */
uint32_t d = uxQueueMessagesWaitingFromISR(q); if (d > peak) peak = d;
```

## Task check-in watchdog [RAN]{.ran}

```c
/* each task, after a full cycle: */   xEventGroupSetBits(checkins, MY_BIT);
/* supervisor, every N ms (> slowest task period): */
uint32_t bits = xEventGroupClearBits(checkins, ALL_BITS);     /* returns the bits before clearing */
if ((bits & ALL_BITS) == ALL_BITS) wdt_feed();
else saved_missing = ALL_BITS & ~bits;                          /* record WHO, then do not feed */
```

## Snapshot instead of two reads [RAN]{.ran}

```c
att_t snap;
taskENTER_CRITICAL();  snap = att;  taskEXIT_CRITICAL();       /* a few instructions: copy once */
/* use only snap from here on */
```

## Stack and heap margins [RAN]{.ran}

```c
uxTaskGetStackHighWaterMark(handle);           /* words free at the worst point so far */
xPortGetMinimumEverFreeHeapSize();             /* the margin you actually had */
vPortGetHeapStats(&stats);                     /* largest free block, number of free blocks */
```

## CPU share per task [RAN]{.ran}

Set `configGENERATE_RUN_TIME_STATS 1`, provide a counter 10–100× faster than the tick, and read `uxTaskGetSystemState()`. Interrupt time is charged to the task it interrupted.

## gdb recipes (labs/rtos/gdb) [RAN]{.ran}

```
source labs/rtos/gdb/freertos.py                       # fr-tasks, fr-tick, fr-queue
break xTaskDelayUntil if $_caller_is("bus_dist") && H_jobs > 0     # LOGPOINT: log and continue
commands
  silent
  printf "tick %4d: job %d, response %d ms\n", xTickCount, H_jobs-1, H_resp[H_jobs-1]
  continue
end
watch resets if resets == 1                            # hardware watchpoint on a shared variable
break xTaskPriorityInherit                             # stop where the kernel boosts a priority
fr-tasks                                               # who runs, who waits on what, any inherited priority
fr-queue lock                                          # mutex holder? waiters?
```

Run the target paused with `python3 labs/rtos/run.py ELF --gdb` and attach with `arm-none-eabi-gdb ELF -ex "target remote :1234"`. Build at `-O0` so variables are visible. VS Code: `labs/rtos/gdb/launch.json.example` [MANUAL]{.manual}.

::: trap
**Observer effect.** A breakpoint stop moved our emulated clock by about 1 ms. On real hardware halted timers may keep running or stop; watchdogs may be frozen. Use logpoints only on rarely-called code, prefer watchpoints, counters and trace, and read results after the run.
:::
