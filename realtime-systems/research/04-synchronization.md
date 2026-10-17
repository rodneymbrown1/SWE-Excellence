# 04 · Shared state, races, priority inversion, deadlock

## 1. Evidence: what concurrency bugs actually look like (Lu et al., ASPLOS 2008) [S10, **P**]

Study of **105 randomly selected real-world concurrency bugs** (**74 non-deadlock, 31 deadlock**) from four applications (MySQL, Apache, Mozilla, OpenOffice). **Scope caveat from the paper:** results are "associated with the four examined applications and the programming languages these applications use"; they are desktop/server C/C++/Java programs, **not RTOS code**. Findings verified against the paper's findings table:

| # | Finding (paper's wording shortened) | Use |
|---|---|---|
| 1 | **97%** of non-deadlock bugs are *atomicity-violation* or *order-violation* | Teach these two patterns first |
| 2 | **32%** of non-deadlock bugs are order violations | "A must happen before B" bugs are common and are **not** fixed by locks |
| 3 | **96%** of concurrency bugs manifest if a certain partial order between **2 threads** is enforced | Two-task tests find most bugs |
| 4 | **22%** of deadlock bugs: one thread acquiring a resource it already holds | Self-deadlock: non-recursive mutex taken twice |
| 5/6 | **66%** involve one variable; **34%** involve multiple variables | A per-variable lock discipline misses a third |
| 7 | **97%** of deadlocks involve **two threads** waiting circularly on at most two resources | Lock ordering between pairs |
| 8 | **92%** manifest if a partial order among **≤ 4 memory accesses** is enforced | Small windows → rare, hard to reproduce |
| 9 | **73%** of non-deadlock bugs were fixed by techniques **other than** adding/changing locks | Fix is often redesign (ownership, ordering, copy) |
| 10 | **61%** of deadlock bugs fixed by preventing one thread acquiring one resource (e.g. lock) | Often by removal, not reordering |

How the book uses it: ch. 12 teaches *atomicity violation* and *order violation* by name and gives an RTOS example of each; Lab R-series plants one of each.

## 2. Definitions the book uses

- **Atomicity violation:** a code region assumed atomic is interleaved by another thread (e.g. check-then-act on a flag).
- **Order violation:** two accesses are assumed to occur in order A then B but nothing enforces it (e.g. a consumer reading before the producer initialized).
- Both definitions follow Lu et al.'s pattern names.

## 3. Therac-25 — shared variables, non-atomic test-and-set (Leveson & Turner 1993) [C06, **P**]

Verified passages (paper text):

- The paper states the software "allows concurrent access to shared data stored in shared variables, and that the 'test' and 'set' for such variables are not indivisible operations" and discusses the resulting **race conditions**. [exact words checked against the PDF text; see line ~247–251 of `therac25-leveson/text.txt`]
- The Tyler, Texas accidents (the report's timeline: 21 March 1986 and 11 April 1986 overdoses) involved an operator editing treatment parameters quickly; the report's description (read via MIT/RIT copies in a search; **S**) is that edits within a few seconds could be missed by the setup routine. The book says "within seconds" and does **not** quote the precise window.
- **Used in book:** the canonical *atomicity violation* with real harm; plus the context lesson that the *same* bug existed with hardware interlocks on earlier models, which masked it — "interlocks hid the bug; removing them exposed it" (paper discusses removal of hardware interlocks; wording paraphrased).

## 4. Priority inversion — Pathfinder (JPL's own account) [C02, **P**]

Reeves (JPL Pathfinder flight software lead), 15 Dec 1997 — verified:

- Architecture: 1553 bus activity on an **8 Hz** (0.125 s) cycle; `bc_sched` sets up transactions, `bc_dist` collects results; "The bc_sched task is the highest priority task in the system (except for the vxWorks 'tExec' task). The bc_dist is third highest (a task controlling the entry and landing is second). All of the tasks which perform other spacecraft functions are lower. Science functions, such as imaging, image compression, and the ASI/MET task are still lower."
- Failure: "a failure of the bc_dist task to complete its execution before the bc_sched task started"; reaction "to reset the computer".
- Mechanism: "The higher priority bc_dist task was blocked by the much lower priority ASI/MET task that was holding a shared resource. The ASI/MET task had acquired this resource and then been preempted by several of the medium priority tasks." The resource: "a mutual exclusion semaphore used within the select() mechanism to control access to the list of file descriptors" — **inside a vxWorks library call (`select`/pipe), not in the team's own code**.
- Diagnosis: a trace/log facility (ring buffers; instrumented pipe, msgQ, interrupt, select, tExec) was **left in the flight software "by design"** under "test what you fly and fly what you test". "In less that 18 hours we were able to cause the problem to occur [in the lab]."
- Fix: "change the creation flags for the semaphore so as to enable the priority inheritance" — via a Wind River global configuration variable (undocumented in the public docs, per Reeves); they ran **analysis and test** because the variable affected "all of the select semaphores created after that point".
- Why not caught earlier: "The problem would only manifest itself when ASI/MET data was being collected and intermediate tasks were heavily loaded. Our before launch testing was limited to the 'best case' high data rates and science activities." Plus: the team **saw it before landing but could not repeat it** and ranked it lower than entry/landing software — "We had our priorities right" (their words).
- Reeves's lesson: "A good lesson when you fly COTS stuff — make sure you know how it works."
- The earlier Jones message (C03, **P**, secondary) is explicitly corrected by Reeves ("I winged it and I sure did get it wrong" is Reeves about his earlier talk with Wilner); the book uses **Reeves**, not Jones, for mechanism.

## 5. Priority inheritance and ceiling protocols (Sha, Rajkumar, Lehoczky 1990) [S05, **P**]

- Abstract (verified): "A direct application of commonly used synchronization primitives such as semaphores, monitors, or the Ada rendezvous can lead to uncontrolled priority inversion, a situation in which a higher priority job is blocked by lower priority jobs for an indefinite period of time." Both protocols solve it. The **priority ceiling protocol** "reduces the worst case task blocking time to at most the duration of execution of a single critical section of a lower priority task. In addition, this protocol prevents the formation of deadlocks." (single-processor, binary-semaphore model)
- Practitioner reading: *inheritance bounds the blocking but permits chains and deadlock; ceiling bounds to one critical section and prevents deadlock but needs resource knowledge up front.*
- FreeRTOS (T01 ch. 8 "Resource Management", **P**): "mutexes include a basic priority inheritance mechanism, whereas binary semaphores do not"; inheritance "does not fix priority inversion, but merely lessens its impact by ensuring that the inversion is always time bounded"; it also warns that inheritance "complicates system timing analysis, and it is not good practice to rely on it for correct system operation". Zephyr `k_mutex` supports priority inheritance (T03 docs, **Sn**). OSEK/AUTOSAR resources use the immediate priority ceiling (T12 **Sn**).

## 6. `volatile`, compilers and interrupts

- **Eide & Regehr (EMSOFT 2008)** [S12, **S**]: tested **thirteen production C compilers**; "for each compiler, cases where the generated code for accessing volatile variables was wrong"; in **96%** of the cases where a random test program was miscompiled, a simple source-level rewrite made the faulty compiler produce correct code (abstract, LLVM pubs page). Regehr's retrospective notes tension between `volatile` and optimization (blog post, read). Date caveat: 2008-era compilers.
- **What `volatile` is for:** memory-mapped hardware registers and ISR-visible flags; **not** a substitute for atomicity or ordering. (Standard C semantics; no single citation.)

## 7. Lee (2006), "The Problem with Threads" [S11, **P**]

Quoted lines (verified): "Threads, as a model of computation, are wildly nondeterministic, and the job of the programmer becomes one of pruning that nondeterminism." and the prescription "Nondeterminism should be explicitly and judiciously introduced". Book use: motivates **ownership** (one writer), **message passing** (copy or move), and **run-to-completion** — i.e., reduce the number of places where interleaving matters.

## 8. Deadlock

- Four conditions (mutual exclusion, hold-and-wait, no preemption, circular wait) — OSTEP `threads-bugs` [S21, **P**] presents them following Coffman et al. (1971); we cite OSTEP, not the 1971 paper (not read).
- Lu et al. finding (7): **97%** of deadlocks are two threads/≤2 resources → a *pairwise lock-order table* is a cheap review artifact (Handbook).
- Pathfinder-style inversion + a watchdog that only runs in a low-priority task can hide a hang (see `06-…` Memfault example).

## 9. Use in documents

| Item | Where |
|---|---|
| Lu et al. table | Book ch. 12 |
| Therac | Book ch. 12 |
| Pathfinder | Book ch. 13; Lab R3 (replica using binary semaphore vs mutex) |
| SRL protocols | Book ch. 13 |
| Eide–Regehr, `volatile` | Book ch. 4 and ch. 12; Appendix B (C survival kit) |
