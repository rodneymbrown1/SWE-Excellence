# Quick reference {.chapter data-part="PART 6 · REFERENCE"}

<p class="lede">The numbers and mappings you reach for twice a day. Full tables: book Appendices B and C.</p>

## Formulas

| What | Formula |
|---|---|
| Utilization | U = Σ C/T (include interrupts) |
| RM guarantee | U ≤ n(2^(1/n) − 1): 1.00, 0.83, 0.78, 0.76, 0.74, 0.72 … 0.69 |
| Harmonic periods | RM schedulable to U = 1 |
| Response time | R = C + B + Σ_hp ⌈(R + J)/T⌉ · C; schedulable if R ≤ D |
| Queue depth | ⌈(peak rate − service rate) × burst⌉ + 1 |
| Worst latency in a full queue | depth × service time |
| Counter wrap | 2^bits ÷ rate: 32-bit tick @1 kHz = 49.7 days; 16-bit = 65.5 s; 32-bit @25 MHz = 171.8 s |
| Clock drift | ppm × 10⁻⁶ × elapsed: 50 ppm ≈ 4.3 s/day |
| Time compare | `(int32_t)(now − then) >= 0` |
| Data age (loose) | Σ (T_i + R_i) |
| Clean test of N trials | failure probability < ~3/N at 95% confidence |

## Where each thing is called in FreeRTOS

| | FreeRTOS | ISR variant |
|---|---|---|
| periodic wait | `xTaskDelayUntil` | — |
| queue | `xQueueSend/Receive` | `…FromISR` |
| mutex | `xSemaphoreTake/Give` on a mutex | **none** |
| binary semaphore (signal) | `xSemaphoreTake/Give` | `xSemaphoreGiveFromISR` |
| notification | `xTaskNotifyGive` | `vTaskNotifyGiveFromISR` |
| critical section | `taskENTER_CRITICAL` | `taskENTER_CRITICAL_FROM_ISR` |

## Same idea, other names

| Idea | FreeRTOS | Zephyr | F´ | cFS | ROS 2 |
|---|---|---|---|---|---|
| task | task | thread | active component | app task | executor thread |
| periodic activation | `DelayUntil`, timer | `k_timer` | rate group | scheduler table slot | timer in executor |
| queue | queue | message queue | async port queue | SB pipe | subscription queue |
| lock | mutex (inherit) | `k_mutex` (inherit) | guarded port | OS mutex | callback group / lock |
| lifecycle | — | — | topology | ES start/stop | managed node |

*(cFS and Zephyr entries: verify in your build's documentation.)*

## Watchdog designs

☒ fed from the timer ISR  ·  ☒ fed from a low-priority task  ·  ☑ fed by a supervisor only if every task checked in since the last feed (and windowed, if the hardware allows).

## Honest limits of this handbook

All lab numbers are from an emulator with a deterministic clock and one FreeRTOS version (V11.3.2); they demonstrate relationships, not your board's speed. Items marked [SEC]{.sec} are expert testimony or press reports. `research/09-claims-we-could-not-verify.md` lists everything unconfirmed.
