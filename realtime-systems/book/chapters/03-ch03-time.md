# Measuring time {.chapter data-part="PART 1 · TIME"}

<p class="lede">Before you can meet a deadline you must be able to read a clock, and trust it. Clocks have a resolution, an accuracy, a width, and a type. Four of the incidents in this book are clock bugs.</p>

## The stack of clocks

{{fig:clock-stack | From oscillator to your code. Two layers wrap around; two layers add error.}}

| Layer | Question to ask | Number to know |
|---|---|---|
| **Oscillator** | how accurate is it? | **ppm**. A 50 ppm crystal gains or loses 4.3 s per day (50×10⁻⁶ × 86,400) |
| **Hardware counter** | how fast does it count, how wide is it? | at 25 MHz a 32-bit counter wraps in 171.8 s (2³² / 25×10⁶); a 1 MHz microsecond counter in 71.6 minutes |
| **Tick interrupt** | what is one tick? | 1 kHz → 1 ms. Tick *resolution* is 1 tick; a delay is accurate to ±1 tick |
| **Kernel tick count** | how wide is the type? | 32-bit at 1 kHz wraps in 49.7 days; 16-bit in 65.5 s |
| **Your code** | how do you compare two times? | subtract first, then compare (below) |

**Resolution** is the smallest step a clock can show. **Accuracy** is how close it stays to true time. A clock can have microsecond resolution and be wrong by seconds per day.

## Every counter wraps: compare differences, not values

An unsigned counter that reaches its maximum goes to zero. Code that compares two *values* breaks at the wrap; code that compares a *difference* does not, provided the interval is less than half the range.

```c
if (now >= deadline) { ... }                 /* WRONG across the wrap */
if ((int32_t)(now - deadline) >= 0) { ... }  /* right, for intervals < 2^31 ticks */
```

[RAN]{.ran} Lab R7 builds the kernel with a **16-bit tick** so it wraps after 65.5 s, jumps the clock to 6 ticks before the wrap, and asks for a 100-tick timeout. The naive comparison reported "expired" immediately (0 loop iterations, 2 µs). The safe comparison ran the full 100 ticks (99,651 µs). The kernel's own delays were unaffected: a periodic task woke every 20 ms through the wrap (ticks 65,521 → 5 → 25 …).

::: case
**Boeing 787, 2015: the 248-day counter.** A US airworthiness directive (mirrored by EASA) states that a 787 "powered continuously for 248 days can lose all alternating current (AC) electrical power due to the generator control units (GCUs) simultaneously going into failsafe mode", "caused by a software counter internal to the GCUs that will overflow after 248 days of continuous power." If the four main units were powered up together they would all fail together. The directive does not give the counter's width or unit. The number is *consistent with* a signed 32-bit count of 10 ms ticks: 2³¹ × 0.01 s = 248.55 days. The lesson is independent of the details: **every counter wraps, and identical units powered together wrap together.**
:::

## A clock that is almost right gets worse every hour

::: case
**Patriot, Dhahran, 1991: 0.3433 seconds.** A battery that had run for over 100 hours failed to track an incoming missile. The US Government Accountability Office found that the system kept time as an integer count of tenths of a second and converted it to seconds by multiplying by 1/10 in a 24-bit register. 1/10 has no exact binary form; the stored value was chopped. The error per tick is tiny, the number of ticks grows with uptime, so the clock error grows **linearly**: 0.0034 s after 1 hour, 0.0687 s after 20, 0.1648 s after 48, **0.3433 s after 100** — a range-gate shift GAO tabulates as 687 m.
:::

[RAN]{.ran} Lab H1c reproduces GAO's table to four decimals by chopping 1/10 to 23 binary places (the 24-bit register's first fractional bit is zero for 0.1, an explanation that is ours; GAO says only "24 bits"). The question to take from it is general: **what is each time value multiplied by, and how long can the system stay up?**

## Wall clock versus monotonic clock

| Clock | Can jump? | Use for |
|---|---|---|
| **Wall / real-time** (calendar time) | yes: NTP steps, leap seconds, manual set | timestamps for humans and logs |
| **Monotonic** | never goes backwards; may not count while suspended | durations, timeouts, periods, deadlines |

::: case
**Cloudflare, 1 January 2017.** A leap second made a duration computed from two wall-clock readings **negative**. A component had assumed "the difference between two times would always be, at worst, zero"; the negative value reached weighted-selection code that panicked. At peak about 0.2% of DNS queries were affected. (Cloudflare's own post-mortem.) Not an embedded system, but the bug is a clock-type bug, and embedded systems that mix a calendar time from a radio or GPS with a tick count can do the same.
:::

## Delays in an RTOS: three behaviours to know

| Call (FreeRTOS names) | What it means | Use it for |
|---|---|---|
| `vTaskDelay(n)` | block for *at least n−1 ticks plus the rest of the current tick* after this call | "wait a bit" |
| `xTaskDelayUntil(&last, n)` (`vTaskDelayUntil`) | wake at `last + n`, then advance `last` | **periods** |
| software timer | run a callback at an instant | periodic work that is short and does not block |

[RAN]{.ran} Lab R1, 1 kHz tick, 3 ms of work per cycle:

| Method | Mean period | Drift after 99 iterations |
|---|---|---|
| work + `vTaskDelay(10 ms)` | 12,999 µs | **+296,934 µs** |
| work + `vTaskDelayUntil(10 ms)` | 9,998 µs | **−153 µs** |
| `vTaskDelay(1)` called at 40 different phases in a tick | between **24 µs and 999 µs** (one tick = 1,000 µs) | — |

The last row is the tick's granularity: a one-tick delay can return almost immediately.

::: trap
**Trap: a "next wake" time in the future.** `xTaskDelayUntil(&last, n)` assumes `last` is the previous wake time, not a future one. Initialising `last` to a tick that has not happened yet makes the kernel think the counter wrapped, and the call **does not block at all**. In our own first draft of Lab R3 a task did exactly this, spun at priority 6, and starved every lower-priority task for the whole run. Initialise `last = xTaskGetTickCount()` and delay once for an offset.
:::

## Latency, jitter and what to measure

| Term | Definition | Where it comes from |
|---|---|---|
| **Interrupt latency** | event → first instruction of the handler | other interrupts, interrupts masked by critical sections |
| **Scheduling latency** | task becomes ready → task starts | higher-priority tasks, the kernel's own work, a lock |
| **Response time** | release → completion | everything above plus the task's own execution |
| **Jitter** | variation of any of the above from job to job | rare slow paths, preemption, interference |

You measure them with a **second clock that does not depend on the thing measured**: a hardware timer you read (`now_us()` in the labs), a cycle counter (on Cortex-M, `DWT->CYCCNT`, enabled via `DEMCR.TRCENA` and `DWT_CTRL.CYCCNTENA`; not tested in our emulator), or a GPIO pin you toggle and watch on a logic analyser (zero overhead, because writing a pin takes one instruction). Printing is *not* a measurement: formatting and sending a line takes hundreds of microseconds and can change what you are measuring (Lab R9 measures the cost of just stopping in a debugger: about 1 ms per stop).

::: rule
**Rule.** Report time with its **clock, resolution and wrap period**. "Latency 450" is not a measurement; "450 µs, 25 MHz timer, 32-bit, wraps at 172 s" is.
:::

## Check yourself

::: check
1. A 32-bit tick at 1 kHz wraps in 49.7 days. A device runs for 60 days. Which of these are affected: a `vTaskDelay`, a hand-written `if (now > t_end)`, a subtraction `now - t_start` with a 5-second interval?
2. A component multiplies a tick count by a constant and adds it to a calendar time once per second. List two ways the sum can drift or jump.
3. Why does `vTaskDelay(1)` sometimes return in microseconds?
:::

**Lab links.** H1 (loop timing, tick wrap, Patriot arithmetic), R1 (delay behaviour), R7 (tick wrap on a real kernel).
