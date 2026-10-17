# The implicit requirements {.chapter data-part="PART 6 · PUT IT TOGETHER"}

<p class="lede">The requirements you are given say what the component does. The ones that decide whether it works on the device are never stated: they are consequences of running on a scheduler, with queues, interrupts and a finite memory, on a machine with a clock. This chapter is the list. Use it as a review checklist and as a prompt for questions to the people who wrote the spec.</p>

## How to use the list

Each row is a requirement that is **implicit** in almost every RTOS component. For each, ask the question and look for the evidence. If nobody can answer, you have found a gap before the device did. The chapter column points to the explanation; the handbook has the same list as a checklist you can tick.

## 1 · Timing

| # | Implicit requirement | Ask | Evidence | Ch. |
|---|---|---|---|---|
| T1 | Every periodic component has a **period** and a **deadline** | What are they, and where is each written? | spec or code comment; default D = T is a choice | 1 |
| T2 | Every component has a **budget** (WCET) and the budget is an **upper bound** | Who set it, how, under what load? | analysis or high-water mark + margin | 9, 20 |
| T3 | The **miss policy** is defined | What happens to the next release when a job overruns? | framework docs; test | 11 |
| T4 | **Jitter** is bounded | How much can the release time vary, and who cares? | period histogram | 3, 17 |
| T5 | **Interrupts and the tick** are in every budget | What fraction of the CPU do they use? | trace, run-time stats | 4 |
| T6 | **Counters wrap** and clocks have a type | When does each one wrap? Which comparisons break? | width, rate, uptime arithmetic | 3 |
| T7 | **CPU load** has headroom | What is U, and what is the exact worst-case response? | `rtcalc`, measurement | 8, 9 |
| T8 | **Rates** are justified and compatible | Why this rate? Harmonic with its neighbours? | control or input argument | 17 |
| T9 | Delays use **absolute** times for periods | `vTaskDelay` or `DelayUntil`? Initial `last` valid? | code review | 2, 3 |

## 2 · Scheduling

| # | Implicit requirement | Ask | Evidence | Ch. |
|---|---|---|---|---|
| S1 | **Priorities** follow timing, not importance | Who chose them, by what rule? | rate/deadline order | 7 |
| S2 | No task **spins** or never blocks | Does every task wait on something? | code review; trace | 6, 7 |
| S3 | **Equal-priority** tasks are fair enough | Who shares a level, and is time slicing on? | config | 7 |
| S4 | **Timer callbacks** are short | At what priority do they run? Do they block? | timer task priority | 7 |
| S5 | The **idle task** can run | Can everything block? Are deleted tasks reclaimed? | idle share in stats | 6 |
| S6 | Overload degrades **predictably** | Which components starve first? | overload test | 11 |

## 3 · Messaging

| # | Implicit requirement | Ask | Evidence | Ch. |
|---|---|---|---|---|
| M1 | Every queue has a **depth** that is justified | From what burst? | formula, test | 15 |
| M2 | Every queue has an **overflow policy** | Block, drop newest, drop oldest, overwrite? | code, QoS | 15, 16 |
| M3 | **Drops are counted and visible** | Where is the counter? Who reads it? | counter, telemetry | 15 |
| M4 | Data has an **age limit** and a **source timestamp** | How old is too old? Stamped where, by what clock? | timestamp check | 17 |
| M5 | Each **rate crossing** has a rule | Latest, average, hold, interpolate? | design note | 17 |
| M6 | Each subscription has **QoS** that matches its need | Reliability, depth, durability, deadline, lifespan? | QoS table | 16 |
| M7 | **Startup order** and readiness are defined | Who must exist before whom? What gates activation? | lifecycle | 18 |
| M8 | **Message ownership** is clear at every stage | Who frees it? Copy or move? | pool accounting | 14, 18 |

## 4 · Synchronization

| # | Implicit requirement | Ask | Evidence | Ch. |
|---|---|---|---|---|
| Y1 | Every shared datum has an **owner**, a **protection rule**, and a **longest hold time** | Fill the five-fact line | table | 12 |
| Y2 | Multi-field data is read as a **snapshot** | Are two related values ever read at different times? | invariant check | 12 |
| Y3 | **Mutexes** (with inheritance) guard shared resources; binary semaphores signal | Which is used where? | code review | 13 |
| Y4 | **Blocking time** is bounded and counted in response times | What is the longest lower-priority critical section? | B term | 9, 13 |
| Y5 | Locks are taken in a **fixed order** and never held across blocking calls | Lock-order table? | review | 13 |
| Y6 | **Library and driver calls** are known to lock or not | What does this call lock, at whose priority? | docs, trace | 13 |
| Y7 | ISRs use only **ISR-safe** calls and short critical sections | Which calls? How long with interrupts off? | review, latency | 4, 12 |

## 5 · Reliability

| # | Implicit requirement | Ask | Evidence | Ch. |
|---|---|---|---|---|
| R1 | A **watchdog** exists, is fed only after progress of **every** task, and is not fed from an interrupt | Who feeds it, under what condition? | code, injection test | 19 |
| R2 | The **reaction** to a detected failure is defined | Reset, restart one component, degrade? | design, test | 19 |
| R3 | **Containment**: a failing component cannot silently take down another | Stack, queue, memory boundaries? | review | 14, 19 |
| R4 | **Restart** state is defined and tested, including **repeated** restarts | What survives? What if start-up always fails? | restart test | 18, 19 |
| R5 | **Evidence** survives a reset | Reset reason, check-in mask, trace tail? | post-mortem | 19 |
| R6 | **Stacks and heaps** have measured margins, overflow is detected | High-water marks? Hook? | margins | 14 |
| R7 | **Resources that grow** with time are bounded | Files, logs, caches, queues, uptime? | soak test | 14 |
| R8 | **Silent consumers and sensors** are detected | Heartbeat, lease, age check? | injection test | 15, 19 |

## 6 · Observability

| # | Implicit requirement | Ask | Evidence | Ch. |
|---|---|---|---|---|
| O1 | Each requirement has **one number, a method and a margin** | p99.9? max? over how many samples, under what load? | requirement table | 20 |
| O2 | Latency is reported as a **histogram**, from **open-loop** measurement | Mean or tail? Does the tester wait for replies? | histogram | 20 |
| O3 | **Releases, completions and misses** are counted separately | Where? | counters | 11, 20 |
| O4 | There is a **trace** and it is **left in the product** | Ring buffer? Who dumps it, on what event? | trace | 20 |
| O5 | The **observation itself** does not change the result | Printing in a task? Breakpoints on hot paths? | cost measured | 3, 20 |
| O6 | The **observed maximum is not called WCET** | Which words does the report use? | review | 9, 20 |
| O7 | **Tests drive the worst case** | Slow path, burst, all interrupts, cold cache? | test plan | 20 |

## Scoring yourself

::: check
Pick a component you own. For each of the 45 rows above, mark: **known** (you can point to the evidence), **assumed** (you believe it but have no evidence) or **unknown**. A good first target is no *unknown* in Timing and Reliability. The number of *assumed* rows is the size of your risk.
:::

::: why
**Where this list comes from.** Each row corresponds to a mechanism that failed in a cited case: T6 (Patriot, 787, tick wrap lab), T2/T7 (Toyota check, R2 measurements), S2 (the lab's spinning-task trap), M3 (the capstone's silent drops, Northeast blackout), M4 (Ingenuity Flight 6), Y3/Y4/Y6 (Pathfinder), Y2 (Therac-25, the capstone's torn reads), R1 (Toyota testimony, Memfault, lab R5), R3/R4 (Ariane, Spirit), O2 (coordinated-omission lab), O4 (Pathfinder's trace). It is a *checklist derived from incidents and labs*, not a complete theory; extend it with your own.
:::
