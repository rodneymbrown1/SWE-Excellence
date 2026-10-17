# Code-review checklist for RTOS changes {.chapter data-part="PART 5 · REVIEW"}

<p class="lede">What to look at in a diff that touches tasks, interrupts, queues, locks or timing. Each item is a failure that has happened. Review the diff against the Component Card, not against taste.</p>

## Interrupts and timing

| ☐ | Check |
|---|---|
| ☐ | New or changed ISR: only ISR-safe calls; no blocking; no locks; no print; short (state its worst case). |
| ☐ | Anything done with interrupts disabled: how many microseconds? Any loop in it? |
| ☐ | A delay or timeout: absolute time for periods; difference compare for wrap; `last` initialised correctly. |
| ☐ | A busy-wait or `for(;;)` without a blocking call. |
| ☐ | Anything that takes a variable time (float, division, search, printf, flash/EEPROM write) in a high-priority path. |
| ☐ | A timer callback: does it block or take long? |

## Tasks and priorities

| ☐ | Check |
|---|---|
| ☐ | New task: stack size justified (high-water mark), priority justified (rule), name set, created in the right order. |
| ☐ | Changed priority: re-ran the budget? Any equal-priority neighbours? |
| ☐ | Task deletion: who frees what; is the idle task able to run? |
| ☐ | Anything added to a **high-priority** task's loop: new budget. |

## Messaging

| ☐ | Check |
|---|---|
| ☐ | New queue: depth from burst, policy, drop counter, owner of the message memory. |
| ☐ | A send or receive with `portMAX_DELAY`: what if it never comes? |
| ☐ | A message without a timestamp, or stamped late. |
| ☐ | Producer enabled before the consumer exists. |
| ☐ | QoS changed: still compatible with every subscriber? |

## Synchronization

| ☐ | Check |
|---|---|
| ☐ | New shared variable: owner, protection, hold time; invariant for tearing. |
| ☐ | A lock: mutex (not binary semaphore)? Order consistent? Held across a blocking call? Taken in an ISR? |
| ☐ | A call into a driver/library from a high-priority task: does it lock? |
| ☐ | `volatile` offered as the fix. (It is not.) |

## Memory and reliability

| ☐ | Check |
|---|---|
| ☐ | New allocation: after init? failure handled? freed? bounded? |
| ☐ | New large local array or recursion: stack effect. |
| ☐ | New log/file/cache that grows. |
| ☐ | A new failure path: what detects it, what reacts, what evidence is kept? |
| ☐ | Watchdog feeding changed: still conditioned on progress of every task? |

## Observability

| ☐ | Check |
|---|---|
| ☐ | Does the change add a counter or trace point where it adds risk? |
| ☐ | Evidence attached: before/after histogram or trace, not an average. |
| ☐ | The observed maximum is not described as WCET. |
