# 02 · Time: clocks, ticks, wrap-around, jitter, latency, WCET, histograms

## 1. Patriot at Dhahran — a clock that drifts (GAO/IMTEC-92-26) [C04, **P**]

Verified from the GAO report text (`_raw/gao-patriot/`):

- 25 Feb 1991: a Patriot battery failed to track/intercept a Scud; "killing 28 Americans" (report p.1 text). The battery "had been operating continuously for over 100 hours".
- Mechanism (GAO text): "Time is kept continuously by the system's internal clock in tenths of seconds but is expressed as an integer"; the conversion to a real number is done in **24-bit** registers "cannot be any more precise than 24 bits". The longer the system runs, the larger the integer, the larger the absolute error.
- **GAO table (reproduced in the book, checked row by row):** after 1 h → 0.0034 s error, ~7 m range-gate shift; 8 h → 0.0275 s, 55 m; 20 h → 0.0687 s, 137 m; 48 h → 0.1648 s, 330 m; 72 h → 0.2472 s, 494 m; **100 h → 0.3433 s, 687 m**. The table footnote: "Continuous operation exceeding about 20 hours — target outside range gate".
- Lesson: an error that is invisible per-sample can be **linear in uptime**. The book asks: *what is the clock's resolution, what is it multiplied by, and how long can the system stay up?*
- Lab note: the book's Lab H1 reproduces the arithmetic (truncating 0.1 to 24 fractional bits) and prints the drift after N hours, so the 0.34 s figure can be reproduced rather than taken on trust. **[RAN]** (see `10-…`).

## 2. Boeing 787 — a counter that overflows after 248 days [C05, **P**]

EASA-hosted copy of the FAA AD (2015-09-07) (`_raw/easa-787-ad/`), verified wording:

- "a Model 787 airplane that has been powered continuously for **248 days** can lose all alternating current (AC) electrical power due to the generator control units (GCUs) simultaneously going into failsafe mode."
- "caused by a software counter internal to the GCUs that will overflow after 248 days of continuous power."
- If all four main GCUs were powered up at the same time, they would all enter failsafe mode together → loss of all AC power.
- **Not in the AD:** the counter's unit and width. The widely repeated "signed 32-bit counter of 10 ms ticks" is **arithmetic inference**: 2³¹ × 0.01 s = 21,474,836 s = **248.55 days**. The book presents it as *"consistent with"*, never as fact. (`09-…`)
- Lesson: every counter wraps; **common-cause** (all four units powered at once) turns a single-unit fault into a system fault.

## 3. Cloudflare leap second (2017) — wall clock vs monotonic clock [C12, **P**]

From Cloudflare's own post-mortem (`_raw/cloudflare-leap-second/`): the root cause "was the belief that time cannot go backwards"; code "assumed that the difference between two times would always be, at worst, zero"; Go's `time.Now()` at the time was wall-clock based, so a leap second made a measured duration **negative**; a negative value reached weighted selection code that panicked. At peak ≈0.2% of DNS queries affected (per the post). Used in ch. 3 to explain **monotonic vs wall-clock** time. (Not an embedded incident; chosen because the failure is precisely about a clock type.)

## 4. Jitter and latency affect control, quantitatively

- **Cervin thesis (2003)** [S09, **P**, targeted passages]: "A typical rule-of-thumb [Åström and Wittenmark, 1997] is that the sampling interval *h* should be selected such that **ω_c h = 0.2–0.6**, where ω_c is the bandwidth of the closed-loop system. A real-time system where the product ω_c h is small for all control tasks will be less sensitive to scheduling-induced latencies and jitter, but it will also consume more CPU resources."
- Same thesis: "As a rule of thumb, relative variations of the sampling interval that are smaller than **ten percent** of the nominal sampling interval need not be compensated for."
- Same thesis: "additional, time-varying latency will be introduced by the task scheduling. Taken together, the latency and jitter degrade the control performance."
- Book usage: ch. 17 (choosing a rate). We state the rule with its source and say: *this is the control-engineer's rule; you will usually be handed the rate, but you should know where it came from and what moving it costs.*
- The IEEE CSM article (Cervin et al. 2003) was **not** opened; only the thesis. (`09-…`)

## 5. WCET — what it is and what measuring can and cannot give [S08, **P**, key passages]

Wilhelm et al. (2008): static analysis vs "measurement-based methods" ("dynamic timing analysis"). Verified phrases: bounds must be "**safe**, i.e., they must never underestimate" and "**tight**"; two cautions the book repeats — "The assumption that only local worst cases have to be considered to safely determine upper bounds on global execution times is unsafe" and "The assumption that one could identify a worst initial execution state, to safely start measurement or analysis of a piece of code in, is unsafe." Therefore **the largest value you observed is a lower bound on the true WCET, not an upper bound.** The book calls the measured value "observed maximum (HWM)" and the budget "WCET budget (claimed)", and keeps the two names apart.

## 6. Measuring latency correctly

- **Coordinated omission** (Gil Tene) [S19, **P**]: "when omission is coordinated with observed events, it can dramatically skew the statistical analysis of the remaining results." In a closed-loop tester that waits for each response before sending the next, a stall suppresses exactly the samples that would have been slow. The group post works an example in which 10 observations of 526 ms imply "5,350 additional results" that were never recorded.
- Tene's talk recommends percentile histograms; HdrHistogram README [T14] documents a histogram that records values over a wide dynamic range with fixed precision and supports "coordinated omission" correction.
- **Percentiles do not average** (talk slides; stated in a search summary of the 2015 slides and consistent with the 2012 slides we read): do not average p99 across runs; merge the histograms.
- **Application to RTOS:** a periodic task that overruns *skips* its next release(s); a logger that only records the response time of jobs that *ran* has the same bias. Lab H5 builds this on purpose. **[RAN]**

## 7. Measuring on Cortex-M

- DWT cycle counter `CYCCNT` at 0xE0001004, enabled by `DEMCR.TRCENA` (bit 24) and `DWT_CTRL.CYCCNTENA` (bit 0); 32-bit, so at e.g. 100 MHz it wraps in ≈43 s; unsigned subtraction handles one wrap. (IAR, MCU on Eclipse, SEGGER knowledge-base pages in a search; **S/Sn** — the arithmetic is checked by us.)
- SEGGER's embOS note (search summary): the more complex the CPU, the bigger the min–max spread (caches, pipelines).
- **QEMU note (`10-…`):** the labs time with the emulated CMSDK TIMER0 under QEMU's deterministic instruction-count mode. Whether QEMU's Cortex-M3 model implements the DWT cycle counter was **not tested**. On real boards use DWT.

## 8. Real-time Linux latency data

- **OSADL QA Farm** [T13] publishes continuously-run latency plots (cyclictest) for PREEMPT_RT kernels on real hardware. Only the index page was downloaded; **no latency number from it is quoted** in the book. The reader is pointed to the live plots.
- **PREEMPT_RT is mainline as of Linux 6.12** (Sept–Nov 2024) — Phoronix/heise/InfoQ search summaries (**Sn/S**); the kernel real-time docs page was downloaded (`linux-rt-docs`).

## 9. Use in documents

| Item | Where |
|---|---|
| Patriot arithmetic + table | Book ch. 3, Lab H1 |
| 787 counter | Book ch. 3, Lab R7 (tick wrap), Handbook "every counter wraps" |
| Wall vs monotonic clock | Book ch. 3 |
| ω_c h rule, 10% jitter rule | Book ch. 17, Handbook rate-review |
| Observed max ≠ WCET | Book ch. 9, 20 |
| Coordinated omission | Book ch. 20, Lab H5 |
