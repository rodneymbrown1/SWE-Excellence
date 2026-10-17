# 07 · Frameworks to learn from, and the best resources (ranked, with reasons)

How "best" was decided: (1) **primary** (written by the people who did the work), (2) **evidence-bearing** (data, counterexamples, incident reports — not opinion), (3) **free and readable**, (4) **fit** with the six questions (timing, scheduling, messaging, synchronization, reliability, observability). "Read" = opened and read in this project; "Listed" = known standard, recommended, **not opened** here.

## A. Reference frameworks (what to read to understand a framework you will be dropped into)

| Framework | Why it matters here | What to read first | Status |
|---|---|---|---|
| **FreeRTOS** | The most widely recognised MCU RTOS; small enough to read; the book is free and current. Our labs run it. | *Mastering the FreeRTOS Real Time Kernel* ch. 4 (tasks), 5 (queues), 7 (interrupts), 8 (resources), 12–13 (developer support, troubleshooting) | **Read** (T01) |
| **Zephyr** | Modern RTOS with cooperative + preemptive threads, optional EDF, time slicing, workqueues, devicetree | Kernel → Scheduling page | **Read** (scheduling page, T03) |
| **F´ (F Prime)** | JPL's component framework: *components, ports, queues, rate groups* are exactly the "frequency of a component" and "message lifecycle" vocabulary | Component and port selection; `ActiveRateGroup` and `RateGroupDriver` SDDs | **Read** (T07) |
| **cFS (core Flight System)** | NASA's flight software framework: apps, **software bus** pub/sub with pipes, scheduler tables, time and event services | cFS README + cFE docs; the Scheduler (SCH) app configuration | **Read overview only** (T08) |
| **ROS 2** | DDS-style pub/sub with QoS; lifecycle nodes; executors | About QoS settings; Managed (lifecycle) nodes design; Casini et al. on executor timing | **Read** (T05, T06, S14) |
| **AUTOSAR Classic / OSEK OS** | Automotive: tasks, alarms, counters, schedule tables, priority-ceiling resources, Watchdog Manager (alive/deadline/logical supervision) | OSEK OS spec; AUTOSAR WdgM SWS | **Listed / Sn** (T11, T12) |
| **Linux PREEMPT_RT / SCHED_DEADLINE** | "Real-time on a big CPU": EDF+CBS in mainline; PREEMPT_RT in mainline from 6.12 | Kernel docs: SCHED_DEADLINE; real-time theory | **Read** (T04) |

## B. Foundations — best books and papers (in the order we recommend reading)

1. **Liu & Layland (1973)** — read the first 10 pages and Theorems 1, 5, 7. Short, readable, the source of the 69.3% and 100% numbers. (S01, **Read**)
2. **Eyles (2004), "Tales from the Lunar Module Guidance Computer"** — the best single account of why a priority-driven executive beats a time-sliced one, with real margins and a real overload. (C01, **Read**; free)
3. **Reeves (1997), Pathfinder email** — the most instructive five pages on priority inversion because it includes *how it was found* and *why it was missed*. (C02, **Read**; free)
4. ***Mastering the FreeRTOS Real Time Kernel*** — chapters above. (T01, **Read**; free)
5. **Arpaci-Dusseau, *Operating Systems: Three Easy Pieces*** — free; "Limited Direct Execution" (timer interrupt + context switch), "Scheduling: Introduction", and the concurrency bugs and semaphore chapters. (S21, **Read**; free)
6. **Buttazzo (2005), "Rate Monotonic vs. EDF: Judgment Day"** — the one paper that corrects folklore with counterexamples. (S03, **Read**)
7. **Audsley et al. (1993)** — response-time analysis in 9 pages. (S04, **Read**)
8. **Sha, Rajkumar & Lehoczky (1990)** — priority inheritance and ceiling protocols. (S05, **Read**; long — read abstract, §II–III)
9. **Lu et al. (2008)** — the data on what concurrency bugs are. (S10, **Read**)
10. **Koopman (2014) slides** — a worked, referenced case study that applies the above to a real product (with the expert-witness caveat). CC BY 4.0. (S22, **Read**)
11. **Holzmann (2006), "Power of 10"** — 2 pages. (S17, **Read**)
12. **Wilhelm et al. (2008)** — what WCET analysis can and cannot promise. (S08, **Read** key passages)
13. **Cervin (2003) thesis, ch. 2** — how timing affects control. (S09, **Read** passages)
14. **Dunkels et al. (2006)** — protothreads: stackless cooperative concurrency in 2 bytes each. (S16, **Read**)
15. **Davis et al. (2007)** — a cautionary tale about published analysis. (S13, **Read** abstract)

**Listed, standard, not opened here (recommended from general knowledge — verify before relying):**
Jane W. S. Liu, *Real-Time Systems* (2000) [user-supplied] · Burns & Wellings, *Real-Time Systems and Programming Languages* · Kopetz, *Real-Time Systems: Design Principles for Distributed Embedded Applications* · Buttazzo, *Hard Real-Time Computing Systems* · Klein et al., *A Practitioner's Handbook for Real-Time Analysis* (SEI RMA handbook; only book listings found, no free copy) · Koopman, *Better Embedded System Software* · Joseph Yiu, *The Definitive Guide to ARM Cortex-M* · Samek, *Practical UML Statecharts in C/C++* and the Modern Embedded Systems Programming course.

## C. Practitioner sources worth following

| Source | Why | Status |
|---|---|---|
| **Memfault Interrupt blog** | Concrete, runnable firmware articles (watchdog, context switch, fault analysis, coredumps, watchpoints). The watchdog article contains a reproducible failure of the "low-priority task feeds the dog" design. | **Read** (T09) |
| **Ganssle — watchdog guide** | Long-standing practitioner guidance | **Read** (T10) |
| **Embedded Online Conference** | Talks, including Gillian Minnehan's *GDB Deep Dive* (user-supplied; ties to the Debugging project) | **Listed** (session page only) |
| **Gil Tene — "How NOT to Measure Latency"** | The correct way to think about latency data | **Read** (slides, S19) |
| **Valvano (UT Austin)** — *Embedded Systems: Shape the World* (edX) and the RTOS volume | Zero-to-RTOS on a Cortex-M; building a tiny RTOS; user-supplied | **Read syllabus/outline** (T15) |
| **Samek / Quantum Leaps** | Active-object (event-driven, run-to-completion) alternative to blocking threads; vendor viewpoint | **Read** blog (T16) |
| **OSADL QA Farm** | Public, continuous real-time latency measurements on real hardware | **Read** index only (T13) |

## D. Evidence ranking summary (what we trust for which kind of claim)

| Claim type | Best evidence in this library |
|---|---|
| "Utilization ≤ 69.3% always works for RM" | Liu & Layland (theorem) |
| "How much can I really load the CPU" | Exact analysis (Audsley), not a rule; average-case 88% (Lehoczky–Sha–Ding, **Sn**) |
| "Is RM/EDF better" | Buttazzo (counterexamples), Linux/Zephyr docs (what exists in practice) |
| "How common are concurrency bugs of kind X" | Lu et al. (n=105, four server/desktop apps) |
| "Does this failure happen in real systems" | Case files (C01–C13) |
| "How do I get this right on target" | Framework docs + the labs in this project **[RAN]** |

## E. Framework cross-reference table (used in the Handbook)

| Concept | FreeRTOS | Zephyr | F´ | cFS | ROS 2 | OSEK/AUTOSAR |
|---|---|---|---|---|---|---|
| Unit of execution | task | thread | active component (task) | app (task) | node/executor callbacks | task / runnable |
| Periodic activation | `vTaskDelayUntil`, timer | `k_timer`, workqueue | rate group (cycle port) | SCH table (minor frames) | `create_timer` | alarm → task / schedule table |
| Priority | fixed, higher number = higher | fixed (+ optional EDF) | thread priority per instance | task priority per app | OS-level only (executor-level ordering) | fixed + ceiling |
| Message queue | `xQueue*` | `k_msgq`, FIFO | async port queue (depth) | SB pipe (depth) | subscription queue (QoS depth) | (COM / RTE) |
| Pub/sub | (none built-in; build) | zbus | (ports are point-to-point) | Software Bus | topics | RTE / SOME-IP |
| Mutex w/ inversion protection | mutex (inheritance) | `k_mutex` (inheritance) | guarded port (mutex) | OS_MutSem | — | resource (ceiling) |
| Watchdog | `configASSERT` + your design | task watchdog | health component | HS app | liveliness QoS | WdgM |
| Lifecycle | — | — | topology start/stop | ES start/stop app | lifecycle nodes | EcuM / OS start |

*(Cells reflect the researched sources where marked in sections above; cells for cFS, Zephyr zbus, OS_MutSem, HS app and EcuM are from general knowledge and are marked **to verify in your framework** in the Handbook.)*
