# Deadlines and response-time analysis {.chapter data-part="PART 2 · ORDER"}

<p class="lede">Utilization tells you if a set is probably fine. Response-time analysis tells you exactly how long each task can take, in the worst case, and compares it with its deadline. It needs four numbers per task, and it gives a yes or a no.</p>

## The equation

Audsley, Burns, Richardson, Tindell and Wellings (1993) give the analysis for tasks scheduled by fixed priority, preemptively:

**R_i = C_i + B_i + Σ over higher-priority j of ⌈(R_i + J_j) / T_j⌉ · C_j**

| Symbol | Meaning |
|---|---|
| C_i | worst-case execution time (budget) of task *i* |
| B_i | worst-case **blocking** by lower-priority tasks (chapter 13) |
| J_j | release jitter of higher-priority task *j* |
| T_j | period (or minimum inter-arrival) of *j* |
| ⌈x⌉ | round up: the number of releases of *j* that land inside *R_i* |
| R_i | worst-case response time; the task is schedulable if **R_i ≤ D_i** |

You solve it by iteration: start with R = C + B, compute the right-hand side, feed it back, and stop when it stops changing (or exceeds the deadline). The authors note that the method "is not based on the notion of processor utilisation" and gives "sufficient and necessary" tests for the model, and that on an avionics case study its predictions were "in close agreement with the behaviour exhibited during simulation studies."

{{fig:rta-stack | Worst-case response of t3 (C = 3, T = 12) with t1 (1/4) and t2 (2/6) above it: 3 → 6 → 7 → 9 → 10 → 10. t3 only runs in the gaps, at ms 3, 5 and 9.}}

## By hand, in five steps

1. List every task *and every interrupt* with period T and budget C. Interrupts are tasks with the highest priority.
2. Sort by priority (rate-monotonic: shortest period first).
3. For the lowest-priority task, start R = C, compute the sum of interference from every higher-priority task, repeat.
4. Add blocking B (zero if tasks share nothing; chapter 13 explains how to bound it) and jitter if releases are not exact.
5. Compare R with D. Slack = D − R. Record it.

[RAN]{.ran} `python3 labs/host/rtcalc.py a:1:4 b:2:6 c:3:12` prints each R, the slack and a Gantt chart. The simulator in `rtsim.py` agrees with the analysis on every set in the labs (for example t3: R = 10 by both).

## Predict, then measure: the numbers from a real kernel

[RAN]{.ran} Lab R2 runs the set on FreeRTOS on an emulated Cortex-M3 and records every job's response time from the release tick to completion (job 0 excluded: it includes task creation).

| Task | C (µs) | T (ms) | Analysis | Measured max | Overhead |
|---|---|---|---|---|---|
| t1 | 1,000 | 4 | 1,000 | **1,006** | 6 µs |
| t2 | 2,000 | 6 | 3,000 | **3,024** | 24 µs |
| t3 | 3,000 | 12 | 10,000 | **10,087** | 87 µs |

The model predicted the measurement within 1%, and the difference is the kernel's own time (ticks and switches). That is the good news. Here is the lesson in the second set.

| Task | C (µs) | T (ms) | Analysis (R) | Measured max | Jobs missing the deadline |
|---|---|---|---|---|---|
| t1 | 2,000 | 5 | 2,000 | 2,008 | 0 of 489 |
| t2 | 4,000 | 7 | 8,000 (> 7: miss) | 8,284 | **279 of 349 (80%)** |

U = 0.971. The zero-overhead simulator predicts only **1 in 5** t2 jobs misses (R = 8 once per hyperperiod). On the real kernel **4 in 5** missed. Per-job responses show why: the simulator's pattern is R = 7, 6, 7, 6, 8 ms, so three of every five jobs finish at *exactly* the deadline. The target's was 7.08, 8.14, 7.17, 6.20, 8.04 ms: the 7 ms jobs finished 80–170 µs late.

::: rule
**Rule.** A job that finishes at its deadline on paper misses it on target. Add a **margin** for the tick, switches and measurement error to C (or require R ≤ 0.9 D), and treat zero slack as failure.
:::

## The four inputs, and how wrong each can be

| Input | Source | Danger |
|---|---|---|
| **T** | spec, or the sensor's datasheet | actual rate drifts (sensors have their own clocks) or arrives in bursts; use the *minimum* inter-arrival |
| **D** | requirement | often unstated; the default "D = T" may be wrong |
| **C** | analysis or measurement | the observed maximum is a **lower bound** on the true worst case |
| **B** | lock durations of lower-priority tasks | requires knowing every critical section (ch. 13) |

On **C**: Wilhelm et al.'s survey of the worst-case execution time problem is clear that a bound must be "safe, i.e., … never underestimate" and "tight", that "the assumption that only local worst cases have to [be] considered to safely determine upper bounds on global execution times is unsafe", and that one cannot assume you have found "a worst initial execution state, to safely start measurement or analysis." Measurement shows what *did* happen; static analysis tools bound what *can*. On a small core without caches the gap is modest; on a core with caches and speculation it can be large. In this book, a measured maximum is called **observed maximum (high-water mark)**, never WCET, and a budget is **claimed** until someone defends it.

## Release jitter, deadlines and priorities

If a task is released late by up to J (for example because a tick-aligned wake-up follows an interrupt), it can be pushed into a collision with its next release: add J to R. If the deadline D is shorter than T, assign priorities by **deadline** rather than period (deadline-monotonic); the analysis is the same.

## Why have both utilization and RTA?

| | Utilization bound | Response-time analysis |
|---|---|---|
| Cost | one sum | an iteration per task |
| Answer | yes (guaranteed) or "unknown" | yes or no, with the number |
| Handles blocking, jitter, D < T | no | yes |
| Tells you *which* task fails and by how much | no | yes |

::: trap
**Trap: analysing the tasks you wrote.** The set includes every interrupt, the tick, the timer service task, and any task a framework created for you. List them from the *running system* (chapter 22), not from your component's source.
:::

## Check yourself

::: check
1. Tasks in ms (C, T): (1, 5), (2, 8), (3, 20). Compute R for each by hand. Is the third schedulable? What is its slack?
2. Add a 200 µs interrupt every 1 ms. Recompute.
3. A task's measured maximum is 4.1 ms over a day. Its budget in the analysis is 4.0 ms. What is wrong, and what do you do?
:::

**Lab links.** H3 (workbench), R2 (predict then measure), R8 (with interrupts).
