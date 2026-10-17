# Utilization and the rate-monotonic bound {.chapter data-part="PART 2 · ORDER"}

<p class="lede">Utilization is the fraction of the CPU a component needs. It is the cheapest schedulability check there is, and Liu and Layland's 1973 result tells you exactly how much it can prove — and how much it cannot.</p>

## Utilization

For a periodic task with execution budget C and period T, **utilization** is U = C / T. For a set, **U = Σ C_i / T_i**. Always include interrupts (their rate and handler time) and, if you can estimate it, kernel overhead.

| If… | Then… |
|---|---|
| U > 1 | **no** scheduler can meet every deadline: the CPU is overloaded (ch. 11) |
| U ≤ 1 | EDF can schedule it (ch. 10) if deadlines equal periods; fixed priority *might* |
| U ≤ the bound below | fixed priority with rate-monotonic priorities **will** schedule it |

## The Liu–Layland bound

For *n* periodic tasks, independent, with deadlines equal to periods and constant run-times, rate-monotonic priorities meet every deadline whenever

**U ≤ n(2^(1/n) − 1)**

{{fig:util-bounds | The guarantee falls with the number of tasks and settles at ln 2 ≈ 0.693. Above the curve is not "failing": it is "unknown — run exact analysis".}}

| n | 1 | 2 | 3 | 4 | 5 | 10 | ∞ |
|---|---|---|---|---|---|---|---|
| bound | 1.000 | 0.828 | 0.780 | 0.757 | 0.743 | 0.718 | 0.693 |

Three facts to hold at once:

1. **It is sufficient, not necessary.** Above the bound a set may still be schedulable; you need the exact test (chapter 9). [RAN]{.ran} Lab H3: C = (1, 2, 3) ms, T = (4, 6, 12) ms has U = 0.833, above 0.780 — and is schedulable (t3 finishes at 10 ms of its 12).
2. **The average case is better.** Lehoczky, Sha and Ding (1989) report that for randomly generated sets with uniformly distributed parameters the *average breakdown utilization* is about 88% (abstract-level source; a later analysis argues the large-set threshold is nearer 0.80, so treat 88% as an observation about a particular random distribution, not a rule).
3. **Harmonic periods reach 1.0.** If every period divides the next longer one (100, 50, 25 Hz), RM can schedule up to U = 1. This is one reason designers pick rates that are multiples of each other (chapter 17).

## A utilization check as a first review

```
python3 labs/host/rtcalc.py sense:1:10 filter:3:20 control:4:40 log:10:100
tasks: 4   utilization U = 0.450   hyperperiod = 200
Liu-Layland bound for n=4: 0.757   -> U <= bound: schedulable under RM (sufficient test)
```

[RAN]{.ran} The calculator in the labs prints this line, a hyperbolic-bound check (a tighter sufficient test, Bini et al.; not read here), whether the periods are harmonic, and then runs the exact analysis of chapter 9.

::: case
**Toyota's electronic throttle control, as testified (2013).** In litigation over unintended acceleration, a software expert for the plaintiffs, Professor Phil Koopman, presented slides on the throttle controller. Among the claims he reported from NASA's review and trial testimony: the operating system had "multiple priority levels; each with round-robin tasking"; the main CPU had "less than 20% idle time at 5000 RPM … in other words, more than 80% loaded"; the Liu–Layland bound for four tasks is 75.68% and "would miss deadlines even if RMA had been used." The same slides note that NASA's analysis found "no deadline misses seen" and that worst-case execution time was "difficult due to busy-wait loops, indirect recursion". [SEC]{.sec} These are an **expert's** slides in a case Toyota contested; we use them for *the check*, not the verdict: *compare U with the bound, and ask what the interrupts and background load add.* A load above the bound is a reason to run the exact analysis, not proof of a miss.
:::

## What utilization does not capture

| Missing from U | Why it matters | Where it is handled |
|---|---|---|
| deadlines shorter than periods | a task with D < T can miss at lower U | deadline-monotonic priorities and RTA (ch. 9) |
| blocking on shared resources | a high-priority task waits for a low one | blocking term B (ch. 9, 13) |
| release jitter | releases are not exactly periodic | jitter term J (ch. 9) |
| interrupts and the tick | consume CPU above every task | add them as top-priority tasks (ch. 4, 9) |
| overhead of context switches | adds to every job | measure it (R2: 4–24 µs per wake-up) |
| execution time that varies | U uses the *budget* | the budget must be an upper bound (ch. 9, 20) |

::: trap
**Trap: "we're at 70%, we're fine."** A single-number load says nothing about the *lowest-priority* task's deadline, about bursts, or about blocking. It also hides the opposite error: a set at 95% with harmonic periods and no blocking may be fine. Use utilization to *triage*, then compute.
:::

## Check yourself

::: check
1. Tasks (C, T) in ms: (2, 10), (3, 20), (8, 40), plus a 100 µs interrupt every 1 ms. Compute U with and without the interrupt and compare with the bound for the right *n*.
2. Which tasks in your system have harmonic periods? What would you change to make more of them harmonic?
3. A colleague says the bound is 69%, so 75% load is unsafe. What do you ask them?
:::

**Lab link.** H3 demo 1 and the `rtcalc.py` workbench.
