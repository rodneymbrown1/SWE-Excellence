# Queues and backpressure {.chapter data-part="PART 4 · FLOW"}

<p class="lede">A queue between two components lets each run at its own pace. It also hides a question that every queue must answer: what happens when the producer is faster than the consumer for long enough to fill it? "It won't" is not an answer; it is the assumption behind most message-loss incidents.</p>

## What a queue decouples, and what it does not

A queue lets a producer (often an interrupt) hand data to a consumer (a task) without waiting for it. It removes the *timing coupling* of a direct call. It does **not** remove the *capacity coupling*: if the average arrival rate exceeds the average service rate the queue fills however large it is; if only the *peak* rate exceeds it, the queue size decides whether the burst is absorbed or lost.

FreeRTOS queues copy items in, block senders and receivers with a timeout, and have "FromISR" variants that never block. A queue of length one with `xQueueOverwrite` implements "latest value wins", which is right for a sensor *state* and wrong for an *event*.

## The four decisions every queue needs

| Decision | Options | Question to ask |
|---|---|---|
| **Depth** | a number, from a burst calculation | how long can the consumer fall behind, at what rate? |
| **Overflow policy** | block the producer · drop newest · drop oldest · overwrite · error and escalate | which data is worth more: old or new? Can the producer block at all (an interrupt cannot)? |
| **Visibility** | a counter of drops, a high-water mark of depth | will anyone *notice* a loss? |
| **Age limit** | maximum useful age of an item | is a 200 ms-old sample better than none? |

::: rule
**Rule.** A queue without a written overflow policy and a drop counter is a bug waiting for load. The policy is a *requirement*; the framework's default is a *choice somebody else made*.
:::

## Sizing from a burst

Average load hides the burst. The formula is arithmetic, not statistics:

**depth ≥ ⌈(peak arrival rate − service rate) × burst duration⌉ + 1**

Little's law (L = λW: the average number in a stable system equals the arrival rate times the average time each item spends in it) gives the *average* occupancy and is a good sanity check, but a queue must be sized for the peak.

[RAN]{.ran} Scenario: 100 messages/s steady plus one burst of 20 messages in 20 ms each second (peak 1,100/s); the consumer needs 5 ms per message (200/s capacity, so the mean load is a comfortable 60%). Formula: ⌈(1,100 − 200) × 0.020⌉ + 1 = **19**.

{{fig:queue-depth | Items in the system during one burst (host simulation). A queue of 19 holds the burst; a queue of 4 loses everything above the red line. The drain takes about 95 ms after the burst ends.}}

| Queue depth | Host simulation, 10 s (lab H4) | FreeRTOS on the emulator, 5 s (lab R4) |
|---|---|---|
| 4 | 134 dropped | 75 dropped |
| 8 | 98 dropped | 55 dropped |
| 18 | 8 dropped | 5 dropped |
| **19** | **0 dropped** | **0 dropped** |

Three independent routes — the formula, a simulation and a real kernel with an interrupt producer — agree on the same threshold: 19 slots, with 18 losing messages. Both also agree that with **no drops the worst latency is 95 ms** (a 5 ms service time × 19 queued): **a bigger queue buys loss-free delivery with latency**. If an item older than 50 ms is useless, a queue of 19 is the wrong design even though it never loses anything.

## Choosing the policy

| Policy | Latency of what you keep | What you lose | Use when |
|---|---|---|---|
| **Block** the producer | highest (producer is held) | nothing, if the producer can wait | the producer is a task and can be slowed |
| **Drop newest** (queue full → refuse) | old data stays | fresh data | **events** that must be processed in order, with bounded loss |
| **Drop oldest** (make room) | lowest | stale data | **state** where only the latest matters |
| **Overwrite** (length 1) | lowest | all but latest | sensor values, set-points |
| **Escalate** (error, shed load, restart) | — | — | loss is unacceptable and must be handled |

[RAN]{.ran} In Lab R4, at depth 4 the drop-oldest policy kept the worst latency at **20 ms** against **24 ms** for drop-newest, with the same number of drops. It keeps fresher data. Which is correct depends on whether the data is state or an event.

An interrupt cannot block. Its only options are to drop (and count), overwrite, or notify a task and move work out of the interrupt altogether (chapter 4).

## Unfinished work is a queue too

::: case
**Apollo 11 (1969): the queue was the job table.** Each unfinished `SERVICER` job held one of eight "core sets". Work was never dropped by a producer; the *queue of unfinished jobs* grew until its fixed pool ran out and the executive restarted. Recognise the pattern wherever a periodic job can start before the previous instance finished: in thread pools, callback queues, rate groups with queued cycle messages, and retry loops. (Chapter 11.)
:::

## A consumer that stops silently

::: case
**Northeast blackout, 14 August 2003.** The US–Canada task force found that the alarm software at the utility "essentially 'stalled' while processing an alarm event", operators "were unaware" their alarms had stopped, and that at 14:41 "the primary server hosting the EMS alarm processing application failed, due either to the stalling of the alarm application, 'queuing' to the remote EMS terminals, or some combination of the two." Press coverage of the vendor's analysis describes "a couple of processes that were in contention for a common data structure" that "were both able to get write access … at the same time", a fault found only after weeks of searching about a million lines of code, in software the vendor said had run "in excess of three million online operational hours" without exercising it; once the alarm function stopped, "unprocessed events began to cue up" and the server hosting it failed [SEC]{.sec} (the task force's own text says "stalled"; the race detail is the vendor's finding as reported). The pattern generalises: **a consumer that stops, with a queue in front of it, produces silence, then delay, then overflow.** What was missing was any signal from the alarm function that it was alive.
:::

How to see a stalled consumer: expose **queue depth**, **age of the oldest item**, and a **heartbeat** from the consumer that a separate monitor checks (chapter 19). Depth rising with no consumer progress is a stall, not a burst.

## Queues and the analysis

A queue breaks Liu and Layland's "independent tasks" assumption: the consumer's response time now depends on the producer's pattern. Two practical consequences:

1. **Treat the consumer as sporadic**, with a *minimum inter-arrival* equal to the fastest the queue can be refilled (often the producer's period), and a deadline equal to the age limit minus the queue wait.
2. **Add the queue wait to the end-to-end budget.** In the example above, the worst item waits 95 ms before it is even processed (chapter 17).

## Check yourself

::: check
1. A sensor posts 500 samples/s, mean; during a 40 ms fault it posts 4,000/s. The consumer handles 800/s. Size the queue; state the policy; what extra latency does a full queue add?
2. Where in your system does the producer *not* know the consumer's rate? What does it do when the queue is full?
3. A consumer task blocks forever on a lock. Which numbers on a dashboard would show it within one second?
:::

**Lab links.** H4 (host simulation and the `apollo` model), R4 (interrupt to queue).
