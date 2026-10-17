# Interrupts: reacting on time {.chapter data-part="PART 1 · TIME"}

<p class="lede">Polling asks "has anything happened?" on a schedule. An interrupt makes the hardware say "it happened" and run your handler now. Interrupts are how a processor meets a deadline measured in microseconds — and the first place a program gets concurrent.</p>

## A short history

Smotherman's survey of the field dates early forms of the mechanism to the mid-1950s: the NBS DYSEAC (1954) with an I/O interrupt, the UNIVAC 1103A (1956, often cited as first), the Lincoln Lab TX-2 and IBM Stretch (1957) with vectored interrupts that jump straight to the right handler. Smotherman is explicit that attribution is contested (for example, the 1953 1103 manual does not describe interrupts), so this book says only "by the mid-1950s". The Apollo guidance computer, a decade later, shows the mature pattern: **hardware interrupts** for the few things that cannot wait (the digital autopilot, uplink, keyboard), a **timed-task list** (Waitlist) for short code that must run at a given instant, and **priority jobs** for everything else.

## What happens on an interrupt

1. The peripheral asserts a request. If that interrupt is enabled and not masked by a higher-priority one, the CPU finishes the current instruction.
2. The hardware saves a small set of registers and jumps through the **vector table** to the handler (the ISR).
3. The ISR runs. A higher-priority interrupt can preempt it.
4. The ISR returns; the hardware restores the registers and the interrupted code resumes — or, if the kernel asked for a task switch, a different task resumes (ch. 6).

{{fig:interrupt-flow | The standard split: the interrupt handler does the minimum and posts an event; a task does the long work.}}

## ISR rules that matter

| Rule | Why |
|---|---|
| **Short**: microseconds to tens of microseconds | while an ISR runs, equal and lower-priority interrupts and *every task* wait |
| **Never block** (no waiting for a lock, queue space, or time) | there is no task to put to sleep; the system would stop |
| **Use only the kernel's "FromISR" functions** | normal calls assume they run in a task; the ISR versions never block and report whether a task switch is needed |
| **Handle the interrupt source** (clear the flag) | otherwise it fires again immediately |
| **Touch shared data with care** | the ISR can run between any two instructions of the code it interrupted |
| **Do not print, allocate or take long locks** | each is long, variable or unsafe |

On Cortex-M the kernel only masks interrupts **at or below** a configured priority (`configMAX_SYSCALL_INTERRUPT_PRIORITY`). An interrupt more urgent than that line is never delayed by the kernel but may **not** call kernel functions. A numerically larger priority value is *less* urgent — a frequent source of confusion.

## The deferred-work pattern

[RAN]{.ran} Lab R4 uses the pattern end to end: a timer interrupt every millisecond stamps a message with the hardware time and posts it with `xQueueSendFromISR`; a task consumes it. The ISR's whole job is 5 lines:

```c
static void producer_isr(void) {
    BaseType_t woken = pdFALSE;
    msg_t m = { seq++, now_us() };                     /* stamp at the source */
    if (xQueueSendToBackFromISR(q, &m, &woken) != pdTRUE)
        dropped++;                                     /* cannot block: drop and COUNT it */
    portYIELD_FROM_ISR(woken);                         /* switch now if the consumer outranks the interrupted task */
}
```

The two lines to remember: **stamp the data where it is born** (the ISR), and **count what you cannot deliver**. Chapters 15 and 17 return to both.

## Interrupts are part of the schedule

Interrupt handlers run at a priority above every task, so their execution time delays *every* task. An analysis that lists tasks and forgets the interrupts is optimistic by exactly their interference.

[RAN]{.ran} Lab R8: three periodic tasks (C/T = 1/4, 2/6, 3/12 ms) plus a timer interrupt every 2 ms costing 250 µs (12.5% of the CPU).

| Task | Deadline | Measured worst response | Analysis **without** the interrupt | Analysis **with** it as a top-priority task |
|---|---|---|---|---|
| t1 | 4,000 µs | 1,260 | 1,000 | 1,250 |
| t2 | 6,000 µs | 3,534 | 3,000 | 3,500 |
| t3 | 12,000 µs | 11,619 | 10,000 | 11,500 |

Leaving the interrupt out understates t3 by 14%. Including it matches the measurement to 1%. (Method: chapter 9.)

::: rule
**Rule.** In any timing budget, list every interrupt with its rate and worst-case handler time, and charge it to every task below it.
:::

## Masking interrupts is not free

To protect a short sequence from an interrupt, code can **disable interrupts** (a critical section). While interrupts are off, nothing preempts the code — and nothing else runs, including the interrupt you are waiting for. A critical section adds its length to the worst-case latency of every interrupt. Two consequences:

- **Keep critical sections to a handful of instructions.** Copying a 16-byte struct is fine; formatting a log line is not.
- **A masked interrupt that fires twice is delivered once.** The hardware remembers *that* it fired, not *how many times*. A 1 kHz interrupt delayed by 2.5 ms delivers one handler call, not three: samples are silently lost. Lab R10 counts these as `isr_late`.

::: trap
**Trap: `volatile` is not synchronization.** A flag set by an ISR and polled by a task must be `volatile` so the compiler re-reads it. That is all `volatile` does. It does not make a read-modify-write atomic, does not order writes to *other* variables, and has been miscompiled: Eide and Regehr tested thirteen production C compilers and found volatile-access bugs in each (EMSOFT 2008; a simple source rewrite worked around 96% of the failing cases; 2008-era compilers). Chapter 12 gives the real tools.
:::

## Where the debugger and the interrupts disagree

Stopping the CPU at a breakpoint does not stop the world on real hardware: timers keep counting, peripherals keep receiving. Many microcontrollers pause the watchdog while halted, others do not. In the emulator used in this book the virtual clock is frozen during a stop but still moved forward by about 1 ms per stop in our measurement (Lab R9). Consequence: **do not use breakpoints to investigate timing**; use tracing, counters and watchpoints (chapter 20).

## Check yourself

::: check
1. A 1 kHz interrupt takes 80 µs. A critical section elsewhere disables interrupts for 1.6 ms. What happens to the interrupt, and what should the code count to notice?
2. Why can an ISR not call `xSemaphoreTake` with a timeout, and what does it call instead of `xSemaphoreGive`?
3. What does "numerically higher priority value" mean on your target? Check before you assign an interrupt priority.
:::

**Lab links.** R4 (ISR to queue), R8 (interrupts in the analysis).
