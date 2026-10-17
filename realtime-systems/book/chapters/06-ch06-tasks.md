# Tasks and the kernel {.chapter data-part="PART 2 · ORDER"}

<p class="lede">A kernel makes one CPU look like many. It does that with a small trick: keep a separate stack and a few saved registers for each activity, and switch between them fast enough, and at the right moments, that each looks continuous. Knowing the trick tells you what a task costs, what it can never do, and how it differs from an event handler.</p>

## Words that mean nearly the same thing

| Term | What it adds | Where you meet it |
|---|---|---|
| **Process** | its own address space (memory protection) | Linux, ROS 2 nodes in separate processes |
| **Thread** | an execution context sharing a process's memory | Linux, Zephyr (*thread*), POSIX |
| **Task** | the same, in small-RTOS vocabulary; usually no memory protection | FreeRTOS, OSEK/AUTOSAR |
| **Job** | one release of a task: one pass through its work | scheduling theory |
| **Component / app / node** | a unit of design that may own one or more tasks, queues and state | F´ (component), cFS (app), ROS 2 (node) |

This book says *task* for the unit the scheduler sees and *job* for one release of it.

## Anatomy of a task

A task is four things: a **function** that never returns (or deletes itself), a **stack** (its local variables and saved context), a **control block** (state, priority, the saved stack pointer), and the **kernel lists** it moves between.

```c
void vSensorTask(void *arg) {
    TickType_t last = xTaskGetTickCount();
    for (;;) {                                   /* a task body is a loop that BLOCKS somewhere */
        read_and_filter();
        xTaskDelayUntil(&last, pdMS_TO_TICKS(10));
    }
}
xTaskCreate(vSensorTask, "sensor", 256 /* WORDS, not bytes */, NULL, 3 /* priority */, NULL);
```

The stack size is in **words** (4 bytes on Cortex-M). The FreeRTOS book is explicit: "the value specifies the number of words the stack can hold, not the number of bytes." [RAN]{.ran} In Lab R6 the manager task, created with 256 words, had 145 words free at its worst point; the idle task, 118.

{{fig:task-states | The four states. Only Running consumes CPU. A task that never blocks never lets a lower-priority task run.}}

## How one CPU runs many tasks

{{fig:context-switch | The kernel stores the running task's registers on its stack, saves the stack pointer in the task's control block, loads the other task's stack pointer, and returns "into" it.}}

On a Cortex-M the *tick interrupt* (SysTick) counts time and may make a task ready; a low-priority exception (PendSV) then performs the switch after all other interrupts have finished (Memfault's walk-through of the same mechanism is in `research/`). A switch costs tens of microseconds of CPU on a microcontroller. [RAN]{.ran} In Lab R2, a zero-length periodic job measured **4 to 24 µs** per wake-up in steady state, and the *first* job of each task cost about 230 µs more because it includes task creation.

Nothing here is "at the same time". Two tasks printing every 100 ms in Lab R0 look simultaneous: both lines carry the same millisecond. In microseconds they are 39 µs apart (A at 4,331 µs, B at 4,370 µs), because A ran first and then blocked.

## Cooperative, preemptive, and run-to-completion

| Style | Who decides when to switch | Strength | Weakness |
|---|---|---|---|
| **Cooperative** | the task, when it blocks or yields | no preemption races; tiny kernel | one long step delays everyone (Zephyr: a cooperative thread "remains the current thread until it performs an action that makes it unready") |
| **Preemptive** | the kernel, whenever a higher-priority task is ready | short response for urgent work; analysable | any code can be interrupted between any two instructions: shared data needs protection (ch. 12) |
| **Run-to-completion / event-driven** | the handler, by returning | no stacks per activity; deterministic | a handler must never block; control flow becomes a state machine |

The FreeRTOS book calls "fixed priority preemptive scheduling with time slicing" the algorithm "used by most small RTOS applications"; the same kernel can be configured cooperative (`configUSE_PREEMPTION` 0).

**Stackless alternatives.** Dunkels et al. (SenSys 2006) built *protothreads*: blocking-style code that compiles to a state machine, with a memory overhead of "only two bytes per protothread" and, in their evaluation, "the number of lines of code … reduced by one third" with execution overhead "on the order of a few processor cycles". The price: no local variables survive a block. **Active objects** (Samek; a vendor's viewpoint) give each object a private queue and thread, process events to completion, and block in one place only. Lee's critique of threads ("wildly nondeterministic … the job of the programmer becomes one of pruning that nondeterminism") is why many frameworks hide threads behind queues: you will see this in F´ (active components) and ROS 2 (callbacks).

## What a kernel adds to your design

| Kernel object | Use | Cost to remember |
|---|---|---|
| **Task** | an activity with its own wait points | one stack (permanent RAM) + control block |
| **Software timer** | a short callback at an instant | runs in the *timer service task*, at that task's priority |
| **Queue / notification / event group** | hand data or a signal between tasks and interrupts | RAM for items; behaviour when full (ch. 15) |
| **Mutex / semaphore** | protect data / signal | blocking time and inversion (ch. 12–13) |
| **Idle task** | runs when nothing else can; reclaims memory of deleted tasks | if starved, deleted tasks leak |

## Tasks in other frameworks

| Concept | FreeRTOS | Zephyr | F´ | cFS | ROS 2 |
|---|---|---|---|---|---|
| unit the scheduler sees | task | thread | **active** component (queue + thread) | app's task | executor thread running callbacks |
| runs without its own thread | — | workqueue item | **passive** component (called synchronously) | library call | callback inside the executor |
| how it waits | block on kernel object | block / poll | dequeue next message | pend on a software-bus pipe | wait set / executor spin |

Passive, queued and active components are F´'s three kinds ("no queue and no thread", "a queue but no thread", "both"). When you read an unfamiliar system, *count the threads* first: it is the quickest map of where preemption can happen.

::: trap
**Trap: a task that never blocks.** A `for (;;)` that polls without waiting runs forever at its priority; every lower-priority task, and the idle task, starves. In Lab R3's first draft a task initialised its wake time to a *future* tick (chapter 3's trap), never blocked, and starved the whole system at priority 6.
:::

::: trap
**Trap: deleting tasks and the idle task.** A task that deletes itself leaves its stack and control block for the idle task to free. If something at priority 0 (or the idle task itself) is starved, memory leaks. The FreeRTOS book warns: "it is essential that the Idle task is not starved of processing time."
:::

## Check yourself

::: check
1. List the threads in a system you work on. For each, what does it block on?
2. A task has a 128-word stack and calls a function with a 600-byte local array. What happens, and when will you find out? (Chapter 14.)
3. Why can a cooperative scheduler be easier to reason about than a preemptive one, and what is the price?
:::

**Lab links.** R0 (two tasks), R1 (delays), R2 (measured overhead).
