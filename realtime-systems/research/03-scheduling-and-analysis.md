# 03 · Scheduling and schedulability analysis

## 1. Rate-monotonic (RM) utilization bound — what it does and does not say

- **Source:** Liu & Layland 1973 (S01, **P**). Bound `U ≤ m(2^{1/m} − 1)`; m=1 → 1.000, 2 → 0.828, 3 → 0.780, 4 → 0.757, 5 → 0.743, 10 → 0.718, ∞ → ln 2 ≈ 0.693. (We recomputed these in `labs/host/` and checked them against the formula.)
- **Sufficient, not necessary.** Any task set with U at or under the bound is schedulable by RM (under assumptions A1–A5). Above the bound is *inconclusive*, not *failing*.
- **Average case is better than the bound — with a caveat.** Lehoczky, Sha & Ding (1989) [S06, **Sn**]: for randomly generated task sets with uniformly distributed parameters the *average breakdown utilization* is about **88%**. A later arXiv paper (0912.3852, **Sn**) argues the threshold for large sets is nearer **0.80** and that "breakdown utilization" ≠ "utilization threshold". The book therefore says: *"69.3% is the guarantee, high-80s is typical for random sets, and harmonic periods can reach 100%. Do not plan on the typical number — compute the exact answer."*
- **Harmonic periods** (each period an integer multiple of the next-shorter one) make RM schedulable up to U = 1.0. This follows from the Liu–Layland theorems (Theorem 4's ratio condition / the construction in the proof: when the period ratios are integers the bound is 1) — and is verified by our simulator for several sets (`labs/host/`). Used in ch. 17 as a reason to choose rates that are harmonic.

## 2. Response-Time Analysis (RTA) — the practical test

- **Source:** Audsley, Burns, Richardson, Tindell, Wellings 1993 [S04, **P**] (the paper names earlier equivalent work by Joseph & Pandya and by Lehoczky). Verified definitions in the paper: `C_i` worst-case computation time; `T_i` lower bound on inter-arrival time; `D_i` deadline; `B_i` worst-case blocking by lower-priority tasks (via priority ceiling); `J_i` release jitter; `I_i` interference by higher-priority tasks; `R_i` worst-case response time; and the central equation **R_i = C_i + B_i + I_i** with `I_i = Σ_{j ∈ hp(i)} ⌈R_i / T_j⌉ · C_j`, solved by fixed-point iteration starting from `R_i⁰ = C_i + B_i`.
- Paper's own words that matter for practice: the analysis "is not based on the notion of processor utilisation" and gives "sufficient and necessary" (i.e. exact) tests for the model, so a failing RTA means a miss is *possible*; a passing RTA means *no miss* **if** the C, T, B, J inputs are true upper bounds.
- The paper tested the method on an avionics case study and reports the predictions "in close agreement with the behaviour exhibited during simulation studies".
- **The inputs are the hard part.** WCET (S08) and blocking (S05) are what you do not know. The book's rule: *RTA converts your assumptions into a yes/no; it cannot validate the assumptions.*
- **ISRs and the tick** are higher priority than every task and appear in `hp(i)` for every task. Omitting them is the most common practical error (Handbook checklist item).

## 3. EDF (deadline-driven) and its place in real systems

- **Theory:** EDF is optimal on one processor for the Liu–Layland model: schedulable iff `U ≤ 1` (S01 Thm. 7).
- **Linux** has EDF in the mainline kernel: `SCHED_DEADLINE`, "basically an implementation of the Earliest Deadline First (EDF) scheduling algorithm, augmented with a mechanism (called Constant Bandwidth Server, CBS)". Parameters `runtime`, `deadline`, `period`; "avoiding any interference between different tasks (bandwidth isolation)". (T04, **P**)
- **Zephyr** has an optional EDF: `CONFIG_SCHED_DEADLINE` ("off by default"); deadlines order only threads **of equal static priority**; `k_thread_deadline_set()` takes a cycle-count delta; the scheduler does not enforce that the deadline is met. (T03, **P** via Kconfig page + doc; commit-message details from search **Sn**.)
- **FreeRTOS** kernel scheduling is **fixed-priority preemptive** (with optional time-slicing among equal priorities); it does not ship EDF (T01, ch. 4, **P**).
- **OSEK/AUTOSAR OS:** fixed-priority with priority-ceiling resources (T12, **Sn** secondary lecture notes).
- **Reading:** most MCU-class RTOSes you will meet use fixed priorities. Know EDF so you can read Linux/Zephyr docs and understand why your framework's "rate group" cannot do it.

## 4. RM vs EDF — the evidence, and the misconceptions it corrects

**Buttazzo (2005)** [S03, **P**]. Abstract (verified): "many misconceptions still exist … claim that RM is easier to analyze than EDF, it introduces less runtime overhead, it is more predictable in overload conditions, and causes less jitter in task execution. Since the above statements are either wrong, or not precise …". Specific items used:

| Claim in the wild | What the paper shows | How we use it |
|---|---|---|
| "EDF has more overhead" | Counting context switches, EDF often preempts *less* than RM (e.g. for two tasks, one preemption in the hyperperiod vs. more under RM; simulation plots of preemptions vs. number of tasks and vs. load) | Don't pick RM *only* for overhead reasons |
| "RM is predictable in overload — the long-period tasks fail first" | "this property does not hold under RM (neither under EDF)": counterexample **C = (2,3,1,1), T = (5,9,20,30)** with a 1.5-unit overrun in τ1: the task that misses is **τ2, not τ4** | **Reproduced in our simulator** (Lab H3 / ch. 11) **[RAN]** |
| What RM *does* guarantee | "under RM, an overrun in task τi cannot cause tasks with higher priority to miss their deadlines, whereas under EDF any other task could miss" | The one real overload property of fixed priority: **overrun damage flows downward in priority** |
| Permanent overload (U > 1) | EDF "automatically performs a period rescaling": average period `T̄_i = T_i · U` (Cervin et al. 2002 theorem cited in the paper); under RM "a permanent overload may cause a complete blocking of the lower priority tasks" | Example U = 4/8 + 6/12 + 5/20 = 1.25 → EDF behaves like periods (10, 15, 25) |
| Timeline (cyclic) scheduling | "fragile during overload … domino effect"; "a little change in a task rate … thus requiring a complete redesign of the scheduling table" | Ch. 5 |

Caution: Buttazzo is an *advocate* of EDF; the paper is peer-reviewed and gives counterexamples we can check, which is why it is used — but the book tells the reader to run the numbers for their own task set.

## 5. Real-world evidence on utilization

- **Apollo 11:** 13% unexpected load on a ≈10–15% margin produced executive overflow, not collapse, because the executive was priority-driven (C01).
- **Toyota ETCS (expert testimony, S22, P):** claims that (a) the OS "multiple priority levels; each with round-robin tasking"; (b) "main CPU less than 20% idle time at 5000 RPM … more than 80% loaded"; (c) Liu–Layland RMA bound for 4 tasks 75.68% and 69.3% asymptote so the system "would miss deadlines even if RMA had been used". **Caveat to carry in the text:** these are plaintiff's-expert slides summarizing NASA's appendix and trial testimony; Toyota disputed the conclusions. The book uses them as an *illustration of the check* (compare U to the bound; ask what the ISR/ background load is), not as a finding about Toyota's cars. Also noted in the slides: "no deadline misses seen" in the NASA analysis — the book repeats that.
- **Pathfinder (C02):** `bc_sched` highest priority except `tExec`; `bc_dist` third; entry/landing second; science lowest. A deadline check **inside the system** (`bc_sched` checking that `bc_dist` finished) converted a hidden timing fault into a visible, recoverable reset.

## 6. Distributed example: CAN bus is a fixed-priority non-preemptive scheduler

- **Davis, Burns, Bril, Lukkien (2007)** [S13, **P**]: CAN is used extensively ("in excess of 400 million CAN enabled microcontrollers manufactured each year"). The 1994 schedulability analysis for CAN, cited "in over 200 subsequent papers" and embedded in commercial tools used by major automakers, "is flawed. It may provide guarantees for messages that will in fact miss their deadlines in the worst-case." The paper also shows the priority-assignment policy "previously claimed to be optimal for CAN, is not in fact optimal".
- **Lesson used in book (ch. 21):** (1) a published, widely used analysis can be wrong; use tools *and* measurement; (2) message ID = priority; arbitration is non-preemptive once a frame starts, which adds a blocking term.
- **Tool-ish:** the Python helper in `labs/host/rta.py` includes the CAN blocking term as an optional input (not the full revised analysis); the book says so.

## 7. Multi-rate / hyperperiod facts used

- Hyperperiod = LCM of periods; frame (minor cycle) must divide each period and be ≥ longest task (S03 intro describes it; textbook constraints in Liu's book not re-read).
- Number of jobs in a hyperperiod can be large for non-harmonic periods; example in ch. 5: periods 10, 20, 40, 50 ms → hyperperiod 200 ms; periods 10, 25, 40 → 200 ms; periods 7, 11, 13 ms → 1001 ms. Arithmetic only.

## 8. Use in documents

| Item | Where |
|---|---|
| Bound table, harmonic exception, 88% caveat | Book ch. 8; Handbook "utilization sanity" card |
| RTA procedure + worked example | Book ch. 9; Lab H3 (the code), Lab R2 (measure on RTOS) |
| EDF theory, Linux/Zephyr support | Book ch. 10 |
| RM vs EDF misconceptions | Book ch. 10–11; Lab H3 reproduces the counterexample |
| CAN example | Book ch. 21 |
