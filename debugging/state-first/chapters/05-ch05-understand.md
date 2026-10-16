# Step 2 · Understand it {.chapter}

<p class="lede">At least half of any new task is reading the problem conceptually. If you do not know the purpose, the premise, and the desired state, you cannot turn them into data and conditions. This chapter makes that reading fast, bounded, and testable.</p>

## What "understand" means here

Not "I have read every function." It means you hold a small **theory** of the part you work on, in Peter Naur's sense: you can explain it, justify it, and respond to a change request. It is tested by **Gate 1** at the end of this chapter.

## Five questions

Answer each in one or two lines. Short answers are better than long ones.

| # | Question | Prompt | Practice program (the gateway) |
|---|---|---|---|
| 1 | **Purpose** | Why does this exist? Who or what uses its output? | Decide if the link to a peer is usable, so data is forwarded only when it is. |
| 2 | **Premise** | What must be true for it to work? What are the inputs and assumptions? | Events arrive in order: Tick, then Heartbeat, then Data. Heartbeats arrive every tick when healthy. |
| 3 | **Desired state** | What does "working" look like in things I can observe? | Rules R1 to R6 in `gateway.cpp`. For example R5: a link that is receiving heartbeats must not be declared Down. |
| 4 | **Boundary** | Which part is mine? What can I treat as a black box? | `LinkMonitor` and the data it holds. The event source and the Gateway are black boxes. |
| 5 | **Data path** | Where does the data enter, change, and leave? | Event in, `missed_` and `good_` change, `state_` out, read by `Gateway::dispatch`. |

## Where to get the answers, fastest first

| Source | What it gives you | Typical cost |
|---|---|---|
| The run you just did (step 1) | Real behavior | Done |
| Ticket, requirement, acceptance criteria | Desired state, in words | 5 min |
| **Declarations**: headers, class definitions, data members, enums | The nouns: what data exists and its types | 10 min |
| Existing tests | Executable examples of expected behavior | 10 min |
| Diagrams and design docs | Boundary and data path | 10 to 20 min |
| History: `git log -S missed_ -- path` and `git blame` | "What touched it last" (Google SRE's phrase) | 5 min |
| A person | What is *not* written down | One good question |

Read **declarations before implementations**. The header tells you what exists. The bodies tell you what happens. That is the Declare and Implement split you will use in chapter 6, applied to reading.

::: rule
**Ask with a hypothesis, not just a symptom.** "I think `missed_` should reset on every heartbeat but the Degraded path doesn't. Is that intended?" gets better answers than "the link is flaky." (Alaboudi and LaToza found that being offered hypotheses helped people succeed far more than being shown locations.)
:::

## How much is too much? The slice rule

You asked this directly: how much information is too much, how much too little, and if my module has no explicit messaging with others, can I ignore the rest?

::: rule
**The slice rule.** Read *completely* everything that reads or writes the data on your card (one hop). Treat everything else as a **black box with a written assumption** ("`EventSource` delivers Tick before Heartbeat within a tick"). Stop reading when you can fill the Behavior Card.
:::

This is our synthesis of two research findings: systematic readers did better on small programs, while experts on large ones read "as needed", driven by their goal (as described in a 2023 survey of the literature). So: be systematic *inside* a small slice, and as-needed outside it.

**Test a boundary.** Ask: *if I replaced module X with a stub that returns Y, would my task change?* If no, X is a black box. If yes, X is inside your slice.

**Signs you have read too little:**

* You cannot predict the next lines of output.
* The same question keeps coming back after you "read it".
* You are changing a value and the result surprises you.

**Signs you have read too much:**

* You are reading code that never touches the data on your card.
* You are drawing a diagram of the whole system for a task that touches one class.
* Half of your Understand time is gone and the card is still empty. Stop reading. Go probe (Agans: "quit thinking and look").

### "My module doesn't talk to the others. Can I ignore them?"

Not by messaging alone. Modules also interact through **shared state**. Check these, in this order:

1. Globals, statics, singletons
2. Shared queues, buffers, caches
3. Files, databases, configuration
4. Hardware registers and memory-mapped I/O (embedded)
5. Timing: priorities, timers, who runs when
6. The same lock or the same resource

If none of these intersects the data on your card, you can treat your task as pure logic. You can also **test it with the debugger**: watch the card's data during a full run and log who writes it (chapter 11). If every writer you see is inside your slice, the slice is closed. If an unexpected function appears in a backtrace, widen the slice by exactly that one function.

## If there are no diagrams, draw three

Ten minutes, on paper. These are the minimum.

```
1. CONTEXT: who talks to whom          2. DATA PATH: one value's journey
   +-------+     +-------+                input -> [stage A] -> [stage B] -> output
   | mine  |<--->| other |                          ^ where can it change?
   +-------+     +-------+                          ^ who else touches it?

3. STATE x EVENT TABLE (best form for event-driven code)
   | state \ event | Tick | Heartbeat | Data |
```

For event-driven systems the **state by event table** is the most valuable of the three, because it lists every cell you must reason about. Build it from the **requirements** (the desired state), not from the code. Then the code has something to be compared against. Here it is for the practice program, from rules R1 to R6:

| State \ Event | Tick | Heartbeat | Data |
|---|---|---|---|
| **Down** | `missed++` | `missed=0`; `good++`; if `good>=3` go Up (R1) | count; drop (R6) |
| **Up** | `missed++`; if `missed>=4` go Degraded (R2) | `missed=0` (R5) | count; forward (R6) |
| **Degraded** | `missed++`; if `missed>=8` go Down (R3) | `missed=0` (R5); `good++`; if `good>=2` go Up (R4) | count; drop (R6) |

Every cell is a claim you can check. In chapter 21 the probes will show that the code disagrees with exactly one of them.

Tools that help when you want them: your IDE's *Find All References* and *Call Hierarchy*, `rg` for visible strings, and Doxygen with Graphviz for call graphs (`CALL_GRAPH = YES`). A live `bt` in the debugger is also a call graph for one moment in time. [MANUAL]{.manual}

## Gate 1: the Confidence Gate

::: gate
**Pass all three before you leave step 2.**

**Explain.** Say the behavior in three plain sentences, with no "somehow" or "I think it kind of". Include why it exists.

**Predict.** Write down the next two lines of output before running again. Run. If you were wrong, you do not understand it yet, and the *difference* is your next question.

**Locate.** Name the module, one piece of data, and one candidate function where the behavior lives.
:::

These are Naur's three abilities (explain, justify, respond to a modification) as a pass/fail check.

## Time-box it

Understand takes about a quarter to a third of a task's time in the starting budgets of chapter 20. Spend **half of that reading**, then switch to probing. If the gate still fails after the full allocation, you are blocked on *knowledge*, not tools. Escalate (chapter 20).

## Check yourself

* Which of the five questions can you not answer for your current task?
* What is the boundary of your slice, and what assumption do you write down for each black box?
