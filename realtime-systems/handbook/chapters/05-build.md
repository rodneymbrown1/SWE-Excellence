# Build checklist: before you merge a component {.chapter data-part="PART 2 · BUILD"}

<p class="lede">Twenty-six checks, grouped by the six questions. Each takes a minute if you filled in the card and budget; each is a gap that has caused a real failure if you did not. Tick, or write the owner who will answer.</p>

## 1 · Timing

☐ T1 Trigger, period/min gap, deadline and budget written on the card.
☐ T2 Budget is an **upper bound** with margin, and says how it was obtained.
☐ T3 Miss policy defined (what happens to the *next* release).
☐ T4 Every periodic wait uses an **absolute** time (`DelayUntil`), initialised correctly (not in the future).
☐ T5 All counters/timeouts are compared by **difference**; wrap times known (tick, µs timer).
☐ T6 Interrupts and tick are in the budget.

## 2 · Scheduling

☐ S1 Priority follows the rate/deadline rule, or the exception is documented.
☐ S2 The task **blocks** somewhere (no polling spin); nothing blocks without a timeout.
☐ S3 Timer callbacks do no blocking and take microseconds.
☐ S4 Response time R ≤ D with slack, computed or measured.

## 3 · Messaging

☐ M1 Every queue: depth justified from a burst; overflow policy named; **drop counter exists and is read**.
☐ M2 Every message carries a **source timestamp** and, if order matters, a sequence number.
☐ M3 Age limit defined and checked at the consumer.
☐ M4 Start-up order: consumers exist and are ready before producers run.
☐ M5 QoS (if any) written down per subscription.

## 4 · Synchronization

☐ Y1 Every shared datum: owner, protection, longest hold (card).
☐ Y2 Multi-field data read as one snapshot (or passed by value); invariant to detect tearing.
☐ Y3 Mutex (with inheritance) for exclusion; no binary semaphore as a lock.
☐ Y4 No blocking call while holding a lock; lock order documented.
☐ Y5 Interrupt handlers use only ISR-safe calls and no locks.

## 5 · Reliability

☐ R1 If the component hangs: who notices (check-in, deadline monitor), how fast, what happens.
☐ R2 Stack sized from a measured high-water mark with margin; overflow detection on.
☐ R3 No allocation after initialization (or failure handled and bounded).
☐ R4 Restart behaviour defined (state, repeated failure, boot loop).
☐ R5 Evidence survives a reset (reset reason, who was missing).

## 6 · Observability

☐ O1 Each requirement has a metric, a method and a margin written down.
☐ O2 Latency reported as a histogram; open-loop; p99.9 and max.
☐ O3 Releases, completions and misses counted separately.
☐ O4 A trace hook or ring buffer exists and can be dumped on error.

## Sign-off

Reviewer ____________  date ______  open `?` items: ______  **Merge only when every box is ticked or has an owner and a date.**
