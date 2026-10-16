<section class="part-title"><p class="pn">Part 4</p><div class="ph">Probe it</div><p>Step 4, and the tools behind steps 5 and 6. How to look inside a program that never stops, and which probe answers which question.</p></section>

# Debugging a loop that never ends {.chapter}

<p class="lede">The basic recipe, <code>break main</code> then <code>next</code>, <code>next</code>, <code>next</code>, works for a program that runs and finishes. In a continuously running, event-driven system it fails. You need a different model.</p>

## Why stepping fails here

In your words: stepping through the loop can be useless, and can cause the state you are looking for to differ from what you expected.

* **The world keeps moving.** While you are stopped, real time passes. Timers expire, peers time out, buffers fill, a watchdog resets the device. When you resume, the system is not in the state it would have been in.
* **Iteration 40,000.** The thing you want happens deep into the run. Stepping gets you there in hours.
* **You change what you measure.** Agans's rule: use instrumentation to look at what is going wrong, but "don't change the mechanism; that's what's causing the failure."

## The model: a stream of events

Stop thinking of the program as a path you walk. Think of it as a **stream of events** flowing through code that changes state. You do not follow the stream. You **tap** it.

{{svg:stream-probes}}

A probe is a small instruction to the debugger: *when this happens, do that.* You attach several and let the program run at full speed. The debugger interrupts only for events you chose.

## Six verbs

| Verb | What it does | The question it answers | gdb | lldb |
|-----|-------|---------|-----------|-----------|
| **FILTER** | Stop only when a condition is true | *Show me the one event that breaks the rule.* | `break LOC if COND` | `breakpoint set … -c 'COND'` [RAN]{.ran} |
| **COUNT** | Tally events without stopping | *How often? Is it the 3rd time?* | a convenience variable, in a `commands` list | Python callback, return False [RAN]{.ran} |
| **LOG** | Print a line and keep running | *What values did it take over time?* | `dprintf`, or a `commands` list that ends in `continue` | Python callback, return False [RAN]{.ran} |
| **TRAP** | Stop when a piece of data changes | *Who writes this?* | `watch`, `rwatch`, `awatch` | `watchpoint set variable` [RAN]{.ran} |
| **ARM** | One probe switches another on | *Only after X has happened.* | `disable N`, then `enable N` in a `commands` list | Python callback calling `SetEnabled` (untested) |
| **REWIND** | Go back in time from a bad state | *The state is bad now. What made it so?* | `reverse-continue` with `rr` or `record` | no equivalent used here |

Everything in the rest of Part 4 is a detail of one of these six verbs.

## Fundamentals you may be missing

You asked whether there are other basic strategies besides breakpoints and watchpoints. Here is the whole list, in the order they tend to pay off. The first two you already have.

| # | Strategy | Why it matters in a loop |
|---|---|---|
| 1 | Conditional breakpoint | You have it. The workhorse. |
| 2 | Watchpoint | You have it. Follows data, not code. |
| 3 | **Ignore count / hit count** | "Skip the first 1,000 passes", or "stop on the 25th." |
| 4 | **Logging without stopping** (`dprintf`, `commands` + `silent`) | Observe the stream with no stop and no rebuild. The debugger version of `printf`. |
| 5 | **One-shot breakpoints** (`tbreak`, `enable once`) | Stop once, then stay out of the way. |
| 6 | **Counters** (convenience variables) | Measure frequency and rank causes. |
| 7 | **Arming** | Watch a variable only after a trigger event. Cuts noise by orders of magnitude. |
| 8 | **Scope filters**: caller, instance, thread | Isolate "this one object" or "only via this path." |
| 9 | **Read and access watchpoints** (`rwatch`, `awatch`) | Find the code that *consumes* a value, not just the code that writes it. |
| 10 | **Catchpoints** (`catch throw`, `catch signal`, `catch syscall`) | Stop on an event class, not a line. |
| 11 | **Change a value by hand** (`set var`) | Test a hypothesis in seconds, before touching source. |
| 12 | **Reverse execution / record and replay** | Go from "bad now" back to "who wrote it." |
| 13 | **Post-mortem** (core dumps) | Examine a crash you cannot reproduce at your desk. |
| 14 | **Scripts and the Python API** | Make probes repeatable and shareable (chapter 14). |
| 15 | **Non-debugger tools**: assertions, structured logs, hardware trace | Some systems cannot be halted at all. See the box below. |

::: rule
**The three that change your week most are #4 (log without stopping), #7 (arming), and #11 (change a value by hand).** Learn those first.
:::

::: trap
**On real hardware, a stop halts the processor.** A breakpoint that stops and resumes still pauses the CPU for a moment, which may disturb timing, peripherals, or a watchdog. Use `dprintf` and logging probes sparingly on time-critical code. Non-intrusive tracing exists (hardware trace and tools built on it), but I have not verified specifics for them and they are outside this book. Ask your hardware team what your target supports.
:::

## One question per probe

Every probe answers a single question and carries a prediction. Write them on the card as you go.

```
PROBE CARD
Q:          Does missed_ ever stay non-zero after a heartbeat?
Verb:       FILTER
Place:      end of LinkMonitor::on_event (gateway.cpp:81)
Condition:  e.type == Heartbeat && missed_ != 0
Predict:    never fires
If it fires: the invariant is broken. Note state_, tick, and what comes next.
If silent:   the probe may be wrong. Check that it can fire (chapter 7).
```

If you cannot write the prediction, you are not ready to run the probe. Go back to the card.

## The probe chooser

Start from what you know, not from the command you remember.

| You know… | You want… | Use |
|---|---|---|
| A **place**, and the data looks wrong there | The first bad moment | FILTER |
| A place that runs thousands of times | The Nth time, or after a warm-up | Ignore count, or COUNT plus a conditional |
| A place, and you do not want to stop | Values over time | LOG |
| A **piece of data**, not a place | Who changes it | TRAP (`watch -l`) |
| A piece of data, and only bad values matter | Filter the writes | TRAP with a condition |
| A piece of data, and you want its **consumers** | Who reads it | `rwatch` or `awatch` |
| Something rare that happens **after** an event | Only look then | ARM |
| An event class (exception, signal, system call) | Stop when it occurs | `catch …` |
| The state is bad **now**, the cause was earlier | Go back | REWIND |
| A crash you cannot reproduce live | The state at death | Core dump |
| A guess about the cause | Test it without editing | `set var`, then `continue` |

## Check yourself

* Why can stepping through an event loop give you a misleading picture?
* Name the six verbs. Which one do you use when you know the data but not the place?
