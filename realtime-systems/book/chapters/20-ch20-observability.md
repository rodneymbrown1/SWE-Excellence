# Observability: proving it meets its requirements {.chapter data-part="PART 5 · TRUST"}

<p class="lede">"It works on my bench" is a statement about the average. Requirements are statements about the worst case, or about a high percentile. This chapter is about gathering evidence that speaks to a requirement: what to record, how to report it, and what not to trust.</p>

## From requirement to evidence

| Requirement | Evidence that speaks to it | Evidence that does not |
|---|---|---|
| "responds within 5 ms" | latency histogram over a long run with the worst-case load; p99.9 and max | mean latency |
| "never drops a message" | a drop counter that stays zero over N hours at peak rate | "we haven't seen any" |
| "period 10 ms ± 10%" | histogram of intervals between releases | average period |
| "recovers from a hang" | a test that injects the hang and records the reset and recovery time | a code review of the watchdog |
| "stack never overflows" | high-water marks after the worst-case test; margin stated | a feeling about call depth |

::: rule
**Rule.** Every requirement gets **one number**, a **method** and a **margin**: *"p99.9 estimate latency ≤ 3 ms (measured at the filter output over 3,000 samples under the worst-case load; margin 4×)."* If you cannot write that sentence, you cannot say it passes.
:::

## Means hide tails

[RAN]{.ran} Lab R10, the capstone pipeline, baseline run, 2,946 latency samples (IMU interrupt to published estimate):

| Statistic | Value |
|---|---|
| **mean** | **715 µs** (a dashboard would show this) |
| median | 416 µs |
| p99 | 8,320 µs |
| p99.9 | **9,496 µs** |
| above the 3 ms requirement | 101 samples (3.4%) |

{{fig:latency-hist | Baseline versus the fixed pipeline on a log scale. The baseline's mean is a healthy 715 µs; its tail runs to 10 ms. After four fixes every sample is under 1 ms (p99.9 = 631 µs).}}

An average of 715 µs is compatible with a requirement of 3 ms at p99.9 being violated **three percent of the time**. Report percentiles and the maximum, from a histogram, and state the sample count and the load.

## The measurement trap: coordinated omission

If a tester sends request *n+1* only after the response to request *n*, a stall *suppresses the very samples that would have been slow*. Gil Tene's name for it: "when omission is coordinated with observed events, it can dramatically skew the statistical analysis of the remaining results."

[RAN]{.ran} Lab H5: a service that normally answers in about 1 ms stalls for 5 s in a 60 s test at an intended 100 requests/s.

| Method | p99 | max |
|---|---|---|
| closed loop, as reported | **1.4 ms** | 5,001 ms |
| closed loop, corrected (fill in the missed samples) | 4,411 ms | 5,001 ms |
| open loop, measured from the *intended* send time (ground truth) | **4,483 ms** | 5,001 ms |

{{fig:coordinated-omission | The same system, three reported tails. The closed-loop tester recorded one slow request (of 5,501); the truth is 558 of 6,000 above 100 ms.}}

The RTOS version: if an overrunning task *skips* releases and your log only records the response times of jobs that ran, the missing releases never appear. **Count releases, completions and misses separately** (chapter 11). Do not average percentiles; merge histograms (a published property of percentile data, noted in Tene's talk).

## What to record, from cheapest to richest

| Tool | What it gives | Cost | In the labs |
|---|---|---|---|
| **Counters** (drops, overruns, restarts) | rates and totals | a few bytes, near zero time | R3, R10 |
| **High-water marks** (stack, heap, queue depth) | margins | free from the kernel | R6 |
| **Timestamps at source** (hardware timer) | latency and age | a register read | R2, R10 |
| **Latency histogram** | the tail | a small array | R4, R10 |
| **Run-time statistics** | CPU share per task | needs a fast counter; interrupt time is charged to the task interrupted | R8 |
| **Context-switch trace** | who ran when | a ring buffer and a hook | R3, R8 |
| **GPIO toggle + logic analyser** | period, jitter, latency with ~zero overhead | a pin and an instrument | (described) |
| **Hardware trace (ETM/SWO) or commercial tracers** | everything, with low overhead | tooling | Tracealyzer, SystemView, Perfetto/LTTng named; not run here |

**The Pathfinder trace.** The team's own words: a "trace/log facility … instrumented the pipe services, msgQ services, interrupt handling, select services, and the tExec task. The facility initializes at startup and continues to collect data (in ring buffers) until told to stop", and "we could not have figured this out ever if we did not have the tools to give us the insight." Leave a ring-buffer trace in the product; make the *scheduler's own error handler* dump it.

[RAN]{.ran} The labs' tracer records `(time, event, task id)` at every context switch through one kernel hook (`traceTASK_SWITCHED_IN`) into a 1,024-entry ring. Converted to a timeline, it makes a priority inversion a picture (chapter 13) and an interrupt's interference visible (chapter 4).

## Is the maximum I saw the maximum there is?

No. Wilhelm et al. (2008) separate **measurement-based** methods ("a subset of all possible executions") from **static analysis**, and insist a bound be "safe" (never underestimate) and "tight". A measured maximum is a **lower bound** on the worst case. The more complex the processor (caches, pipelines, speculation), the larger the gap. Practical consequences:

1. Call it the **observed maximum (high-water mark)** and say what it was observed under.
2. Drive tests toward the worst case on purpose: slowest paths, cold caches, all interrupts firing, maximum message size, lowest battery.
3. Add margin to budgets, and **validate in the field** with the same counters and histograms.
4. If an upper bound is a hard requirement, use a static timing analysis tool or a conservative design (no caches, simple code, bounded loops, the "Power of Ten").

If a test shows **zero** failures in *N* independent trials, the failure probability per trial could still be as high as roughly 3/N at 95% confidence (the "rule of three", standard statistics). Ten thousand clean runs do not show a 1-in-a-million property.

## Observing without disturbing

A debugger stops the CPU; the hardware around it may not stop. [RAN]{.ran} In Lab R9 two silent breakpoint stops moved the program's virtual clock ahead by about 1,982 µs (about 1 ms per stop), and in Lab R3 a breakpoint on a function called in the first cycle made the first deadline miss *vanish* (first reset at tick 257 instead of 55). **Rule of thumb: use breakpoints for logic, not for timing.**

For timing questions:

- **Tracepoints / logpoints** that record and continue (gdb `dprintf`, or the lab's conditional `break … if` with `silent … continue`), **only on rarely-called code**;
- **Hardware watchpoints** on the one variable that matters (R9: `watch resets`);
- **Ring-buffer traces** in the program itself; read them afterwards;
- **State inspection after the event**, with a helper that understands the RTOS (`fr-tasks`).

`fr-tasks` is 60 lines of gdb Python that reads the kernel's own lists. It shows what a thread view cannot: which task waits on what, and any inherited priority. The technique transfers to any framework with in-memory task tables.

## A requirement-to-evidence table for your system

| ID | Requirement | Metric | Method | Margin | Result |
|---|---|---|---|---|---|
| R-1 | no sample lost | `dropped_raw` over run | counter | zero | |
| R-2 | estimate ≤ 3 ms | p99.9 latency | histogram, 3,000 samples, worst-case load | 4× | |
| R-3 | consistent snapshot | `torn` over run | invariant check | zero | |
| R-4 | every task meets its period | `ctrl_late` | period monitor | zero | |

Chapter 24 fills this table in for a real defect-ridden pipeline.

## Check yourself

::: check
1. A test reports "average latency 1.2 ms, max 4.8 ms over 1,000 runs". Which three questions do you ask before believing a 5 ms requirement is met?
2. You cannot afford a trace buffer on a tiny target. Name two cheaper pieces of evidence you can keep.
3. Your test harness waits for each reply before sending the next request. What can it not show?
:::

**Lab links.** H5 (coordinated omission), R8 (trace + statistics), R9 (gdb without breakpoints), R10 (histograms).
