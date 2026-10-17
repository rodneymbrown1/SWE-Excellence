# Publish/subscribe and quality of service {.chapter data-part="PART 4 · FLOW"}

<p class="lede">In publish/subscribe a component sends data to a <em>topic</em> and does not know who receives it. That decoupling is the reason frameworks use it, and the reason timing problems are harder to see: the contract is no longer in a function signature. It is in the quality-of-service settings, or it is nowhere.</p>

## The model

{{fig:pubsub | Publishers write to a topic; each subscriber has its own queue and its own QoS. The same data, three different guarantees.}}

| Piece | What it is | Where it lives |
|---|---|---|
| **Topic** | a named channel with a message type | the framework's directory / middleware |
| **Publisher** | writes messages at its own rate | its own task or callback |
| **Subscriber** | receives into **its own queue**, then processes | the subscriber's task or executor |
| **Message** | typed data, ideally with a source timestamp and sequence number | allocated by the framework |
| **QoS** | the rules for delivery on each connection | configured per publisher and per subscriber |

Three consequences follow from "each subscriber has its own queue": a slow subscriber affects only itself; the publisher cannot know whether anyone is behind; and **every subscriber needs its own sizing and overflow analysis** (chapter 15).

## The QoS vocabulary (ROS 2 / DDS)

ROS 2 documents these policies for every publisher and subscription:

| Policy | Options | What it decides |
|---|---|---|
| **History** | *keep last* N · *keep all* (bounded by resource limits) | how many samples a slow reader can accumulate |
| **Depth** | the N for keep-last | queue size ("only honored if the history policy was set to keep last") |
| **Reliability** | *best effort*: "may lose them if the network is not robust" · *reliable*: "may retry multiple times" | loss versus latency and retries |
| **Durability** | *transient local*: "the publisher becomes responsible for persisting samples for late-joining subscriptions" · *volatile* | what a **late joiner** sees |
| **Deadline** | "the expected maximum amount of time between subsequent messages being published to a topic" | detects a publisher slower than promised |
| **Lifespan** | "the maximum amount of time between the publishing and the reception of a message without the message being considered stale or expired (expired messages are silently dropped …)" | **age limit** |
| **Liveliness + lease duration** | automatic or manual; "the maximum period of time a publisher has to indicate that it is alive … (losing liveliness could be an indication of a failure)" | failure detection |

A publisher and subscriber **match** only if the publisher offers at least what the subscriber requests: a best-effort publisher and a reliable subscriber do not connect, and the framework reports an incompatible-QoS event rather than failing loudly in your code. Read the compatibility table in your framework's documentation for the full matrix.

::: why
**Evidence and limits.** The list above is quoted from the ROS 2 documentation (rolling release). Other pub/sub systems (DDS itself, cFS's software bus, F´'s ports, MQTT) use different words for overlapping ideas. We do not claim identical semantics across them. The *questions* carry over: how many samples are kept, can they be lost, how old may they be, who hears the last one, who notices silence.
:::

## Translating the vocabulary into requirements

| Question about a connection | QoS knob | Example answer |
|---|---|---|
| Can this data be lost? | reliability | control commands: no; display refresh: yes |
| How many samples may pile up? | history / depth | latest only (1) for state; N for a filter that needs a window |
| How old is too old? | lifespan, deadline | a position older than 100 ms is not used |
| Does a late joiner need history? | durability | a logger that starts late needs the last configuration |
| How do I know the publisher is alive? | liveliness + lease | missing for 3 periods → degrade |
| Who is slower than whom? | rate × depth | 100 Hz producer, 10 Hz consumer, depth 10 → 1 s of backlog |

::: rule
**Rule.** For every subscription write the sentence: *"This subscriber needs ___ from this topic at least every ___ and at most ___ old; if it cannot keep up it ___."* The blanks are your QoS.
:::

## What the middleware does not give you

- **Timing.** QoS says what to deliver, not when. Delivery latency depends on the transport, serialization, the executor and the priorities of the threads involved. Casini, Blaß, Lütkebohle and Brandenburg (ECRTS 2019) had to model the ROS 2 executor's scheduling to analyse response times of callback chains, reporting its timing behaviour as undocumented at the time; the practical rule is that **callbacks in an executor are scheduled by the executor's own order, not by your RTOS priorities**.
- **Ordering across topics.** Two topics have two queues; messages from different topics have no defined order unless you timestamp and merge.
- **A consistent snapshot.** A subscriber reading three topics sees them at three times (chapter 17).
- **Liveness.** A silent publisher looks the same as one with nothing to say, unless you set a deadline or liveliness.

## The same ideas in other frameworks

| Framework | Pub/sub construct | Where the contract lives |
|---|---|---|
| **ROS 2** | topics, QoS profiles | QoS settings, executor configuration |
| **cFS** | **software bus**: apps publish CCSDS messages and subscribe by message ID through **pipes** | pipe depth, message limits, scheduler table (check your build's values) |
| **F´** | typed **ports** wired point-to-point in a topology; async ports have a **queue per component**; guarded ports use a mutex | port kinds and queue depth per component instance |
| **AUTOSAR** | signals via the RTE; SOME/IP for service-oriented | signal/timing configuration |
| **Your own** | a queue per subscriber | whatever the code implies |

F´'s "async port" is the clearest bridge from chapter 15: a message arrives at a port; the component's queue holds it; the component's own thread dequeues and handles it. cFS's pipe is the same object under another name.

::: trap
**Trap: assuming "reliable" means "on time".** Reliable delivery retries; retries add latency, and a retransmission storm can load the network and the CPU exactly when the system is already struggling. For control data that must be fresh, best-effort with a short lifespan is often safer than reliable with a long queue.
:::

## Check yourself

::: check
1. A 100 Hz IMU topic feeds a 100 Hz controller and a 1 Hz logger. Write the QoS for each subscriber and justify the difference.
2. A subscriber joins 10 s after the publisher started. What do you want it to receive first? Which setting controls it?
3. Your framework's default queue depth for a subscription is 10. At 200 Hz publishing and a consumer that stalls for 100 ms, what is lost, and does anything say so?
:::
