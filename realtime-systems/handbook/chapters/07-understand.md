# Understanding a system you did not write {.chapter data-part="PART 4 · UNDERSTAND"}

<p class="lede">The goal is not to read all the code. It is to trace **one message** from where it is born to where it takes effect, and to know every wait, queue, lock and clock on the way. After that, the rest of the system is a set of neighbouring traces.</p>

## Trace one message

Pick the most important output of the system (a command to a motor, a value on a display, a telemetry packet). Then walk backwards and fill this chain for each hop.

| Hop | Question | Look for |
|---|---|---|
| **Sink** | where does it take effect, and by when must it? | the deadline / requirement |
| **Producer of the sink's input** | which task, at what rate and priority, produces it? | task table row |
| **Queue / shared data** | how does it get from producer to consumer? depth, policy, protection | queue and shared-data rows |
| **Earlier stages** | repeat until you reach… | |
| **Source** | the interrupt or sensor; its clock; where is it stamped? | interrupt table row; timestamp site |

Then compute: **worst-case data age** at the sink = Σ (T + R) along the chain (book ch. 17) and compare with the requirement. If the framework hides a hop (a middleware, an executor), find it in the documentation and write it in.

## Reading order for a code base

1. **Configuration** (kernel config; framework topology/launch/schedule). It lists the threads, rates, queues.
2. **Start-up code**: what is created, in what order, what is enabled last.
3. **Interrupt handlers**: short? what do they post?
4. **The tasks**: each loop: what does it wait on, what does it do, what does it post?
5. **Shared state**: grep for locks, critical sections, `volatile`, globals written by more than one flow.
6. **Error paths**: assert, hook functions, fault handler, watchdog feeding, reset.
7. **Logging and trace**: what exists to observe the system.

## Questions to ask the people (and the framework docs)

| Topic | Ask |
|---|---|
| **Rates** | Why is this component at this rate? What would break at half? At double? |
| **Deadlines** | What is the real requirement behind each deadline, and who owns it? |
| **Budgets** | Where do the execution-time numbers come from? Worst case, or typical? Measured on which hardware? |
| **Priorities** | Who assigned them and by what rule? Has anyone re-analysed since the last change? |
| **Queues** | What happens when this queue is full? Who would notice? |
| **Shared data** | Who else writes this? What stops a torn read? |
| **Start-up** | What must exist before this starts? What enforces the order? |
| **Failure** | What is the watchdog fed by? What does the system do on the third reset in a row? |
| **Observability** | What do you look at when this misbehaves? Is there a trace? A histogram? |
| **History** | What was the last timing bug here, and what changed afterwards? |

## Done when…

☐ You can name every task, its rate and priority from memory. ☐ You can trace the main message end to end with its worst-case age. ☐ You know what happens when each queue is full and when each task hangs. ☐ You know one way to see inside the running system. ☐ Your `?` list has owners.
