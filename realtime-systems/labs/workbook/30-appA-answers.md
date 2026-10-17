# Answer key {.appendix data-part="APPENDICES"}

Answers to the *Predict first* questions and selected *Questions*. Read after you have run the lab.

## H1
**Predict.** (a) Period ≈ work + sleep = 12 ms plus wake-up lateness; drift grows linearly (here 1,239 ms over 300). (b) Period = 10 ms; drift ≈ 0. (c) The absolute version loses time **only** on the slow iteration and recovers (its next start is late, then it catches up); the relative version never recovers. **Q4.** With an interval of more than half the range the difference changes sign. **Q5.** `(int16_t)(now − deadline) >= 0` with 16-bit unsigned operands. **Q6.** To stay under 1 ms of drift after 100 hours (3.6×10⁶ ticks) the per-tick error must be below 2.8×10⁻¹⁰ s: about 32 fractional bits.

## H2
**Predict.** (a) Frame 0 has 10 − (2+3+4) = 1 ms; frame 2 has 5 ms. (b) Frame 9 starts 1 ms late (A at 91 ms), and frame 11 starts 1 ms late. (c) C is skipped in frame 8; frame 9 is still 1 ms late.

## H3
**Demo 1.** U = 0.833 > 0.780; schedulable (R₃ = 10). **Demo 2.** U = 0.971; RM misses t2 (R = 8 > 7), EDF does not. **Demo 3.** t2 misses, not t4. **3b.** FP completes 15, 10, 0; EDF 12, 8, 4. **Demo 4.** None: H completes at 56 (deadline 55); inheritance: 16; ceiling: 16 (H waits for the CPU, not the lock).

## H4
**Predict.** (a) 1,100/s. (b) ⌈(1,100 − 200) × 0.020⌉ + 1 = 19. (c) 19 × 5 ms = 95 ms. **Q1.** At 18, 8 messages are lost over 10 s (about 0.8 per second): one per burst. **Q3.** (pool size) ÷ (deficit per period).

## H5
**Predict.** Closed loop p99 ≈ 1.4 ms (1 slow request of 5,501); open loop p99 ≈ 4.5 s (558 of 6,000 above 100 ms). The open loop is what a user would see.

## R0
**Predict.** (a) A then B (round robin among equals). (b) 39 µs. (c) The reaper prints "done" and ends the run. **Q4.** With time slicing off, equal-priority tasks run until they block.

## R1
**Predict.** (a) 12,999 µs mean; drift ≈ +297 ms. (b) 9,998 µs; ≈ −0.15 ms. (c) 24 µs to 999 µs.

## R2
**Predict.** (a) 1, 3, 10 ms. (b) t2 misses (R = 8 > 7). (c) 20% in the simulator; (d) the real kernel misses 80%. **Q1.** Kernel overhead (tick, switches). **Q2.** The three jobs that finish at exactly 7 ms on paper finish 80–170 µs late on the target.

## R3
**Predict.** (a) 51 ms; misses. (b) 5. (c) 0. **Q1.** From about 6 to 53 ms; `comms` ran. **Q3.** `xSemaphoreCreateBinary` → `xSemaphoreCreateMutex` (inheritance).

## R4
**Predict.** 19 slots. At depth 4, about 75 drops in 5 s. `drop_oldest` changes the *latency* (20 vs 24 ms at depth 4), not the number of drops.

## R5
**Predict.** Mode 1: no reset; mode 2: no reset; mode 3: reset at tick 700, and the next boot names `control`. **Q1.** Mode 2's feeder was fed only 9 times because the supervisor period (150 ms) feeds at that rate; mode 1's feeds come from the interrupt regardless of tasks.

## R6
**Predict.** (a) No. (b) 25,888 free but the largest block is 5,728. (c) No; it reports at the next context switch. **Q2.** 720 of 2,048 bytes were overwritten.

## R7
**Predict.** (a) Yes. (b) 0 iterations (naive); 100 (safe). **Q2.** 49.7 days; 4.97 days. **Q3.** A signed 32-bit count of 10 ms ticks is consistent with 248.55 days (an inference; the directive does not give the width).

## R8
**Predict.** (a) 10,000 µs without, 11,500 µs with. (b) 25%, 33%, 25% of the CPU, plus 12.5% from the interrupt. (c) The measurement (11.6 ms) matches the "with" prediction. **Q1.** 14%. **Q2.** Interrupt time is charged to the task that was interrupted.

## R9
**Predict.** About 1 ms per stop (1,982 µs for two). **Q4.** A binary semaphore records no holder. **Q5.** `met`: priority 5, base 3. **Q6.** The logpoint/watchpoint stops in the first cycle shifted time; investigate timing with traces and counters.

## R10
The four problems: (1) the logger at priority 6; (2) a raw queue of depth 4 with no visible counter; (3) the filter publishes a struct that control reads twice, 150 µs apart; (4) the 6 ms recalibration inside the high-priority filter. Reveal counters at baseline: `dropped_raw` 54, `torn` 47, `ctrl_late` 61, `isr_late` 0. After the four patches: 0, 0, 0, p99.9 = 631 µs.
