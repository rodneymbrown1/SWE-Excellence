# A worked system: taking over a pipeline {.chapter data-part="PART 6 · PUT IT TOGETHER"}

<p class="lede">You have inherited a small sample-to-actuator pipeline. It runs. The dashboard says latency is fine. You have been asked whether it meets its four requirements. This chapter does it with the method of the book, using the capstone lab (R10) so every number is a real, reproducible result.</p>

## The system and its contract

| Component | Trigger | Priority | Work | Writes / reads |
|---|---|---|---|---|
| **IMU interrupt** | hardware timer, **997 µs** (the sensor's own clock) | above all tasks | stamp a sample, post to `q_raw` (depth 4) | `q_raw` |
| **filter** | each raw sample | 4 | 400 µs; every 250th sample a 6 ms **recalibration** | publishes `att` (struct) |
| **control** | periodic, 10 ms | 3 | 150 µs | reads `att`, posts to `q_cmd` (depth 1, overwrite) |
| **actuator** | each command | 5 | 200 µs | reads `q_cmd` |
| **logger** | periodic, 50 ms | **6** | 3 ms of formatting | reads counters |

| ID | Requirement |
|---|---|
| R-1 | no IMU sample is lost between the interrupt and the filter |
| R-2 | the attitude estimate is published ≤ 3 ms after its IMU interrupt, for 99.9% of samples |
| R-3 | control reads one consistent attitude estimate per cycle |
| R-4 | every task meets its period |

## Step 1: run it, and read what it says

[RAN]{.ran}

```
samples produced   : 3000
estimates published: 2946
commands applied   : 309
mean latency       : 715 us
control cycles     : 309 (expected ~309)
```

Already one line disagrees with R-1: **54 samples produced and never published.** The mean latency looks excellent. (Chapter 20: means hide tails.)

## Step 2: write the budget and predict

Ask the analysis before touching the device. List every task with a budget, rank by priority, and compute the worst-case response time of the filter (chapter 9):

| Case | Filter response (µs) | Reading |
|---|---|---|
| logger at priority 6 (as shipped) | **3,600** | already above R-2's 3,000 µs, **before** counting the recalibration |
| logger moved to priority 1 | **600** | within R-2 with 5× margin |
| filter's budget includes the 6 ms recalibration | **> 6,000** | no priority arrangement can satisfy R-2 |

Three things have been predicted without running anything: **the logger is the wrong priority**, **the recalibration cannot live inside the filter**, and (from chapter 15) a queue of 4 cannot absorb the backlog a 3 ms stall creates: 3 ms ÷ 0.997 ms ≈ 3 samples arrive while the filter is stopped, plus the recalibration's ~6 more.

## Step 3: see the system

Counters not shown by the dashboard; evidence from a latency dump and a trace.

[RAN]{.ran} Histogram of 2,946 estimates: p50 416 µs, p99 8,320 µs, **p99.9 9,496 µs**; 101 samples above 3 ms. The trace shows the cause of the first stretch:

{{fig:trace-r10 | Baseline trace, 80 ms. The filter runs continuously except for a 3 ms gap where the logger (highest priority) runs; during that gap raw samples queue up. Control and actuator run every 10 ms.}}

A debugger session with a watchpoint or a counter gives the rest. The hidden counters, revealed (`make REVEAL=1`):

| Counter | Baseline | Meaning |
|---|---|---|
| `dropped_raw` | **54** | R-1 violated, silently |
| `torn` | **47** (of 309 cycles) | R-3 violated: control read two different samples |
| `ctrl_late` | **61** | R-4 violated: control cycle > 11 ms |
| `isr_late` | 0 | the interrupt itself is never delayed |

## Step 4: fix one thing at a time, and re-measure

Each fix is a small patch in `labs/rtos/r10_pipeline/solutions/`. After each, the same run.

| Patch | Change | `dropped_raw` | `torn` | `ctrl_late` | p99.9 (µs) |
|---|---|---|---|---|---|
| baseline | — | 54 | 47 | 61 | 9,496 |
| 1 | logger priority 6 → 1 | 22 | 49 | 10 | 6,471 |
| 2 | queue depth 4 → 8, drop counter printed | **0** | 39 | 10 | 6,476 |
| 3 | snapshot under a critical section | 0 | **0** | 10 | 6,477 |
| 4 | move the recalibration to a low-priority task | 0 | 0 | **0** | **631** |

The order teaches as much as the numbers. Patches 1–3 each fix a counted failure but leave R-2 untouched: **p99.9 stays at 6.5 ms because a 6 ms job still sits inside the high-priority filter.** That was never a bug in the code; it is a requirement the *design* cannot meet. Only moving the slow path out (patch 4) changes the tail.

{{fig:latency-hist | Latency of the estimate, baseline versus all four fixes. Every sample is under 1 ms afterwards.}}

## Step 5: fill in the evidence table

| ID | Requirement | Metric | Method | Margin | Result |
|---|---|---|---|---|---|
| R-1 | no sample lost | `dropped_raw` | counter, 3,000 samples | zero | **0** — met |
| R-2 | ≤ 3 ms, p99.9 | p99.9 estimate latency | histogram, 3,000 samples, worst-case load | 4.8× (631 µs vs 3,000) | **met** |
| R-3 | one consistent estimate | `torn` | invariant check (`angle_inv == ~angle`) | zero | **0** — met |
| R-4 | every task meets its period | `ctrl_late` | period monitor | zero | **0** — met |

**What is not claimed.** This is 3,000 samples (3 s) on an emulator with a deterministic clock. It shows the *method* works and the fixes do what they claim; it does not show the property holds over hours, on a real board, with real jitter, or at the worst-case alignment of the recalibration with the logger. A 95%-confidence statement from 3,000 clean samples is "failure rate below roughly 1 in 1,000" (the rule of three, chapter 20). Soak and fault-injection tests extend it.

## What the example demonstrates about the discipline

1. **The implicit requirements were all in the table of chapter 23**: M3 (drops visible), Y2 (snapshot), S1 (priorities follow timing), O1/O2 (percentiles), T2 (the budget included the rare path).
2. **Analysis predicted the main defects before the run**; measurement then quantified them.
3. **Four defects, four kinds of evidence**: a counter, an invariant, a trace, a histogram. No one tool found them all.
4. **Fixing was cheap once found**; finding them without the discipline would have taken weeks of "mean latency looks fine".

::: case
**The same pattern at the other end of the scale.** Pathfinder's team had the trace facility, the deadline monitor and a safe reset. They could reproduce the inversion in under 18 hours and fix it by a configuration flag. They had also *seen* it before landing and not reproduced it, and ranked it below other work. The difference between a lab pipeline and a spacecraft is the cost of being wrong; the method is the same.
:::

## Your turn

::: try
Lab R10: run it, **do not** read `main.c` first. Find the four problems using only: the first-look output, `make DUMP=1` and `tools/lathist.py`, `make TRACE=1` and `tools/trace2gantt.py`, and gdb (`labs/rtos/gdb/freertos.py`). Write your hypotheses before each probe (the debugging book's rule). Only then run `make REVEAL=1`.
:::
