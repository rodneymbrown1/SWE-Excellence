# Formulas and numbers to keep {.appendix data-part="APPENDICES"}

## Time and clocks

| Quantity | Formula | Example |
|---|---|---|
| Counter wrap time | 2^bits ÷ clock | 2³² ÷ 25 MHz = 171.8 s; 2³² ÷ 1 MHz = 71.6 min |
| Tick wrap time | 2^bits ÷ tick rate | 16-bit @1 kHz: 65.5 s; 32-bit @1 kHz: 49.7 days |
| Drift from oscillator error | error (ppm) × 10⁻⁶ × elapsed | 50 ppm × 86,400 s = 4.3 s/day |
| Two clocks | sum of both errors | 2 × 50 ppm = 100 ppm = 8.6 s/day |
| Safe time comparison | `(int32_t)(now − then) >= 0` | valid for intervals < 2³¹ ticks |
| Sleep error per iteration | work time, if relative | accumulates linearly (lab H1) |

## Utilization and schedulability

| Quantity | Formula |
|---|---|
| Utilization of a task / set | U = C/T;  U = Σ C_i/T_i (include interrupts) |
| RM guarantee (Liu–Layland) | U ≤ n(2^(1/n) − 1) → 1.000, 0.828, 0.780, 0.757, 0.743, 0.718, … 0.693 |
| Harmonic periods | RM schedulable up to U = 1 |
| EDF (deadline = period) | schedulable iff U ≤ 1 |
| Hyperperiod | LCM of periods |
| **Response time** (fixed priority) | R = C + B + Σ_hp ⌈(R + J_j)/T_j⌉ · C_j, iterate from R = C + B |
| Schedulable | R ≤ D for every task |
| Slack | D − R |
| Overload rescaling under EDF | average period T_i × U (when U > 1) |

## Queues

| Quantity | Formula |
|---|---|
| Queue depth for a burst | ⌈(peak rate − service rate) × burst duration⌉ + 1 |
| Time to drain | backlog ÷ (service rate − arrival rate) |
| Worst latency in a full queue | depth × service time |
| Little's law (averages) | L = λ · W |

## End-to-end

| Quantity | Formula |
|---|---|
| Loose data-age bound, register-based chain | Σ (T_i + R_i) over stages |
| Control rate rule of thumb | ω_c · h = 0.2 – 0.6 (Åström–Wittenmark) |
| Tolerable jitter (control) | variation < 10% of nominal need not be compensated (Cervin) |

## Statistics for test evidence

| Statement | Rule |
|---|---|
| Zero failures in N independent trials | failure probability < ~3/N at 95% confidence (rule of three) |
| Percentiles | do not average; merge histograms |
| Max over a test | a lower bound on the worst case, never the WCET |

## Numbers from this project's labs (for orientation, not for your board)

| Lab | Result |
|---|---|
| R1 | work 3 ms + `vTaskDelay(10)`: period 12,999 µs, drift +297 ms/99 iterations; `vTaskDelayUntil`: 9,998 µs, −0.15 ms |
| R2 | RTA 1,000 / 3,000 / 10,000 µs → measured 1,006 / 3,024 / 10,087 µs |
| R2 (U = 0.971) | simulator predicts 20% misses; kernel measured 80% |
| R4 / H4 | 19 slots hold a 20-message burst against a 5 ms consumer; 18 lose messages |
| R6 | 25,888 B free total, 5,728 B largest block: an 8,000 B request fails |
| R8 | with a 12.5% interrupt: RTA without it 10.0 ms, with it 11.5 ms, measured 11.6 ms |
| R10 | mean 715 µs, p99.9 9,496 µs → after four fixes p99.9 631 µs |
