# Beyond one CPU: buses, clocks and other computers {.chapter data-part="PART 5 · TRUST"}

<p class="lede">Everything so far assumed one processor with one clock. Real systems add a second core, a bus to another controller, a network to a computer in another room. Each addition brings the same six questions back with new answers.</p>

## What changes

{{fig:distributed | Three nodes on a shared bus. Each has its own clock and scheduler; the bus has its own arbitration and delays.}}

| Single CPU | With more than one |
|---|---|
| one clock | many clocks that drift; "now" must be agreed or carried in the data |
| a call either runs or doesn't | a message may be lost, delayed, duplicated or reordered |
| a crash stops everything | one node fails while others carry on (**partial failure**) |
| a lock protects data | there is no shared lock across a bus; use ownership and protocols |
| response time = sum of local pieces | add transmission, arbitration, and the other node's scheduling |

## Many cores in one chip

On a multicore microcontroller or application processor the new problems are **which core runs what** (pinned or migrating), **shared resources** (caches, buses, memory controllers) that make one core's execution time depend on another's, and **true parallelism** for races (chapter 12): two tasks can now truly run at the same instant, so the "it cannot happen because the other has lower priority" arguments of single-core code no longer hold. FreeRTOS supports symmetric multiprocessing in recent versions; its own book notes the examples assume a single core. Treat a multicore RTOS as a different course: this book's analyses (response-time analysis in particular) are for **one** processor.

## A bus is a scheduler too: CAN

The Controller Area Network (CAN) is the dominant in-vehicle bus. Every message has an **identifier**, and the identifier is its **priority**: when several nodes start at once, the lowest identifier wins arbitration and the others wait. A frame already on the bus cannot be preempted. A CAN bus is therefore a **fixed-priority, non-preemptive scheduler**, and a message's worst-case response time has the same shape as a task's (own transmission time, plus blocking by one lower-priority frame already in flight, plus interference from higher-priority messages).

::: case
**CAN schedulability analysis, 1994 → 2007.** Davis, Burns, Bril and Lukkien (2007) report that more than "400 million CAN enabled microcontrollers" were manufactured each year, and that the 1994 worst-case response-time analysis for CAN, "cited in over 200 subsequent papers and transferred to industry in the form of commercial CAN schedulability analysis tools", used by "a large number of major automotive manufacturers" for cars of which "millions" were built, "is flawed. It may provide guarantees for messages that will in fact miss their deadlines in the worst-case." They give revised analysis, and show that the priority-assignment policy "previously claimed to be optimal for CAN, is not in fact optimal." **Lesson:** a published, widely used analysis can be wrong; use tools *and* measurement, and know the model's assumptions.
:::

## Time across nodes

Two clocks that start equal drift apart at the rate of their oscillator error: at 50 ppm each, up to 100 ppm relative, or 8.6 seconds per day (chapter 3). Systems that need a shared notion of time use a **synchronisation protocol** (PTP / IEEE 1588 and, for automotive and industrial Ethernet, gPTP) or put timestamps from a trusted source into the messages. Lamport's 1978 paper makes the underlying point precisely: in a distributed system there is no global clock, only a **"happened before"** relation, and logical clocks give an order consistent with it.

| Need | Technique |
|---|---|
| order of events across nodes | logical clocks, sequence numbers per sender |
| compare *times* across nodes | synchronised clocks, with a known error bound |
| measure latency across nodes | timestamp at the source, subtract at the sink **using synchronised clocks** |
| detect a dead node | heartbeat with a lease; the decision "dead" is a timeout, hence a guess |

::: trap
**Trap: subtracting timestamps from two clocks.** The result includes the clocks' offset. A negative latency, or one that jumps when synchronisation steps the clock, is a symptom (chapter 3's Cloudflare case is the same bug on one machine).
:::

## Messages between nodes

| Property | What can happen | Defence |
|---|---|---|
| **Loss** | frame corrupted or dropped | acknowledgement + retry (adds latency); or tolerate (best effort) |
| **Duplication** | a retry after a lost ack | make the receiver **idempotent**; sequence numbers |
| **Reordering** | multiple paths | sequence numbers; reorder window |
| **Delay** | arbitration, queues, other traffic | deadlines and lifespans (chapter 16) |
| **Partition** | a link is down | heartbeats; degraded mode; reconcile on reconnect |

"Reliable" delivery does not mean "on time": retries consume bandwidth and time. For control data that must be fresh, a stale retry is worse than a loss (chapter 16).

## The same six questions, across nodes

| Question | Across a bus or network |
|---|---|
| Timing | end-to-end budget = source rate + queueing + transmission + remote scheduling + remote processing |
| Scheduling | bus priority (CAN IDs), network QoS, time-triggered schedules |
| Messaging | per-link queues, loss policy, ordering |
| Synchronization | ownership, versioned data, leader election (not locks) |
| Reliability | heartbeat/lease, redundant paths, safe state on silence |
| Observability | synchronised timestamps, traces merged by a common clock |

## Check yourself

::: check
1. A CAN message with a low priority is 130 µs long. A higher-priority message is released just as it starts. What does the high-priority message's analysis need to include that a preemptive task's does not?
2. Two nodes each timestamp a sample with their own 25 MHz clock at 50 ppm. After one hour, how far apart can the clocks be?
3. A command message is retried after a lost acknowledgement. What must the receiver be able to tolerate?
:::
