# The simplest program: a loop {.chapter data-part="PART 1 · TIME"}

<p class="lede">Almost every embedded program starts as a loop that reads, computes and writes. It has no scheduler and no clock. Understanding exactly what that loop does and does not guarantee explains why everything else in this book exists.</p>

## The super-loop

```c
int main(void) {
    init_hardware();
    for (;;) {                      /* "super-loop" / "main loop" */
        read_sensors();
        compute();
        write_outputs();
    }
}
```

This is correct, tiny, easy to reason about, and used in production systems of every size. The loop's **cycle** is one pass. Everything about its timing follows from one fact:

> **The period of the loop is the sum of the time of everything in it.**

{{fig:loop-time | A loop's period is whatever the code takes. The third iteration takes a rare branch and is almost twice as long.}}

## What the loop cannot do

| Wish | Why the loop cannot promise it |
|---|---|
| "Run every 10 ms" | nothing measures 10 ms; the period is the sum of the code's durations, and it changes whenever the code or the data changes |
| "React within 1 ms to a button" | the button is checked once per cycle: the reaction time is *up to a full period* |
| "Do two things at once" | there is one flow of control; a long step delays every step after it |
| "Add a feature without disturbing the rest" | the new step lengthens the period for *all* steps |

A loop that does nothing slow is predictable. One slow step, taken rarely, is the usual way a loop fails after launch. The same shape appears in the Pathfinder lead's account of what *testing* missed: the rare, heavily-loaded path.

## Waiting: busy-wait versus a time check

The first fix people reach for is a delay.

```c
for (;;) {
    do_work();                      /* takes 2 ms, sometimes 5 ms */
    delay_ms(10);                   /* wait 10 ms */
}
```

The period is now **work time + 10 ms**, not 10 ms. The error is not random: it is the work time, every cycle, so it **accumulates**. [RAN]{.ran} Lab H1 on this machine: a 2 ms job followed by a "10 ms" relative sleep, 300 iterations, ended 1,239 ms late (4,239 ms against an ideal 3,000 ms). Sleeping until an *absolute* next instant ended 0.2 ms late.

```c
next = now();
for (;;) {
    do_work();
    next += PERIOD;                 /* the schedule advances by the period, not by "now + period" */
    wait_until(next);               /* absolute instant: lateness does not accumulate */
}
```

::: rule
**Rule.** Periodic work waits for *the next scheduled instant*, never for *a duration after it finished*. Every RTOS has both calls; the relative one is for "wait a bit", the absolute one is for periods (ch. 3, ch. 6).
:::

A busy-wait (spinning on the clock) is exact but wastes the CPU and blocks everything else. Sleeping lets the CPU idle or do other work, but a general-purpose OS wakes you *late*: on the Mac used for Lab H1 the median wake-up was 1.6 ms late. A microcontroller with a hardware timer wakes you within microseconds. That is the first reason to run on a real-time system.

## Polling and the shape of events

A loop that checks inputs is **polling**. It is simple, but its worst-case reaction time equals the loop period, and its cost is paid even when nothing happens. Interrupts (ch. 4) invert this: the event announces itself.

A loop can still react well if every step is **short and never blocks**. The usual style is a **state machine per activity** that advances one small step each pass and always returns:

```c
switch (state) {
case WAIT_START:  if (button_pressed()) { t0 = now(); state = DEBOUNCE; } break;
case DEBOUNCE:    if (elapsed(t0) >= 20) state = (button_pressed() ? ARMED : WAIT_START); break;
case ARMED:       start_motor(); state = RUN; break;
/* ... */
}
```

This is **cooperative multitasking** by hand: each state machine is a "task" that yields by returning. It is the cheapest concurrency there is, and the root of the "run-to-completion" idea in chapter 6. Its single rule is also its weakness: **one step that takes too long, or blocks, stalls everything.**

## Foreground and background

Add interrupts and the loop becomes the **background**; interrupt handlers are the **foreground**. The foreground reacts fast; the background does the long work. Data passes between them through variables the foreground writes and the background reads. That is already shared state, and the first place real bugs live (ch. 4, ch. 12).

## Where the loop is the right answer

A super-loop is reasonable when all of these hold: few activities, similar rates, hard deadlines easy to meet with large margin, no long steps, and a reviewer who can read the whole program in one sitting. It stops being reasonable when a new feature adds a long or blocking step, or when two activities run at very different rates (a 1 kHz control loop and a once-per-second log line cannot share one pass without waste).

::: trap
**Trap: the invisible rare branch.** The loop in the figure meets "every 45 ms" twice and misses once. Nothing in the source says so; review sees three short steps. Rare branches (error paths, calibration, flash writes, a long print) are exactly where periods are lost. Ask of every loop: *what is the longest single thing it can do?*
:::

## Try it

::: try
Run Lab H1: `./h1_loop sleep_rel 10000 2000 300` and `./h1_loop sleep_abs 10000 2000 300` in `labs/host/`. Then add noise: `./h1_loop sleep_abs 10000 2000 300 6000` (every 17th iteration takes 6 ms longer). Predict first: which of the two versions loses time on the noisy iteration, and which only loses *that one* iteration?
:::

## Check yourself

::: check
1. A loop calls `delay(100)` after 12 ms of work. What is its period? After 1,000 iterations, how far behind an ideal 100 ms schedule is it?
2. A button is polled once per loop pass of 20 ms. What is the worst-case reaction time? What is the average?
3. Name one step in a loop you know whose duration depends on data, and say what it does to every other step.
:::
