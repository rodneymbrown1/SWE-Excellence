# Debug triage: symptom to first probe {.chapter data-part="PART 3 · DEBUG"}

<p class="lede">On a device the debugger is a blunt instrument: stopping the CPU changes the timing you are investigating. Start from the symptom, name the likely class of cause, and pick the probe that observes without disturbing. The method is the one in <em>State First</em>: state the data and conditions, predict, then probe.</p>

{{fig:triage | One row per symptom: the first suspicion and the first probe. Details for each follow.}}

## The rules of probing on a real-time system

| Rule | Reason |
|---|---|
| **Predict before you probe**: write the number you expect | a probe without a prediction teaches nothing |
| **Counters and traces before breakpoints** | a stop costs time (in our emulator about 1 ms each) and may pause watchdogs |
| **One change at a time**, same test, same load | timing bugs move when you touch them |
| **Reproduce first** (make it deterministic if you can: fixed load, emulator with instruction counting) | a bug you cannot repeat you cannot fix |
| **Look at the tail**, not the average | requirements are worst-case |
| **Keep the evidence** (trace, counters, build id) | the next person needs it |

## Playbooks

### A · A deadline is missed, or jitter is high
1. Which task, which job, by how much? (histogram of response time; count releases vs completions)
2. Trace the window around the worst job: who ran, who was blocked on what, which interrupts fired.
3. Compare with the **budget**: is C larger than claimed (slow path)? Is something higher-priority running longer (a logger, a timer callback)? Is it **blocked** on a lock held by a lower-priority task (inversion)?
4. Fix class: shorten the slow path; move work down in priority; bound or shorten critical sections; use a mutex with inheritance; add margin. Re-measure.

### B · The system is alive but one function is dead
1. List tasks with state and what each waits on (`fr-tasks`, framework task list).
2. A task "blocked forever" on a lock or queue is the usual cause. Who holds the lock? Is the producer alive? (A binary semaphore has no owner: look at who *should* have given it.)
3. Check the watchdog design: would it notice this? (book ch. 19)

### C · Resets or a boot loop
1. Read the **reset reason**. Watchdog, brown-out, fault, software?
2. Read the saved evidence (`.noinit` marker, check-in mask, trace tail, fault registers: stacked PC/LR).
3. If it resets at start-up every time: what grows with time in service (files, logs, counters)? Is a resource consumed at boot? (Spirit)
4. Make the evidence persist before the reset in the next build.

### D · Wrong or inconsistent values
1. State an **invariant** the data should satisfy (field and complement; sequence read twice; checksum).
2. Count violations; correlate with other activity (which task or interrupt runs at that instant?).
3. Put a **hardware watchpoint** on the variable (condition on the bad state); on a hit, inspect which task is running and the call stack.
4. Fix class: snapshot, ownership, critical section; never `volatile` alone.

### E · Messages missing, late or duplicated
1. Counters at each hop: produced, enqueued, dropped, dequeued, processed.
2. Queue depth high-water; oldest-item age. Is the consumer starved or blocked?
3. Check start-up order: did the producer run before the consumer existed?
4. Check QoS (reliable? depth? lifespan?) and timestamps (assigned where?).

### F · Gets worse over hours or days
1. Heap: minimum-ever-free and largest free block over time. Stack high-water marks. Queue depths.
2. Counter widths and wrap times (tick, µs timers, sequence numbers). Uptime arithmetic.
3. Clock drift: anything multiplied by uptime? (Patriot)
4. Logs, files, caches that grow.

### G · Works in the debugger or debug build, fails in release (or the reverse)
1. Timing changed: compare optimisation levels and the cost of logging. Is the failure a race?
2. Uninitialised variables (locals are *undefined*), stack sizes differing, `volatile` missing.
3. Observe with traces and counters in **both** builds.

### H · CPU load is too high
1. Per-task CPU share (run-time stats); interrupts' share; idle share.
2. Look for a spin (a task that never blocks), a timer callback that is long, a logger at high priority, a retry storm.
3. Re-run the budget (§4) with measured C.

## Using gdb without wrecking the timing

| Goal | Recipe (see §9) |
|---|---|
| log without stopping | `break FUNC if cond` + `silent` + `printf` + `continue`, **only on rarely-called functions** |
| stop on a bad state | `watch VAR if VAR == BAD` (hardware watchpoint) |
| see all tasks | helper `fr-tasks` (source `labs/rtos/gdb/freertos.py`) |
| find who runs | `fr-tick`; `print pxCurrentTCB->pcTaskName` |
| understand a lock | `fr-queue LOCK` (owner? waiters?) |

**The debugger is not neutral.** In our emulator two silent breakpoint stops moved the clock by about 2 ms, and a breakpoint on a function called in the first cycle made the first deadline miss disappear. On hardware, timers keep running while halted and some watchdogs stop.
