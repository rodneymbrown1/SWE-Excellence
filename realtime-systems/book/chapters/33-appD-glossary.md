# Glossary {.appendix data-part="APPENDICES"}

| Term | Meaning |
|---|---|
| **Active object** | an object with its own thread and queue that handles one event to completion at a time |
| **Alive / deadline / logical supervision** | three watchdog checks (AUTOSAR): checkpoints at the right rate / right spacing / right order |
| **Atomic** | indivisible: no other flow of control can observe it half-done |
| **Atomicity violation** | code assumed atomic that is interleaved (Lu et al.) |
| **Background / foreground** | the main loop and tasks / interrupt handlers |
| **Backpressure** | a signal or effect that slows a producer because a consumer cannot keep up |
| **Blocking (term B)** | time a task waits for a lower-priority task holding a resource |
| **Budget** | the execution time a component is allowed; a *claim* until measured and defended |
| **Cooperative scheduling** | tasks switch only when they block or yield |
| **Coordinated omission** | measurement that waits for replies and thereby hides the slow ones |
| **Critical instant** | the worst-case release alignment: all higher-priority tasks released together with the task |
| **Critical section** | code that must not be interleaved; often implemented by masking interrupts or a lock |
| **Cyclic executive** | a fixed timetable of calls repeated every major cycle |
| **Data age** | how old a value is when it is used |
| **Deadline** | latest acceptable completion time of a job, relative to its release |
| **Deadlock** | tasks each holding something another needs; none can proceed |
| **EDF** | earliest deadline first: run the ready job with the nearest absolute deadline |
| **Frame (minor cycle)** | the fixed time slot of a cyclic executive |
| **Harmonic periods** | each period is an integer multiple of the shorter ones |
| **High-water mark** | the largest use (or smallest free amount) ever observed |
| **Hyperperiod (major cycle)** | LCM of the periods |
| **Idempotent** | repeating it gives the same result as doing it once |
| **Inheritance (priority)** | a lock holder temporarily takes the priority of the highest-priority waiter |
| **Interrupt latency** | event to first instruction of the handler |
| **ISR** | interrupt service routine |
| **Jitter** | job-to-job variation in release, start or completion time |
| **Job** | one release (instance) of a task |
| **Lifespan (QoS)** | maximum age of a message before it is dropped |
| **Liveliness** | evidence that a publisher is still alive |
| **Minimum inter-arrival** | the shortest time between releases of a sporadic task |
| **Monotonic clock** | a clock that never goes backwards |
| **Mutex** | a lock with an owner; in FreeRTOS, with priority inheritance |
| **Order violation** | two operations assumed in one order with nothing enforcing it |
| **Overrun** | a job exceeding its budget (or period) |
| **Preemption** | a higher-priority task taking the CPU from a lower-priority one at once |
| **Priority ceiling** | a lock's ceiling is the highest priority of its users; holders run at it |
| **Priority inversion** | a high-priority task blocked by a lower-priority one (unbounded if medium tasks intervene) |
| **QoS** | quality of service: delivery guarantees per connection |
| **Rate group** | a set of components run together at one rate (F´) |
| **Rate-monotonic (RM)** | shorter period → higher fixed priority |
| **Release** | the instant a job becomes ready |
| **Response time** | completion minus release, including waiting |
| **Run-to-completion** | a handler finishes before another begins; it never blocks |
| **Sporadic** | released by events, with a minimum inter-arrival time |
| **Stack high-water mark** | minimum free stack ever |
| **Tick** | the kernel's periodic timing interrupt and its unit of time |
| **Time slicing** | equal-priority tasks take turns each tick |
| **Utilization** | C/T for a task; the CPU fraction a set needs |
| **Watchdog** | a timer that resets the system unless software feeds it |
| **WCET** | worst-case execution time: a **safe upper bound** (an observed maximum is not WCET) |
