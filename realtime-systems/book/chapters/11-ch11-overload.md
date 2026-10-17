# Overload: when the work does not fit {.chapter data-part="PART 2 · ORDER"}

<p class="lede">Every analysis in the last four chapters assumed the budgets hold. Sooner or later one does not: a slow path, a burst, a fault. What your system does then is a design decision, and the best time to make it is before it happens.</p>

## Two kinds of overload

| Kind | Cause | Example | Shape |
|---|---|---|---|
| **Transient** | a job runs longer than budget, or events arrive in a burst | a recalibration step, a retry storm | passes; the system must recover its schedule |
| **Permanent** | demand exceeds capacity for as long as the condition lasts | a new feature, a faster sensor, a misconfigured peripheral | unfinished work accumulates until something gives |

## What fixed priority does

Under fixed priority an overrun in task *i* cannot make any **higher**-priority task late; it can make any **lower** one late. In permanent overload the lowest-priority tasks starve completely. [RAN]{.ran} Lab H3 demo 3b, three tasks with U = 1.25, 120 ticks: tasks a, b, c (priority order) completed **15, 10 and 0** jobs. Task c never ran.

Buttazzo's counterexample shows the "which task fails first?" question has a less obvious answer than "the longest period". [RAN]{.ran} Tasks C = (2, 3, 1, 1) ms, T = (5, 9, 20, 30) ms are schedulable (U = 0.817); give τ1's first two jobs 1.5 ms extra and **τ2**, not τ4, misses its deadline.

{{fig:gantt-overload | Transient overload under rate-monotonic scheduling. The overrun in t1 delays t2 past its deadline (X); t3 and t4 are pushed but still make theirs. Time unit 0.5 ms.}}

## What EDF does

In permanent overload EDF does not starve a task; every task's effective period stretches by the same factor U. [RAN]{.ran} H3 demo 3b: EDF completed **12, 8 and 4** jobs. A system whose tasks all run slower is sometimes better than one where one task never runs, and sometimes much worse; it depends on what the tasks are. A control loop that runs at half rate may be unstable; a log task at half rate is fine.

## Case file: the Apollo executive

::: case
**Apollo 11, 1969: overload by accumulation.** (All numbers from Eyles 2004.) The guidance software read the accelerometers every 2 seconds in a task called `READACCS`, which scheduled a large job, `SERVICER`, at the **lowest** priority of the descent jobs. Resources were fixed: **eight "core sets"** (register save areas) and **five vector-accumulator areas**; at most eight jobs could be queued. In normal operation the number of jobs started equalled the number finished. Then a radar interface problem consumed **about 13%** of the computer's time. The duty-cycle margin had been "over 15%" before the landing radar locked, about 13% after, and "10% or less" once a monitor display was added. With a 10% margin and a 13% drain, the computer "simply did not have enough CPU time".

What failed: `SERVICER`, last in line, "had not yet reached its conclusion when the next READACCS, running punctually, scheduled SERVICER again." The unfinished job had not released its core set, so each new request took another. "After a short span of such operation the Executive exhausted its supply of core sets and/or VAC areas", and called `BAILOUT` with alarm **1202** (no core sets) or **1201** (no VAC areas).

What did not fail: the system. A software restart kept only the most recent copy of each restart-protected job, "flushed the uncompleted SERVICER 'stubs' that had accumulated", and terminated functions "that had not been restart protected because they were not deemed critical" (the monitor display). "Here a system of restart protection that was primarily motivated by the possibility of hardware glitches synergistically provided a means to shed computational load in response to a software logjam." In a later phase, with less than 10% margin even without the radar, "the software restart flushed the Executive queue but could not shed load" and the alarms kept coming.
:::

{{fig:apollo-pool | A toy model, not Apollo data: a fixed pool of 8 job slots and a job that does not fit its period. A small steady deficit does not fail at once: it fills the pool, then the system restarts, recovers and fails again. Lab H4.}}

[RAN]{.ran} Lab H4 `apollo` toy model (period 2 s, job needs 1 s, pool 8): with the high-priority load at 0.40 the job fits and there are no alarms; at 0.52 (a small deficit) the pool fills once in 800 s; at 0.62 it fills and restarts **11 times**. The spacing of alarms is set by (pool size) ÷ (deficit per period).

## Design choices when the budget is exceeded

| Policy | What it does | Good for | Risk |
|---|---|---|---|
| **Continue late** | let the late job finish | work that is still useful | the next release arrives; backlog grows |
| **Skip** the next release(s) | drop work while behind | periodic estimates and logs | consumers see a gap; count it |
| **Abort** the job at its deadline | kill it | work that is worthless late | must leave state consistent; locks released |
| **Degrade** (shorter algorithm, lower rate) | switch to a cheaper mode | control with graceful loss of quality | the mode switch itself must be safe |
| **Shed** lower-criticality work | stop non-essential tasks | overload from many sources | needs a criticality ranking and a restart path |
| **Restart / reset** | return to a known state | when the state is suspect | loses work; restart loops (ch. 19) |

Enforcement needs detection. Two real examples:

- **F´ rate groups** report "a warning event when a rate group cycle is started before previous is completed" (requirement ARG-004).
- **Pathfinder's `bc_sched`** checked each cycle that `bc_dist` had finished ("a hard deadline in the system") and, when not, "declared the error that initiated the reset": a deadline monitor with a defined, tested reaction.

::: rule
**Rule.** Every periodic component needs three written answers: *how do I detect that a job overran, what do I do with the job, and what do I do about the next release?* If the framework gives a default, read it.
:::

## Count releases, not completions

A log that records only the response times of jobs that ran has *survivorship bias*: skipped releases never appear. [RAN]{.ran} Lab H5 shows the numerical consequence for latency percentiles (chapter 20). In an RTOS, keep **three counters per periodic task**: releases, completions, deadline misses. Their differences tell the truth.

## Check yourself

::: check
1. Your 10 ms task takes 14 ms once an hour. List what happens to the next release under each of: continue late, skip, abort. Which does your framework do by default?
2. In fixed-priority overload which of your components starve first? Is that the order you want?
3. What is the equivalent of Apollo's "restart protection" in your system: what survives a restart, and what is allowed to be lost?
:::

**Lab links.** H3 (overload demos), H4 (`apollo` model), H5 (counting).
