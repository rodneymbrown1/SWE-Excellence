# Priority inversion and deadlock {.chapter data-part="PART 3 · SHARE"}

<p class="lede">A lock makes data safe by making a task wait. If the one who waits is high priority and the one who holds the lock is low priority, the priorities have been turned upside down — and anything in between can keep the low one from finishing. This is the most famous bug in real-time systems, and it is cheap to prevent once you know its shape.</p>

## The shape

Three tasks: **H** (high), **M** (medium), **L** (low). L takes a lock. H becomes ready, preempts L, and then needs the lock: H blocks, L resumes — and then M becomes ready, preempts L, and runs as long as it likes. H, the most urgent task, waits behind M, which does not even use the lock. The wait is **unbounded**: it lasts as long as M's demand.

::: case
**Mars Pathfinder, July 1997.** (From the flight-software lead's own account, 15 December 1997.) The spacecraft's 1553 bus ran a cycle every 0.125 s. `bc_sched` (highest priority except the OS's own task) set up each cycle; `bc_dist` (third) collected the data; the science tasks, including the weather instrument task `ASI/MET`, were the lowest. `ASI/MET` called `select()`, whose internal bookkeeping took a mutex; it was preempted *while holding it*; `bc_dist` then called `pipeWrite()` and "blocked, taking the mutex"; "several of the medium priority tasks" ran; and when `bc_sched` woke it found `bc_dist` had not finished its cycle, "declared the error that initiated the reset." The spacecraft reset its computer, lost the rest of the day's activities, and recovered.

How it was found: "The software that flies on Mars Pathfinder has several debug features within it … not 'fortuitously' left enabled but remain in the software by design." A trace and log facility, instrumented around the pipe, queue, interrupt and `select` services, recorded into ring buffers. "In less that 18 hours we were able to cause the problem to occur [in the lab]. Once we were able to reproduce the failure the priority inversion problem was obvious." The fix "appeared obvious: change the creation flags for the semaphore so as to enable the priority inheritance" — which was not simple, because the flag was a vendor configuration variable that affected *every* `select` semaphore, so the team analysed and tested the side effects before changing the flight software.

Why it was missed: the problem "would only manifest itself when ASI/MET data was being collected and intermediate tasks were heavily loaded", and testing used "best case" data rates. The team had seen a reset before landing but could not repeat it, and ranked it below entry-and-landing work. Their lesson: "A good lesson when you fly COTS stuff — make sure you know how it works."
:::

## See it

[RAN]{.ran} Lab R3 reproduces the structure on FreeRTOS. Task `met` (L) holds a lock for 10 ms; `bus_dist` (H) needs it; `comms` (M) is CPU-bound for 40 ms; `bc_sched` checks each 50 ms that `bus_dist` finished.

{{fig:gantt-inversion-none | No protocol (simulator): H blocks at 6 ms, M runs from 6 to 46 ms, L finishes its critical section at 53 ms, H completes at 56 ms: a miss (X).}}

{{fig:gantt-inversion-inherit | Priority inheritance: when H blocks, L runs at H's priority, leaves the critical section at 13 ms, H completes at 16 ms.}}

{{fig:gantt-inversion-ceiling | Immediate priority ceiling: L runs at the ceiling priority from the moment it takes the lock; H waits for the CPU, not for the lock.}}

The same experiment on the emulated kernel, from a context-switch trace:

{{fig:trace-inversion-p1 | Real trace, binary semaphore: `comms` runs from 5 to 46 ms while `bus_dist` is blocked; `met` finishes at 53 ms and `bus_dist` at about 60 ms. `bc_sched` (tick at 55 ms) sees it unfinished.}}

{{fig:trace-inversion-p2 | Real trace, mutex with inheritance: `met` finishes its critical section at about 13 ms and `bus_dist` runs at once.}}

| | binary semaphore | mutex |
|---|---|---|
| `bus_dist` first response | **51 ms** (deadline 50): miss | **11 ms** |
| misses in 1 s | **5**, each caught by `bc_sched` as a "reset" | **0** |
| difference in code | `xSemaphoreCreateBinary()` + one `give` | `xSemaphoreCreateMutex()` |

## Protocols that bound the blocking

| Protocol | Rule | Bound on blocking | Costs |
|---|---|---|---|
| **None** | — | unbounded | — |
| **Priority inheritance** | while a task holds a lock that a higher-priority task waits for, it runs at the waiter's priority | at most the length of the critical sections of the lower-priority tasks it can be blocked behind (possibly several in a chain) | can chain; does not prevent deadlock |
| **Priority ceiling** (immediate / original) | a lock has a ceiling = highest priority of any task that uses it; a holder runs at the ceiling | at most **one** critical section of a lower-priority task | needs all users known in advance; prevents deadlock (Sha, Rajkumar, Lehoczky, 1990) |

Sha, Rajkumar and Lehoczky's paper begins: "A direct application of commonly used synchronization primitives such as semaphores, monitors, or the Ada rendezvous can lead to uncontrolled priority inversion, a situation in which a higher priority job is blocked by lower priority jobs for an indefinite period of time", and shows both protocols solve it; the ceiling protocol "reduces the worst case task blocking time to at most the duration of execution of a single critical section of a lower priority task" and "prevents the formation of deadlocks."

In FreeRTOS, "mutexes include a basic 'priority inheritance' mechanism, whereas binary semaphores do not." The same book cautions: inheritance "does not 'fix' priority inversion, but merely lessens its impact by ensuring that the inversion is always time bounded", it "complicates system timing analysis, and it is not good practice to rely on it for correct system operation." OSEK/AUTOSAR resources use the (immediate) ceiling protocol.

**The blocking term.** In the response-time equation (chapter 9), B for a task is the longest critical section of any *lower*-priority task on a lock whose users include a task of priority at or above it. Making critical sections short is therefore the most effective way to shrink every higher-priority task's response time.

## Look at it with a debugger

[RAN]{.ran} Lab R9 stops a gdb session the instant the checker declares the first reset and prints the kernel's lists with the helper `fr-tasks`:

```
task         state                      prio  notes
bc_sched     RUNNING                       6
bus_dist     suspended/blocked-forever     5  blocked on queue/semaphore @0x20000ff0
met          ready                         3
--- the lock (a binary semaphore): who owns it? ---
(no owner: counting/binary semaphores and queues are not owned by anyone)
```

A binary semaphore has **no owner**, so the kernel cannot know whom to boost. In phase 2 (a mutex), stopping at `xTaskPriorityInherit` and listing again shows `met  ready  5  <-- priority 5 inherited (base 3)` and `mutex holder = met`.

## Deadlock

Two or more tasks each hold something the other needs. The four conditions (Coffman et al. 1971, as presented in OSTEP): mutual exclusion, hold-and-wait, no preemption, circular wait. Lu et al. found that **97%** of the deadlocks in their sample involved **two threads** waiting on **at most two resources**, and **22%** were a single thread acquiring a lock it already held.

| Defence | How |
|---|---|
| **Lock order** | one global order for taking locks; review pairs of locks |
| **No blocking while holding** | never call a function that can block (queue, delay, print) inside a critical section |
| **Timeouts** | `xSemaphoreTake(m, ticks)` with a finite timeout and a defined reaction |
| **Recursive mutex** | only if re-entry is intended; otherwise a self-deadlock is a bug you want to *find* |
| **Ceiling protocol** | prevents the circular wait by construction |

::: trap
**Trap: a library call that locks.** Pathfinder's lock lived inside the operating system's `select()`. Any call into a library, a driver, a logging framework or the standard I/O can take a lock. For every such call from a high-priority task ask: *what does it lock, and who else holds that lock at lower priority?*
:::

::: rule
**Rule.** Use a **mutex** (with inheritance) for mutual exclusion, never a binary semaphore. Keep critical sections short and free of blocking calls. Never take a mutex in an interrupt. List every lock with its users' priorities.
:::

## Check yourself

::: check
1. Draw a three-task inversion on paper using any numbers. How long is H blocked with no protocol? With inheritance?
2. In your system, find a lock used by tasks of different priorities. Is it a mutex? What is the longest time it is ever held?
3. Task A takes lock X then Y; task B takes Y then X. What happens, and what is the cheapest rule that prevents it?
:::

**Lab links.** H3 demo 4, R3, R9.
