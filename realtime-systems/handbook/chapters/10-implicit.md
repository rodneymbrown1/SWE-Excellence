# The implicit-requirements checklist {.chapter data-part="PART 6 · REFERENCE"}

<p class="lede">Forty-five requirements nobody writes down. For a component you own or review, mark each <b>K</b> known (evidence in hand), <b>A</b> assumed, or <b>?</b> unknown. The number of A and ? marks is the size of your risk. Explanations are in book chapter 23.</p>

| ID | Requirement | K / A / ? | ID | Requirement | K / A / ? |
|---|---|---|---|---|---|
| T1 | period and deadline stated | | Y1 | owner + protection + hold time per datum | |
| T2 | budget is an upper bound | | Y2 | multi-field data read as a snapshot | |
| T3 | miss policy defined | | Y3 | mutex (inheritance) for exclusion | |
| T4 | jitter bounded | | Y4 | blocking time bounded, in R | |
| T5 | interrupts + tick in budget | | Y5 | lock order; no blocking in a lock | |
| T6 | counters wrap; known | | Y6 | library/driver locks known | |
| T7 | CPU headroom; exact R | | Y7 | ISRs: ISR-safe calls, short sections | |
| T8 | rate justified; harmonic | | R1 | watchdog fed after *every* task progresses | |
| T9 | absolute delays for periods | | R2 | reaction to failure defined | |
| S1 | priorities follow timing | | R3 | containment of failures | |
| S2 | no spin; no unbounded wait | | R4 | restart tested, incl. repeated | |
| S3 | equal-priority sharing OK | | R5 | evidence survives a reset | |
| S4 | timer callbacks short | | R6 | stack/heap margins measured | |
| S5 | idle task can run | | R7 | growth with time bounded | |
| S6 | overload degrades predictably | | R8 | silent consumers/sensors detected | |
| M1 | queue depth justified | | O1 | one number + method + margin | |
| M2 | overflow policy named | | O2 | histogram, open-loop | |
| M3 | drops counted and visible | | O3 | releases / completions / misses | |
| M4 | age limit + source timestamp | | O4 | trace left in the product | |
| M5 | rate-crossing rule | | O5 | observation does not perturb | |
| M6 | QoS matches need | | O6 | observed max ≠ WCET | |
| M7 | start-up order + readiness | | O7 | tests drive the worst case | |
| M8 | message ownership clear | | | **Score:** K ___ A ___ ? ___ | |
