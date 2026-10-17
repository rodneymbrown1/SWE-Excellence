# Priorities and preemption {.chapter data-part="PART 2 · ORDER"}

<p class="lede">With a fixed-priority preemptive scheduler the rule is one line: always run the highest-priority ready task. Every interesting behaviour — starvation, inversion, jitter, missed deadlines — is a consequence of that line plus the edge cases around it.</p>

## The rule and a picture

At any instant the CPU runs the **highest-priority Ready task**. If a higher-priority task becomes ready, it preempts the running task *immediately*, not at the next tick: the FreeRTOS book is explicit that "task preemption can occur at any time, not just in the RTOS tick interrupt." Tasks of **equal** priority share the CPU in turn (round robin, one tick per slice); the book adds that this "does not guarantee time is shared equally between tasks of equal priority, only that Ready state tasks of equal priority enter the Running state in turn."

{{fig:gantt-rm-seta | Three periodic tasks scheduled rate-monotonically: t1 (1 ms every 4), t2 (2 ms every 6), t3 (3 ms every 12). Dark = running; dotted = ready but not running. t3 is preempted five times and still finishes at 10 ms.}}

Read the figure the way you will read a trace: for each row, find the *release* (arrow), the *start* (first dark), the *finish*, and the *dotted* region between. The dotted time of a task is the interference it suffers; response time is release to finish.

## Choosing priorities

| Assign by | Rule | When to use |
|---|---|---|
| **Rate** (rate-monotonic) | shorter period → higher priority | periodic tasks with deadline = period; provably optimal among fixed-priority assignments for that model (Liu & Layland) |
| **Deadline** (deadline-monotonic) | shorter relative deadline → higher priority | deadline shorter than period |
| **Importance** | most critical → highest | when deadlines are loose and overload handling matters (ch. 11) |

The common mistake is to rank by *importance*: "the safety task is highest". Priority is a **scheduling** tool. A rarely-run, critical, slow task at the top can make a fast, periodic task miss its deadline while the critical task hardly ever runs. Rank by timing first; handle criticality with budgets, isolation and monitoring.

::: case
**Mars Pathfinder's priority list (1997).** From the flight-software lead's own account: `bc_sched` (sets up each 1553 bus cycle) was "the highest priority task in the system (except for the vxWorks `tExec` task)"; the entry-and-landing task second; `bc_dist` (collects the bus results) third; "all of the tasks which perform other spacecraft functions are lower. Science functions, such as imaging, image compression, and the ASI/MET task are still lower." The bus cycle ran at 8 Hz (0.125 s). The design ranks tasks by how soon a miss is fatal. It was sound until a lock in a library call let the lowest-priority task block the third-highest (chapter 13).
:::

## The edge cases

| Situation | What happens | Consequence |
|---|---|---|
| A task never blocks | all lower priorities starve, including idle | the system "works" with part of it dead |
| Two tasks share a priority | time-sliced each tick | response depends on the other task's length; their *sum* must fit |
| Equal priority, time slicing off | one runs until it blocks | cooperative behaviour inside one level |
| A task changes priorities at run time | order changes at once | analysis must cover every value it takes |
| A lock holder is boosted (inheritance) | its priority is temporarily higher | its priority is no longer its configured one (ch. 13) |
| The software-timer task runs callbacks | at the timer task's priority, which is often the **highest** | a long timer callback preempts everything; keep callbacks tiny |
| An interrupt fires | above every task | interference with all of them (ch. 4) |
| Idle shares priority 0 with application tasks | they time-slice with idle | idle's own work (hooks) steals time |
| Tick granularity | wake-ups happen on tick boundaries | a 1 ms tick gives ±1 ms of release jitter |

[RAN]{.ran} Lab R8 and R3 show these on a real kernel: a trace of each context switch becomes a timeline you can read (below).

{{fig:trace-r8 | A trace of three periodic tasks and a 2 ms interrupt (teal ticks) on the emulated Cortex-M3, 36 ms. Same rule, real kernel: t1 runs first every 4 ms; t3 gets only the gaps.}}

## Preemption is not free and not harmless

- **Cost.** Each switch is tens of microseconds of CPU, plus cache and pipeline effects on bigger cores.
- **Hazard.** Preemption can happen between any two instructions of lower-priority code. Anything two tasks (or a task and an interrupt) both touch is exposed (chapter 12).
- **Benefit.** The highest-priority work has a short, analysable response time, independent of what lower-priority work is doing — *provided it does not need anything a lower-priority task holds*.

::: rule
**Rule.** Priorities encode timing relationships. Change one only after re-running the analysis (chapter 9) or at least the lab trace. A priority that "feels right" is a guess.
:::

## Check yourself

::: check
1. A framework gives you 8 priority levels, with 0 for idle and 7 for the timer task. Four of your components run at 100, 50, 20 and 10 Hz. Assign priorities and defend each.
2. Two equal-priority tasks each need 6 ms of work every 10 ms. Is that a problem? What if one of them is a hard-deadline task?
3. Which of your components run code in a timer callback? At what priority?
:::

**Lab links.** R2, R3, R8 (traces and measurements); H3 (workbench).
