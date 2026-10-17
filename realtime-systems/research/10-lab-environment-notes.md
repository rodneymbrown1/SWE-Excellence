# 10 · Lab environment notes — what was actually run

Everything marked **[RAN]** in the book, handbook and workbook was executed on the machine below, and its output is saved in `labs/transcripts/`. Regenerate with `sh labs/host_capture.sh`, `sh labs/rtos/capture.sh`, `sh labs/rtos/gdb/run_session.sh`.

| Item | Version |
|---|---|
| Machine | Apple Silicon Mac (Darwin 24.3.0, arm64) |
| Host C compiler | Apple clang 17.0.0 |
| Python | 3.12.0 (standard library only) |
| Cross compiler | `arm-none-eabi-gcc` 16.2.0 (Homebrew; **no newlib/libc** — the lab BSP is freestanding) |
| Debugger | `arm-none-eabi-gdb` 18.1 (Python 3.15 embedded) |
| Emulator | QEMU 11.1.2, machine `mps2-an385` (Cortex-M3, 25 MHz system clock) |
| RTOS | FreeRTOS-Kernel **V11.3.2**, commit `640d0c43705e64cd53f46b31d882de6cd8433933` (ARM_CM3 port, `heap_4`) |
| Install side effect | `brew install qemu arm-none-eabi-gcc arm-none-eabi-gdb` also installed Python 3.15 as a dependency |

## How timing works in the RTOS labs (important for reading the numbers)

- QEMU is run with `-icount shift=5,sleep=off`: **virtual time advances with the number of instructions executed** (1 instruction = 2⁵ = 32 ns of virtual time) and idle time is skipped. Consequence: **output is bit-identical from run to run** (checked: two further R2 runs produced byte-identical output, same MD5) and runs finish quickly.
- All "microseconds" in the RTOS labs are *virtual* microseconds read from the emulated 25 MHz hardware timer (TIMER0). **They are not claims about any real board.** The point of the labs is the *method* and the *relationships* (model vs measurement, with vs without a protocol), not the absolute values.
- `burn_us(n)` consumes `n` µs of *CPU time* (a calibrated instruction loop), so a preempted task takes longer in wall time — as a real task would. Calibration is checked by lab R1: `work 3000 µs + vTaskDelay(10 ms)` measures 13,000 µs per period.
- The QEMU Cortex-M3 model's DWT cycle counter was **not** used or tested; labs use TIMER0. On real boards use DWT/CYCCNT.
- `-icount` is switched off with `run.py --real` (host-time mode). That mode was not used for any transcript.

## Findings from the lab work that changed the documents

1. **Model vs measurement (R2).** For C = (1, 2, 3) ms, T = (4, 6, 12) ms the response-time analysis predicts R = (1, 3, 10) ms; measured worst cases: **1.006, 3.024, 10.087 ms** (excluding job 0). The second set (U = 0.971) has three of five jobs per hyperperiod finishing at *exactly* their deadline on paper; the real kernel finished them 80–170 µs late, so the measured miss rate was **80% against the simulator's 20%**. → "zero slack on paper is negative slack on target"; add an overhead term.
2. **The first job is special (R2).** Job 0 also paid for task creation (~230 µs); its response time was excluded from statistics. A zero-length-job test measured steady-state wake-up overhead of **4–24 µs**.
3. **Interrupts must be in the analysis (R8).** With a 250 µs interrupt every 2 ms: measured worst responses **1.26 / 3.53 / 11.62 ms**; RTA *with* the interrupt as a top-priority task: 1.25 / 3.50 / 11.50 ms (error ≤ 1%); RTA *without*: 1.00 / 3.00 / 10.00 ms (up to 14% low).
4. **Queue sizing rule validated three ways (H4, R4).** Formula `ceil((peak − service) × burst) + 1` = 19 slots; the host simulation and the FreeRTOS run both show **0 drops at 19 and drops at 18**.
5. **`vTaskDelayUntil` with a `last` value in the future does not block** (found as a bug in our own R3 first draft: a task spun at priority 6 and starved everything below it). Documented as an edge case in the book (ch. 6) and handbook checklist.
6. **Observer effect (R9).** Two silent breakpoint stops moved the program's virtual time forward by **1,982 µs** (≈ 1 ms per stop; mechanism not investigated) and, in R3, a breakpoint on a function called by the scenario's first cycle made the first deadline miss *disappear* (first reset at tick 257 instead of 55). On real hardware the effect differs (timers keep running while halted; some MCUs pause watchdogs). The documents state the measurement, not a mechanism.
7. **Stack overflow detection is late (R6).** The check (`configCHECK_FOR_STACK_OVERFLOW = 2`) ran only at the next context switch; by then **720 of 2,048 bytes** of the neighbouring heap block had been overwritten.
8. **`xTaskCatchUpTicks()` must not be called with the scheduler suspended** (it asserts); used in R7 to fast-forward a 16-bit tick to just before its wrap. Naive `now >= deadline` expired immediately (0 loop iterations, 2 µs) across the wrap; the safe comparison ran the full 100 ticks.
9. **Watchdog designs (R5).** Feeding from the timer ISR (mode 1) and from a low-priority task (mode 2) never noticed a task blocked forever; the task-check-in design (mode 3) reset at tick 700 and the next boot read `.noinit` diagnostics naming the missing task (`control`). The watchdog is *emulated* with TIMER1 (the QEMU model has no vendor watchdog used here) and the reset is a real `SYSRESETREQ`.
10. **Capstone (R10).** Baseline: mean latency 715 µs ("looks fine") but p99.9 = 9.5 ms; hidden counters: 54 silent drops, 47 torn reads, 61 late control cycles. Patches 1–3 fix drops/torn reads but p99.9 stays 6.5 ms because a 6 ms recalibration runs inside the high-priority filter; patch 4 moves it to a low-priority task → p99.9 = 0.63 ms, zero drops/torn/late.
11. **Host timing is machine-specific (H1).** On this Mac `nanosleep` woke about 1.6 ms late (median start lateness 1,612 µs) and the "relative sleep" version drifted by 1.2 s over 300 iterations. Host transcripts are *samples*, not expected values.

## Not run

- Real hardware; OpenOCD; SEGGER/Percepio tools; VS Code debugging (`launch.json.example` is **[MANUAL]**); FreeRTOS POSIX/Linux simulator port; Zephyr; Docker.
