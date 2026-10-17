# 05 · Messaging, pub/sub, QoS, rates, end-to-end latency, lifecycles

## 1. Queues and backpressure — the arithmetic

- **Little's law:** in a stable queueing system the long-run average number in the system equals arrival rate × average time in the system, `L = λW` (Little 1961 [S25, **U** — classical theorem, used as math]). Embedded use: with 200 msg/s arriving and each message waiting on average 50 ms, you hold on average 10 messages — a lower bound on useful queue depth. The book labels this **average**, and sizes queues for **bursts** using worst-case burst length minus service rate:
  `depth ≥ ⌈ burst_rate × burst_duration − service_rate × burst_duration ⌉ + 1` (+1 for the item in service). This is arithmetic from definitions; no source needed. Lab H4 checks it by simulation. **[RAN]**
- **Overflow policy is a requirement** (we state this as the book's rule): every bounded queue must have a *named* behaviour when full — block, drop-newest, drop-oldest, overwrite, error — and the consumer must be able to *see* drops (counter). FreeRTOS queues: `xQueueSend` blocks up to a timeout and returns `errQUEUE_FULL`; `xQueueOverwrite` is for length-1 queues (T01 ch. 5, **P**).
- **Apollo as a backpressure case (C01):** "if more jobs were being scheduled than were being finished, the number of core sets and VAC areas in use must rise. If the debit continued long enough, the resources would be exhausted." Jobs are not dropped at the producer; the *queue of unfinished work* exhausts a fixed pool; the system **restarts and sheds**.
- **Northeast blackout 2003 (C09, C10):** the Task Force report: FE's alarm process "essentially 'stalled' while processing an alarm event"; "At 14:41 EDT, the primary server hosting the EMS alarm processing application failed, due either to the stalling of the alarm application, 'queuing' to the remote EMS terminals, or some combination of the two." Operators "were unaware" the alarms had stopped — a **silent consumer stall**. The Register (secondary) reports the root cause GE found was a **race condition** in the alarm and event processing routine, reproduced only by slowing the system and injecting delays. **We attribute the race-condition detail to The Register's report of GE's findings (tier C) and the stall/queue/operator-unaware facts to the Task Force report (tier A).** Lesson: a consumer that stops silently turns a bounded queue into an unbounded delay; **heartbeat the consumer**.

## 2. Publish/subscribe and QoS (ROS 2 / DDS vocabulary)

ROS 2 documentation (rolling; T05, **P**) lists the QoS policies verbatim; the book reproduces them as a table:

| Policy | Values (docs) | What it decides |
|---|---|---|
| History | *Keep last* (queue depth N) / *Keep all* (bounded by middleware resource limits) | How many samples are stored for a slow reader |
| Depth | queue size, "only honored if the history policy was set to keep last" | |
| Reliability | *Best effort* ("may lose them if the network is not robust") / *Reliable* ("may retry multiple times") | Loss vs latency |
| Durability | *Transient local* (publisher persists samples for late joiners) / *Volatile* | What a late subscriber sees |
| Deadline | duration: "the expected maximum amount of time between subsequent messages being published to a topic" | Detects a publisher slower than promised |
| Lifespan | duration: max time between publish and reception before a message "is considered stale or expired (expired messages are silently dropped …)" | Age limit |
| Liveliness + Lease duration | automatic / manual by topic; "maximum period of time a publisher has to indicate that it is alive … (losing liveliness could be an indication of a failure)" | Failure detection |

- The same page lists events for incompatible QoS and liveliness lost/changed (T05).
- **Compatibility (request/offer):** a publisher offering weaker guarantees than a subscriber requests will not match (e.g. best-effort publisher with reliable subscriber). The matrix is in the ROS 2 docs; the book copies the rule in words and points to the page for the full table. (The compat table itself was in the page; lines after the policy list. We summarize only the two well-known cases: reliability and durability.)
- **Defaults** (ROS 2 docs): the base profile is described in the same page; the "sensor data" profile uses best-effort and a small depth. We say "sensor-data profiles are best-effort with a small depth" and tell the reader to read their framework's actual defaults.
- **Executor timing (S14, Casini et al. 2019, P):** the paper builds a response-time analysis for ROS 2's executor "under reservation-based scheduling" and treats its processing-chain behaviour as something that had to be reverse-engineered (the authors' talk: "uncovering ROS's undocumented timing behavior"). We use only: *callbacks in an executor are not scheduled by your RTOS priorities; the executor's own ordering matters for latency.* We did not re-derive their bounds.

## 3. Component/port models in NASA frameworks

- **F´ (JPL)** (T07, **P**):
  - Component kinds (cheatsheet/docs): **passive** (no queue, no thread), **queued** (queue, no thread), **active** (queue + thread).
  - Port kinds: **sync** (immediate call, no queue), **async** (placed in a queue, dispatched on the component's thread), **guarded** (mutex-protected).
  - `Svc::ActiveRateGroup` (SDD): "an active component that drives a set of components connected to `Svc::Sched` output ports. It contains an asynchronous input `Svc::Cycle` port. This port sends a message which wakes the component task. The task invokes each output port in order … It tracks execution time and detects overruns." Requirement ARG-004: "shall report a warning event when a rate group cycle is started before previous is completed".
  - This is a **cyclic executive with overrun detection**, hosted on a thread; rate groups at different rates are driven by a `RateGroupDriver` that divides a base tick (SDD downloaded; exact divider semantics to be confirmed when reading the framework).
- **cFS (NASA)** (T08, **P** overview-level): the core Flight Executive (cFE) provides software bus (pub/sub of CCSDS messages through **pipes**), time, events, executive services, tables. A NASA design review (NTRS) notes the SB limit of **256 message IDs** in one configuration (**S**, from search; configuration-specific). We do **not** state default pipe depths or scheduler frame numbers (not verified). The book says: *in cFS look at the Scheduler table (what runs when), the pipe depths (what is dropped when), and the subscription table (who hears what).*
- **ROS 2 lifecycle (managed) nodes** (T06, **P**): 4 primary states — **Unconfigured, Inactive, Active, Finalized**; 6 transition states (Configuring, CleaningUp, ShuttingDown, Activating, Deactivating, ErrorProcessing); 7 transitions exposed to a supervisor (create, configure, cleanup, activate, deactivate, shutdown, destroy); "Finalized … is always terminal". Managed service requests to an Inactive node are not answered. (Package docs list 5/5; the design page is authoritative for 6/7.)

## 4. Rates, harmonics and end-to-end latency

- **Choosing a control rate:** `ω_c·h = 0.2–0.6` rule of thumb (Åström & Wittenmark via Cervin thesis, S09/S24). Sampling faster than needed costs CPU; slower hurts control; latency + jitter degrade control (S09).
- **Harmonic rates** (e.g., 100, 50, 25, 10 Hz) make hyperperiods short and cause-effect chains predictable. Arithmetic.
- **Cause–effect chains and data age vs reaction time:** Feiertag et al. (2008) [S15, **Sn**]: control engineers care about the "maximum age of data" (worst-case age of the latest signal); body-electronics cares about "first reaction" (earliest signal). "Because the two can differ, a clear distinction is mandatory." Also: in automotive systems "register buffers and periodic sampling are far more common" than unbounded FIFOs. A related arXiv paper (1804.07647, downloaded) estimates latencies of task sequences in multicore ECUs; used only for the idea that end-to-end latency ≠ sum of response times because of sampling delay at each rate boundary.
- **Worked bound used in book:** for a register-based chain of tasks with periods T₁…Tₙ and response times R₁…Rₙ, a safe (loose) bound on *data age* is `Σ (T_i + R_i)`; reaction time can have a similar bound. We label this **a bound used in the book, in the spirit of Feiertag/Dürr, not a quotation**; Lab R10 measures actual end-to-end latency and compares.
- **Logical Execution Time (LET):** Giotto / AUTOSAR timing extensions fix the *observable* read/write instants so that timing is independent of execution jitter. Mentioned as a design choice; Henzinger's Giotto paper was **not** downloaded this pass (flag).
- **Ingenuity Flight 6 (C11, P):** NASA/JPL blog: "a glitch in the pipeline of images delivered by the navigation camera" dropped a single frame "causing all subsequent navigation images to be delivered with an erroneous timestamp"; estimates were repeatedly corrected for phantom errors and "large oscillations ensued"; roll/pitch excursions >20°; the helicopter landed safely and a software safeguard ignored images during descent. The Flight 8 post: the team's hypothesis that "the large CPU load involved in capturing the RTE's 13-megapixel color images could result in rare instances of navigation camera images being dropped"; planned fix "will address the Flight 6 anomaly, where image timing delays manifested into aircraft estimation and control challenges." **The lesson: a *dropped message + a timestamp that is assigned by position in a stream rather than carried with the data* corrupts every later message.** (Which framework layer assigned the timestamp is not stated in the posts; we do not claim F´ was involved in this bug — see `09-…`.)

## 5. Lifecycles

- **Task states (FreeRTOS)** (T01 ch. 4): Running, Ready, Blocked, Suspended (+ deleted/terminated pending cleanup by idle task). Verified in ch. 4 text.
- **Component lifecycle patterns** seen across frameworks: ROS 2 managed nodes (above); F´ topology construct → configure → start → run → stop; cFS app init → `CFE_ES_RunLoop` → exit (C: **not verified**, left to the handbook "ask how your framework starts and stops things"). The book teaches the *generic* lifecycle: **construct → configure → activate → run → deactivate → cleanup → destroy**, and the rule that configuration-time allocation is allowed but run-time allocation is not.
- **Message lifecycle (book model):** create → stamp (time, sequence) → publish → route → enqueue → dequeue → process → release/ack → (expire). Every arrow has a possible loss, delay, reorder or duplication; the handbook has a table to fill per message.
- **Apollo restart protection (C01)** as an extreme lifecycle example: *waypoints* register restart points; after restart, "only the most recent [incarnation of a job] was restarted".

## 6. Use in documents

| Item | Where |
|---|---|
| Queue arithmetic; Apollo; blackout | Book ch. 15; Lab H4, Lab R4 |
| QoS table | Book ch. 16; Handbook "message table" |
| F´/cFS/ROS 2 mapping | Book ch. 22; Handbook framework recon |
| Rate/harmonic rules; data age vs reaction time | Book ch. 17; Lab R10 |
| Ingenuity Flight 6 | Book ch. 17, 18 |
| Lifecycle models | Book ch. 18 |
