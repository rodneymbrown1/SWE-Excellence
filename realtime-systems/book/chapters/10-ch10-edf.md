# EDF and the other policies {.chapter data-part="PART 2 · ORDER"}

<p class="lede">Fixed priorities are not the only way to decide who runs. The earliest-deadline-first rule is optimal on one CPU and appears in the Linux kernel and in Zephyr. You may never configure it, but you will read documentation, papers and framework code that assume you know what it promises and what it does not.</p>

## The rule

**Earliest Deadline First (EDF):** at every scheduling decision run the ready job whose **absolute deadline** is nearest. Priorities are not stored; they are *computed* from the deadlines of the jobs currently in the system, so a task's priority changes from job to job.

Liu and Layland proved it optimal for their model: "if a set of tasks can be scheduled by some priority assignment, it can also be scheduled by this method. In other words, the least upper bound on the processor utilization factor is uniformly 100 percent." A set with deadlines equal to periods is schedulable under EDF **iff U ≤ 1**.

[RAN]{.ran} Lab H3 demo 2: C = (2, 4) ms, T = (5, 7) ms, U = 0.971. Rate-monotonic misses (t2 finishes at 8 ms, deadline 7); EDF meets every deadline over the hyperperiod.

{{fig:gantt-setb-rm | Fixed priority (rate-monotonic): the second task misses once per 35 ms.}}

{{fig:gantt-setb-edf | EDF on the same set: no miss. The two tasks swap places depending on whose deadline is nearer.}}

## Where EDF exists in real systems

| System | What it provides | Source |
|---|---|---|
| **Linux** | `SCHED_DEADLINE`: "basically an implementation of the Earliest Deadline First (EDF) scheduling algorithm, augmented with a mechanism (called Constant Bandwidth Server, CBS)". Each task declares `runtime`, `deadline` and `period`; the CBS gives "bandwidth isolation" so one task cannot steal another's reserved time | kernel documentation |
| **Zephyr** | optional `CONFIG_SCHED_DEADLINE` (off by default): among threads of **equal static priority**, the nearer deadline wins; `k_thread_deadline_set()` takes a cycle-count delta; the scheduler does **not** enforce that the deadline is met | Kconfig and kernel docs |
| **FreeRTOS** | none: fixed priority (with time slicing among equals) | FreeRTOS kernel book |
| **OSEK / AUTOSAR OS** | fixed priority with priority-ceiling resources | secondary sources |

Read the Zephyr entry twice: EDF there is a **tie-breaker inside a priority level**, not a replacement for priorities. Many "EDF" features in embedded systems are like that.

## The evidence: EDF versus fixed priority

Buttazzo's "Rate Monotonic vs. EDF: Judgment Day" (2005) opens: "many misconceptions still exist about the properties of these two scheduling methods", including that RM "is easier to analyze than EDF, it introduces less runtime overhead, it is more predictable in overload conditions, and causes less jitter". "Since the above statements are either wrong, or not precise …". The paper is an advocate's, but it argues with counterexamples you can run.

| Folk claim | What the paper shows | What we ran |
|---|---|---|
| EDF needs more preemptions and overhead | counting context switches, EDF often preempts *less* than RM (simulation curves, and two-task examples) | — (see the paper's figures) |
| RM is predictable in overload: the long-period tasks fail first | "this property does not hold under RM (neither under EDF)": with C = (2, 3, 1, 1), T = (5, 9, 20, 30) and a 1.5-unit overrun in the first two jobs of τ1, the task that misses is τ2, **not** τ4 | [RAN]{.ran} H3 demo 3a reproduces it (times doubled): t2 misses |
| In permanent overload RM and EDF both degrade gracefully | under RM, "a permanent overload may cause a complete blocking of the lower priority tasks"; under EDF the average period of every task scales by U | [RAN]{.ran} H3 demo 3b, U = 1.25 over 120 ticks: FP completes **15, 10, 0** jobs; EDF completes **12, 8, 4** |
| What RM *does* guarantee | "an overrun in task τi cannot cause tasks with higher priority to miss their deadlines" (under EDF "any other task could miss") | consistent with the H3 runs |

## So which should you use?

Almost always you do not choose; the framework did. Choose with these facts:

| You want… | Prefer |
|---|---|
| the simplest analysis, wide tool support, hardware priority levels | **fixed priority** (rate/deadline-monotonic) |
| to use the last 10–30% of the CPU with unrelated rates | **EDF** or a reservation server (CBS) |
| isolation between components from different teams | **reservation-based** (budgets enforced), e.g. SCHED_DEADLINE |
| minimal jitter, certified static table | **cyclic executive** (ch. 5) or **time-triggered** design |
| overruns that hurt only the culprit | fixed priority (damage flows *down*) or budget enforcement |

::: trap
**Trap: "EDF is optimal, so it cannot miss."** Optimal means *if any algorithm can schedule the set, EDF can*. If U > 1, nothing can. EDF in overload also has no priority order to fall back on: a late job's deadline is in the past, so it keeps outranking everyone unless the system aborts it (Zephyr's own comment on the API: a deadline in the past "still ranks above others").
:::

## Other policies you will see named

| Name | One line |
|---|---|
| **Round robin / time slicing** | equal-priority tasks take turns each tick; fair-ish, not predictable |
| **Cooperative** | switch only when a task blocks or yields |
| **Time-triggered** | everything starts at pre-planned instants (cyclic executive across a network) |
| **Reservation / server (CBS, sporadic server)** | each component gets a budget per period; excess is delayed |
| **Mixed criticality** | different assurance levels share hardware with enforced isolation (named here; not covered) |

## Check yourself

::: check
1. A set has U = 0.93 with unrelated periods. RM analysis says t3 misses. Name two different fixes that do not involve a faster CPU.
2. Your framework offers a "deadline" parameter on tasks. Find out: does the scheduler *use* it (ordering), *monitor* it (detect), or *enforce* it (abort)?
3. Why does the cost of a context switch matter more to a comparison of RM and EDF than the cost of choosing the next task?
:::

**Lab link.** H3 demos 2 and 3 (RM versus EDF; overload).
