# Many jobs, one CPU: the cyclic executive {.chapter data-part="PART 1 · TIME"}

<p class="lede">Before preemptive schedulers, engineers shared one CPU by cutting time into fixed slots and deciding, on paper, what runs in each. The design is still alive inside modern frameworks, and it teaches the vocabulary of rates, frames and hyperperiods that every later chapter uses.</p>

## Frames and cycles

A **cyclic executive** (also *timeline scheduling*, *table-driven*) works like this. Time is divided into equal **minor cycles** (frames). A hardware timer starts each frame. In each frame the executive calls a fixed list of functions in a fixed order. The whole pattern repeats every **major cycle**, which equals the **hyperperiod**: the least common multiple of all the periods.

Buttazzo's description: "the time line is divided into slots of fixed length (minor cycle) and tasks are statically allocated in each slot based on their rates and execution requirements. The schedule is then constructed up to the least common multiple of all the periods (called the hyperperiod or the major cycle) and stored in a table."

{{fig:cyclic-executive | A 40 ms major cycle of four 10 ms frames (top). One 6 ms overrun makes the next frame start late (bottom). Lab H2 prints this table.}}

```c
for (;;) {
    wait_for_frame_timer();            /* hardware timer: every 10 ms */
    task_A();                          /* every frame */
    if (frame % 2 == 0) task_B();      /* every 20 ms */
    if (frame % 4 == 0) task_C();      /* every 40 ms */
    frame++;
}
```

## Design arithmetic

| Step | Rule | Example (rates 100, 50, 25 Hz) |
|---|---|---|
| Hyperperiod | LCM of the periods | LCM(10, 20, 40) = 40 ms |
| Frame | divides the hyperperiod; every period is a whole number of frames; at least as long as the longest job (if jobs are not split) | 10 ms |
| Slack per frame | frame − Σ budgets of the jobs in it | frame 0: 10 − (2+3+4) = 1 ms |
| Table size | hyperperiod / frame frames | 4 frames |

Non-harmonic rates inflate the hyperperiod: periods of 10, 20, 40 and 50 ms give 200 ms; 7, 11 and 13 ms give 1,001 ms. A long hyperperiod means a long table and a long time before a rare alignment is seen in testing. **Choose harmonic rates when you can** (chapter 17).

## Why it was popular, and what it costs

Buttazzo summarises both sides.

| For | Against |
|---|---|
| "straightforward to implement and does not introduce significant runtime overhead (since scheduling decisions are taken off-line)" | "fragile during overload situations, since a task exceeding its predicted execution time could generate (if not aborted) a domino effect on the subsequent tasks, causing their execution to exceed the minor cycle boundary" |
| "tasks always execute in their preallocated slots, so the experienced jitter is very small" | "a creation of a new task, or a little change in a task rate, might modify the values of the minor and major cycles, thus requiring a complete redesign of the scheduling table" |

The Apollo software authors had the same view in 1960s words: a "boxcar" executive "is painful to implement because computations must be broken up arbitrarily", and "it breaks down completely as soon as any function takes longer than the time it is allocated." Locke's 1992 comparison of one hard real-time application built both ways concluded that, with rate-monotonic priorities, the fixed-priority design "generally dominates" the cyclic executive (abstract-level source).

[RAN]{.ran} Lab H2, 10 ms frames, B overruns by 6 ms in major cycle 2:

| Policy | What happens |
|---|---|
| nominal | 0 of 16 frames start late |
| overrun, no policy | B finishes at 91 ms, C at 95 ms; frames 9 and 11 start late (2 of 16) |
| overrun, **skip what no longer fits** | C is skipped in frame 8; frame 9 still starts 1 ms late |

The choice of policy — continue late, skip, abort — is a **requirement** the table does not contain.

## Its modern descendants

The idea survived because the **rate group** is a natural unit of design: "everything that runs at 10 Hz".

- **F´ (JPL)**: `Svc::ActiveRateGroup` "is an active component that drives a set of components connected to `Svc::Sched` output ports. It contains an asynchronous input `Svc::Cycle` port. This port sends a message which wakes the component task. The task invokes each output port in order … It tracks execution time and detects overruns." Its requirement ARG-004 is a warning event "when a rate group cycle is started before previous is completed". A rate group is a **cyclic executive running on a thread**, with overrun detection added.
- **cFS (NASA)** and other flight frameworks drive applications from a **scheduler table** that sends wake-up messages in numbered slots of a frame. The precise table layout is configuration-specific; the question to ask is the same.
- **AUTOSAR/OSEK** have *schedule tables* and alarms that activate tasks at fixed offsets.

When you meet "rate group", "minor frame", "slot", "cycle" or "tick table" in a framework, translate: *which frame am I in, what else is in it, and what is its slack?*

## When a cyclic executive is the right tool

It is a good choice when the task set is small and fixed, jitter must be minimal, certification wants a statically analysable schedule, and every job's execution time is tightly bounded. It is a poor choice when jobs are long and variable, rates are unrelated, or the system will grow. Its great virtue for a reader of someone else's code: **the table is the documentation**.

::: trap
**Trap: a frame with no slack.** A frame that is 100% budgeted can only be correct if every job takes *exactly* its budget. Budgets are claims; measured values include interrupts and kernel overhead. Chapter 9's lab shows a "schedulable" set missing 80% of deadlines because its jobs finished on the deadline on paper.
:::

## Check yourself

::: check
1. Rates 100 Hz, 40 Hz and 25 Hz: the hyperperiod, a frame length that works, and the number of frames in the table.
2. A job in a 5 ms frame occasionally takes 7 ms. Describe three policies and the consequence of each for the *next* frame.
3. In your framework, find the object that decides what runs at each rate. Does it detect overruns? What does it do then?
:::

**Lab link.** H2 (cyclic executive with overrun and skip policies).
