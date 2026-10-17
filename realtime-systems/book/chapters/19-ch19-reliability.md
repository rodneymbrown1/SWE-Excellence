# Reliability: watchdogs, containment and recovery {.chapter data-part="PART 5 · TRUST"}

<p class="lede">Every component will eventually stop, hang, corrupt something, or run forever. Reliability is the decision, made in advance, about who notices, what is done, how far the damage spreads, and how the system gets back.</p>

## Five decisions per failure

| Decision | Question | Typical answers |
|---|---|---|
| **Detect** | who notices, and how fast? | watchdog, deadline monitor, heartbeat, assertion, fault handler |
| **React** | what happens first? | log, degrade, restart the component, reset the system, enter a safe state |
| **Contain** | how far can the damage reach? | separate memory, separate processes, bounded queues, rate limits |
| **Recover** | how does it come back? | warm restart with saved state, cold restart, redundant unit takes over |
| **Evidence** | what is left for the engineer? | reset reason, saved registers and task states, trace tail, counters |

A system that has answered "detect" but not "react" has a good alarm and no fire brigade.

## What can go wrong, and what notices it

| Failure | Looks like | Noticed by |
|---|---|---|
| **Crash** (fault, assert) | processor halts or resets | fault handler, hardware reset |
| **Hang** (infinite loop, deadlock, task blocked forever) | the system runs, one function is dead | **per-task** supervision; queue age; heartbeat |
| **Starvation** (higher priority never yields) | low-priority work never runs | a low-priority heartbeat that stops |
| **Slow** (overrun) | deadline missed | deadline monitor (chapter 11) |
| **Corruption** (stack overflow, race, wild pointer) | wrong values, later crash | invariants, canaries, MPU, checksums |
| **Babbling** (floods a bus or queue) | everyone else is slowed | rate limits, bounded queues |
| **Silence** (a monitor that fails to monitor) | nothing alarms | a monitor of the monitor |

## The watchdog, three designs

A **watchdog timer** is a counter that resets the processor if software does not reload ("feed", "kick", "tickle") it in time. It exists to turn any software hang into a reset. Its quality depends entirely on **what must be true before software feeds it**.

{{fig:watchdog-designs | Three ways to feed a watchdog and what each can detect. Only the third notices a single dead task.}}

[RAN]{.ran} Lab R5 injects one fault into a three-task system (the `control` task blocks forever on a lock after 15 cycles) and runs each design:

| Design | Watchdog fed by | Outcome in 1.5 s |
|---|---|---|
| **1** | the timer interrupt | 150 feeds; `control` stopped at cycle 15 (~300 ms); **no reset, nothing noticed** |
| **2** | a lowest-priority task | 9 feeds; `control` dead; **no reset, nothing noticed** (the feeder still gets CPU) |
| **3** | a supervisor, only if *all* tasks checked in since the last feed | **reset at tick 700**; the next boot read `.noinit` and printed *"tasks that had NOT checked in: control"* |

This matches what the sources warn about.

- Memfault's article demonstrates design 2 failing: "a high priority thread is suspended waiting for a mutex" while "our low priority thread will be scheduled to run by the RTOS and can keep feeding the watchdog"; the fix is "an API tasks can register with" so the hardware watchdog is fed "only if all tasks have recently checked in".
- Ganssle's long-standing advice: "Build a watchdog that monitors the entire system's operation. Don't assume that things are fine just because some loop or ISR runs often enough to tickle the watchdog timer." and "It's fun to watch a multitasking product crash — the entire system might be hung, but one task still responds to interrupts." The watchdog should "leave breadcrumbs behind, generating debug information for the developers", and software "should [not] be able to reprogram the WDT".
- Koopman's slides (for the plaintiffs in the Toyota litigation) list the same checks: kicking from a timer interrupt "usually a bad sign"; "any single task death must inhibit watchdog kick"; and, as testified for the throttle controller, "watchdog kicked by a hardware timer service routine" with the watchdog detecting the death of the 1 ms task but "not others". [SEC]{.sec}
- AUTOSAR's Watchdog Manager names three kinds of supervision: **alive** (checkpoints arrive at the right frequency), **deadline** (the time between two checkpoints is in range) and **logical** (checkpoints occur in the right order).

::: rule
**Rule.** A watchdog is fed only by code that has *verified* progress of every function you care about. Feed from one place, in a task, never from an interrupt. Use a windowed watchdog if you have one (too early is also an error). Before the reset happens, save *who* was missing.
:::

::: trap
**Trap: the debugger and the watchdog.** Many microcontrollers freeze the watchdog while the CPU is halted at a breakpoint; some do not. A watchdog that resets mid-debugging, or one that quietly stops, changes what you observe (Memfault; Ganssle suggests a jumper that disables only the *reset*, not the watchdog logic, so the circuit is still exercised).
:::

## Containment: how far does a failure spread?

::: case
**Ariane 5, flight 501, 4 June 1996.** The Inquiry Board found the immediate cause in the inertial reference system software, reused from Ariane 4: a conversion of a 64-bit floating-point value to a 16-bit signed integer overflowed. The conversion "was not protected", and "the system specification stated that: the failure should be indicated on the databus, the failure context should be stored in an EEPROM memory …, and finally, the SRI processor should be shut down." "It was the decision to cease the processor operation which finally proved fatal." The board adds: "the reason behind this drastic action lies in the culture within the Ariane programme of only addressing random hardware failures." Both units ran **identical hardware and software**, so both failed the same way: redundancy protected against random hardware faults and not against a *systematic* software fault. The function that failed was an alignment routine, "operative for 50 seconds after starting of the Flight Mode", not required for Ariane 5.
**Lessons.** (1) *What the code does on an exception is a design decision with system-level consequences* — halt, reset, saturate, or carry on? (2) Replicas of the same software share the same bugs. (3) Reused code carries the assumptions of its original envelope.
:::

Containment tools, from cheapest to strongest:

| Tool | Contains | Cost |
|---|---|---|
| bounded queues and rate limits | floods | a drop policy (chapter 15) |
| ownership + copy at boundaries | corruption through shared data | a copy |
| memory protection (MPU) between tasks | wild writes | configuration effort, regions |
| separate processes or cores | crashes | communication overhead |
| separate processors or power domains | everything but the interface | hardware |

## Recovery by design: Pathfinder

::: case
**Pathfinder (1997), the recovery that worked.** "We knew that if this problem occurred we would reset. We built in mechanisms to recover the current activity so that there would be no interruptions in the science data … We built in the ability (and tested it) to go through multiple resets while we were going through the Martian atmosphere." The detector was a deadline check between two tasks; the reaction a reset; the recovery state-in-RAM and a designed re-entry. "We had our priorities right" — the team could rank an unreproduced inversion below landing software *because* the failure had a safe, rehearsed outcome. Compare Clementine (1994), described in Ganssle's article: a software hang fired thrusters, and a software timeout on the thrusters "failed when the firmware hung".
:::

::: case
**Ingenuity, April 2021: a protection that blocked flight.** The helicopter's first high-speed spin attempt did not reach the flight state; the team traced it to "a computer protection and reliability feature" (the watchdog) and fixed it with a flight-controller software update. A watchdog or monitor that is too strict is also a failure mode: it must be part of the test plan.
:::

## Evidence for the engineer on call

| Item | How | Lab |
|---|---|---|
| **Reset reason** | read the reset-cause register at boot (Memfault: `RESETREAS` on nRF52) | R5 (`.noinit` marker) |
| **Who was missing** | save the check-in mask before resetting | R5 |
| **Trace tail** | ring buffer survives in RAM; dump after reset | R3, R8 |
| **Fault registers** | stacked PC, LR, status registers in the fault handler | `startup.c` prints them |
| **Counters** | drops, overruns, restarts, uptime | R10 |

Pathfinder's team could reproduce the bug in under 18 hours *because the trace was already in the flight software*. The debugging-project book (*State First*) is the companion for what to do with such evidence.

## A reliability review in one table

| Failure to survive | Detector | Reaction | Blast radius | Recovery | Evidence kept |
|---|---|---|---|---|---|
| task hangs | | | | | |
| queue overflows | | | | | |
| stack overflows | | | | | |
| sensor goes silent | | | | | |
| watchdog fires repeatedly | | | | | |
| restart fails every time | | | | | |

If a cell is blank, that is an unmade decision, and it will be made by accident.

## Check yourself

::: check
1. In your system, who feeds the watchdog, from where, and under what condition? What failure would not stop it being fed?
2. A component fails at start-up every time. What does the system do after the third reset?
3. Which of your replicated components share code? What failure would take out both?
:::

**Lab links.** R5 (watchdog designs), R3 (a deadline monitor), R9 (reading state after the fact).
