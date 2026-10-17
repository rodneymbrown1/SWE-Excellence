# Reading an unfamiliar framework {.chapter data-part="PART 6 · PUT IT TOGETHER"}

<p class="lede">You will rarely build the scheduler. You will be dropped into a framework that has already chosen the policy, the queues, the lifecycle and the message model, often automating them away. This chapter is the fast route to finding out what it chose, in the first hour, with a running system and a few files.</p>

## The first hour

{{fig:recon-flow | The first hour in a new RTOS system. Each step has a gate: a question you must be able to answer before moving on.}}

Start the way the debugging book does: **run it first.** Build with debug symbols, run it (on hardware or an emulator), read the log. Then answer, in this order, the questions below. A blank is not a failure: it is the list of things to ask.

## Ten questions to put to any framework

| # | Question | Where to look | Why it matters |
|---|---|---|---|
| 1 | **What is the scheduler policy?** fixed priority, time slicing, EDF, cooperative, table-driven | kernel configuration file; framework docs | chapters 5–10 |
| 2 | **What is the tick, and what are the rates?** tick frequency; every periodic rate | kernel config; schedule/rate-group tables | chapters 3, 17 |
| 3 | **How many threads, at what priorities, with what stacks?** | task list at run time; framework topology/launch files | chapters 6–7, 14 |
| 4 | **Which code runs in interrupts and in timer callbacks?** | vector table; ISR list; timer service config | chapter 4 |
| 5 | **What are the queues: depth, policy, counters?** | queue creation, QoS, pipe depth | chapter 15 |
| 6 | **What is shared, and how is it protected?** mutexes, guarded ports, critical sections | grep locks; port/message definitions | chapters 12–13 |
| 7 | **How is memory managed?** static or heap; which heap scheme; stack margins | heap config; linker map; high-water marks | chapter 14 |
| 8 | **What starts, in what order, and what restarts?** lifecycle manager; start-up table | startup code; lifecycle docs | chapter 18 |
| 9 | **Who supervises whom?** watchdogs; heartbeat; health monitor; reset behaviour | watchdog code; framework health service | chapter 19 |
| 10 | **How can I see it?** trace hooks, run-time stats, logs, counters, debug interface | config flags; framework telemetry | chapter 20 |

## The kernel configuration file is the first document

In FreeRTOS the file is `FreeRTOSConfig.h`. Ten lines tell you more about the system than any diagram. These are from the lab build (`labs/rtos/common/FreeRTOSConfig.h`), with the question each answers:

| Setting | Lab value | Question it answers |
|---|---|---|
| `configUSE_PREEMPTION` | 1 | is it preemptive? (1) |
| `configUSE_TIME_SLICING` | 1 | do equal priorities take turns? (1, 7) |
| `configTICK_RATE_HZ` | 1000 | what is a tick? (2, 3) |
| `configMAX_PRIORITIES` | 8 | how many priority levels? (1, 7) |
| `configTICK_TYPE_WIDTH_IN_BITS` | 32-bit | when does the tick wrap? (3) |
| `configTOTAL_HEAP_SIZE` + heap scheme | 48 KB, `heap_4` | how much memory, which allocator? (7) |
| `configCHECK_FOR_STACK_OVERFLOW` | 2 | what detects overflow, and when? (7, 14) |
| `configUSE_MUTEXES` | 1 | do mutexes (with inheritance) exist? (6, 13) |
| `configASSERT` | defined | what happens on a violated assumption? (9) |
| `configUSE_TRACE_FACILITY`, `configGENERATE_RUN_TIME_STATS` | 1 | can I measure? (10) |
| `configKERNEL_INTERRUPT_PRIORITY`, `configMAX_SYSCALL_INTERRUPT_PRIORITY` | `0xE0`, `0xA0` | which interrupts may call the kernel? (4) |
| `configTIMER_TASK_PRIORITY` | highest | at what priority do timer callbacks run? (7) |

Other kernels have the same file under other names: Zephyr's `prj.conf`/Kconfig, AUTOSAR's OS configuration, a cFS build's `*_platform_cfg.h`. Learn to read configuration as a requirements document the previous team left you.

## How frameworks package the six questions

| | FreeRTOS | Zephyr | F´ | cFS | ROS 2 |
|---|---|---|---|---|---|
| **Timing** | tick, `xTaskDelayUntil`, timers | `k_timer`, kernel clock | rate groups driven by a cycle port | scheduler table slots | timers in the executor |
| **Scheduling** | fixed priority + slicing | fixed priority (+ optional EDF within a level), cooperative threads | thread priority per active component | task priority per app | the executor's order; OS thread priorities |
| **Messaging** | queues, notifications | message queues, FIFOs | typed ports; **async port = queue** | **software bus**, pipes | topics + QoS |
| **Synchronization** | mutex (inheritance), semaphore | mutex, semaphore | **guarded** ports, queued messages | OS mutex calls | callback groups, locks |
| **Reliability** | your design (chapter 19) | your design | health/watchdog components | health & safety app, watchdog | liveliness QoS, lifecycle nodes |
| **Observability** | trace hooks, run-time stats | tracing subsystem | telemetry and events from every component | event and housekeeping messages | `ros2 topic`, tracing tools |

*The cFS row and parts of the Zephyr row were not verified against primary sources in this project; confirm in your own build's documentation.* The F´, ROS 2 and FreeRTOS rows follow the pages cited in `research/05` and `07`.

## Worked reading: an F´ rate group

JPL's F´ documentation lists three component kinds — **passive** ("no queue and no thread"), **queued** ("a queue but no thread") and **active** ("both") — and three port kinds: **synchronous** (an immediate call), **asynchronous** (a message placed in the receiving component's queue and handled on its thread) and **guarded** (a call protected by the component's mutex). A rate-group component (`Svc::ActiveRateGroup`) "invokes each output port in order" when its cycle port fires and "tracks execution time and detects overruns".

Translate with the book:

1. Each **active component** is a task: it has a priority, a stack and a queue depth (chapters 6, 14, 15).
2. A **rate group** is a cyclic-executive frame running on a thread: the order is the table; the sum of its members' budgets is the frame's load (chapter 5).
3. An **async port** is a queue with a drop or block policy; the depth is in the topology (chapter 15).
4. A **guarded port** is a mutex (chapter 13): find who else calls it, at what priority.
5. **Overrun detection** gives you the "miss policy" for free; find out what it *does* (chapter 11).

Ten minutes of reading the topology file yields the thread list, the queue depths, the rates and the lock structure: the same answers as the first-hour table above.

## Evidence over assumption

When documentation and behaviour disagree, believe behaviour. Pathfinder's flight-software lead concluded: "A good lesson when you fly COTS stuff — make sure you know how it works." The executor timing of ROS 2 had to be reverse-engineered before it could be analysed (Casini et al. 2019). Verify the answers to the ten questions by *measuring*, with the tools from chapter 20.

## Check yourself

::: check
1. Open the configuration of a system you work on. Fill in the table of twelve settings. Which did you not know?
2. Pick one component. Draw its threads, queues and locks from the code, then from the running system (tasks and queue depths). Where do they differ?
3. What is the default behaviour of your framework when a rate-group or periodic job overruns?
:::

**Handbook link.** The *Framework Recon Sheet* and *First-Hour Checklist* in the Field Handbook are these tables as forms.
