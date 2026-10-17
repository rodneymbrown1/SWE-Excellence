# Lifecycles: components and messages {.chapter data-part="PART 4 · FLOW"}

<p class="lede">Every component is born, configured, run, stopped and destroyed, and every message is created, stamped, queued, processed and released. Bugs live in the transitions: the queue that does not exist yet when the first message arrives, the resource released while a message still points at it, the restart that forgets what it was doing.</p>

## A component's life

{{fig:lifecycle | A generic lifecycle, shaped like the ROS 2 managed-node design. Allocation belongs in configure; processing only in Active; nothing allocates while Active.}}

| State | What may happen | What must not |
|---|---|---|
| **Unconfigured** | constructed; no resources | processing |
| **Inactive** | configured: memory allocated, queues created, subscriptions made, hardware opened | publishing live data; accepting service requests |
| **Active** | timers running, messages processed and published | allocation; reconfiguration |
| **Finalized** | terminal; resources released | anything |

The ROS 2 design lists four primary states (**Unconfigured, Inactive, Active, Finalized**), six transition states, and seven transitions exposed to a supervisor (*create, configure, cleanup, activate, deactivate, shutdown, destroy*); "Finalized" is "always terminal". The vocabulary differs between frameworks (F´ topologies construct, configure and start components; cFS starts apps from a startup list; AUTOSAR has ECU-state management), but the structure repeats. **Read the lifecycle documentation of your framework before you read any component.**

### The ordering problems

| Problem | Example | Class (Lu et al.) |
|---|---|---|
| **Consumer before queue** | a task starts reading a queue that another task has not created | order violation |
| **Producer before consumer is ready** | an interrupt enabled before the task that drains it | order violation, then overflow |
| **Subscriber before publisher** | no data yet; a late joiner sees nothing (durability) | startup race |
| **Release while in use** | a buffer freed while a message still points at it | use-after-free |
| **Two components start each other** | A waits for B's topic; B waits for A's service | startup deadlock |

Fixes are structural: **create everything in a defined order**; **start sinks before sources**; **gate activation on readiness** (a state, not a sleep); **release in the reverse order**. A `vTaskDelay(100)` "to let the other task start" is a race with a long fuse.

### Restart is part of the lifecycle

::: case
**Apollo 11: restart protection.** The guidance software was designed so the computer "could literally be turned off and back on without interrupting" the landing. The mechanism was **waypoints**: at suitable points a job registered where it could safely restart, so that "if processing happened to jump back to the last waypoint, no error would be introduced." After a restart, "processing would commence at the last registered waypoint", only the **most recent copy** of a job was restarted, and non-critical, non-protected functions were simply dropped. Designed against hardware glitches, it also turned out to shed overload (chapter 11).
:::

For every component decide: **what is its state after a restart?** (nothing; reloaded from storage; reconstructed from neighbours); **how does it know it restarted** (a counter, a reset-reason register); **what do its neighbours do meanwhile**. The Spirit rover's boot loop (chapter 14) is the cautionary tale: start-up code that fails *every* time cannot be fixed by restarting it.

## A message's life

{{fig:msg-lifecycle | A message's life and where it goes wrong. Every arrow needs an owner, an age limit and a named behaviour when it cannot keep up.}}

| Stage | Who owns the message | What can go wrong | What to check |
|---|---|---|---|
| **Create** | the producer | allocation fails; fields uninitialised | pool depth; checked allocation |
| **Stamp** | the producer | timestamp taken late, from the wrong clock, or by position | stamp where measured, with a named clock (ch. 17) |
| **Publish** | hand-off | rate faster than promised | rate monitoring; deadline QoS |
| **Route** | the framework | wrong subscribers; duplicates | subscription table |
| **Enqueue** | the queue | full → drop or block | policy, counter (ch. 15) |
| **Dequeue** | the consumer | consumer late; item aged out | age check on dequeue |
| **Process** | the consumer | exceeds budget; blocks | budget, timeout |
| **Release** | the last owner | freed twice, or never | single owner; pool accounting |

If you can fill in this table for one message in your system, you understand that data path. [RAN]{.ran} Lab R10's pipeline has four of these arrows (ISR → raw queue → filter → shared attitude → control → command queue → actuator); the defects planted in it are a missing *Enqueue* counter, a read at two *Process* times, and a *Process* stage with the wrong priority.

## Observing a lifecycle

| Technique | Use |
|---|---|
| **State variable + log on every transition** | the first thing to add; transitions are rare, so logging is cheap |
| **Reset reason + boot counter in `.noinit`** | tells the next boot why the last one ended (chapter 19) |
| **Readiness flag per component** | gates neighbours instead of sleeps |
| **Queue depth and age at start-up** | catches "producer ran ahead" |

## Check yourself

::: check
1. List the start-up order of three components that exchange messages. What breaks if you reverse it? What enforces the order today: code, a configuration file, a delay?
2. A component restarts. What does it publish first? What do its subscribers do with a gap?
3. Trace one message end to end in your system with the table above. Where is the first arrow you cannot fill in?
:::
