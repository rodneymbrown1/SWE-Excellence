# Where to go next: ranked reading {.appendix data-part="APPENDICES"}

Ranked by: written by the people who did the work; carries evidence (data, counterexamples, incident reports); free; fits the six questions. "Read" = opened for this project; "listed" = a standard work we did not open (check before relying on it).

## Start here (free, short, high yield)

| # | Resource | Why | Status |
|---|---|---|---|
| 1 | **Eyles (2004), "Tales from the Lunar Module Guidance Computer"** | the best account of why a priority executive beats a time-sliced one, with a real overload | Read |
| 2 | **Reeves (1997), Pathfinder email** | five pages on inversion, including how it was found and why it was missed | Read |
| 3 | ***Mastering the FreeRTOS Real Time Kernel*** (free, GitHub) | ch. 4 tasks, 5 queues, 7 interrupts, 8 resources, 12–13 debugging | Read |
| 4 | **Liu & Layland (1973)**, first 10 pages | the source of 69.3% and the assumptions | Read |
| 5 | **OSTEP**: Limited Direct Execution, Scheduling, Concurrency bugs, Semaphores | free textbook chapters; the OS background | Read |
| 6 | **Memfault Interrupt** (watchdog; context switching; fault analysis) | runnable firmware articles | Read |
| 7 | **Koopman's Toyota slides** (CC BY 4.0) | a worked review applying these topics to a product, **with the expert-witness caveat** | Read |

## Then, for depth

| Resource | Why | Status |
|---|---|---|
| Buttazzo (2005), "Rate Monotonic vs. EDF: Judgment Day" | corrects folklore with counterexamples | Read |
| Audsley et al. (1993) | response-time analysis in nine pages | Read |
| Sha, Rajkumar, Lehoczky (1990) | inheritance and ceiling | Read (abstract, §II–III) |
| Lu et al. (2008) | data on what concurrency bugs are | Read |
| Wilhelm et al. (2008) | WCET overview | Read (passages) |
| Cervin (2003) thesis, ch. 2 | timing and control | Read (passages) |
| Holzmann (2006), Power of 10 | two pages of coding discipline | Read |
| Dunkels et al. (2006), protothreads | stackless concurrency | Read |
| Davis et al. (2007) | a cautionary tale about published analysis | Read (abstract) |
| Gil Tene, "How NOT to Measure Latency" | reporting latency honestly | Read |
| Ganssle, "A Guide to Watchdog Timers" | practitioner watchdog design | Read |
| Valvano (UT Austin), *Embedded Systems* and the RTOS volume; edX course | build a tiny RTOS from a Cortex-M | Syllabus read |

## Standard textbooks (listed, not opened here)

Jane W. S. Liu, *Real-Time Systems* · Burns & Wellings, *Real-Time Systems and Programming Languages* · Kopetz, *Real-Time Systems: Design Principles for Distributed Embedded Applications* · Buttazzo, *Hard Real-Time Computing Systems* · Klein et al., *A Practitioner's Handbook for Real-Time Analysis* · Koopman, *Better Embedded System Software* · Yiu, *The Definitive Guide to ARM Cortex-M*.

## Framework documentation

FreeRTOS · Zephyr (Kernel → Scheduling) · F´ (component and port selection; rate-group SDDs) · cFS (cFE documentation) · ROS 2 (QoS; managed nodes) · AUTOSAR (Watchdog Manager) · Linux (`SCHED_DEADLINE`, real-time docs).

## A path

| If you have… | Read | Do |
|---|---|---|
| one afternoon | Eyles, Reeves, this book's ch. 1, 7, 9, 13, 15, 19, 20, 23 | R3 and R10 |
| one week | the FreeRTOS book ch. 4–8; OSTEP scheduling and concurrency; this book Parts 1–3 | H3, R1–R3, R6 |
| one month | all of this book; Buttazzo; Audsley; Lu; Wilhelm | every lab; then port R10 to your framework |
