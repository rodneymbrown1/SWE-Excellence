# Worked example 2 · Understand {.chapter}

<p class="lede">The task as handed over: "You are taking over <code>LinkMonitor</code>. Where is it called from? Is that the only place? Under what conditions? And how does it work?" This is the start of the book's own wording: "I don't know how this code works" and "I don't know where this code is called."</p>

## Intake

* **Family A.** Types **A1** (who calls this) and **A2** (how does it work). The deliverable is a map, not a change.
* **First probes:** LOG the callers, and tally which *(state, event)* combinations really occur.
* **Time plan (4 h, Family A):** run 24 min, understand 72, state 48, probe 60, pin 12, prove 12, log 12. Note how much more of the time goes to understanding than to probing.

## Steps 1 and 2 · Run it, understand it

The run is the same as in chapter 21. The purpose, premise, and desired state are the five answers from chapter 5. The state-by-event table built from the requirements is the *expected* map. Our job is to compare it with what the program does.

## Step 3 · State it (A1)

```
Q:       Who calls LinkMonitor::on_event? Only one place? Under what conditions?
DECLARE  LinkMonitor::on_event(const Event&)   gateway.cpp:74
DEFINE   caller set = {...}   each caller with the condition that leads to it
?        callers not exercised by a normal run
```

## Step 4 · Probe it

### First, the static answer

A text search shows what *exists* in the code. [RAN]{.ran}

```
$ grep -n "on_event(" gateway.cpp
74:  void on_event(const Event& e) {
159:    monitor_.on_event(e);
170:      monitor_.on_event(extra);
```

One definition and **two call sites**: line 159 and line 170. Static search cannot tell how often each runs, or when.

### Then the runtime answer

Log the caller of every call, and tally. In gdb this is the commands list from chapter 8. In lldb it is a Python callback. [RAN]{.ran}

```out
callers of LinkMonitor::on_event (function:line  count)
  Gateway::dispatch(Event const&):159     400
  Gateway::flush_burst(Event const&):170  93
```

Two callers, as the search said. `dispatch` is called once per event in the loop (400 events). `flush_burst` is the **rare path**: 93 calls, in groups of 3, so 31 bursts.

### What selects the rare caller?

Break only when the caller is `flush_burst`. [RAN]{.ran}

```out
(lldb) bt
* frame #0: gateway`LinkMonitor::on_event(this=…, e=…) at gateway.cpp:75:12
  frame #1: gateway`Gateway::flush_burst(this=…, e=…) at gateway.cpp:170:16
  frame #2: gateway`Gateway::dispatch(this=…, e=…) at gateway.cpp:163:28
  frame #3: gateway`Gateway::run(this=…) at gateway.cpp:147:7
  frame #4: gateway`main(…) at gateway.cpp:186:6
(lldb) p e
(const Event &) 0x000000016fdfef60 (type = Data, tick = 90, payload = 99)
```

The first time it happens: tick 90, a `Data` event with `payload = 99`. Reading `dispatch` confirms the rule: a Data event with `payload >= 99` calls `flush_burst`, which feeds three extra Data events to `on_event`. The condition that selects the rare caller is **`Data` and `payload >= 99`**. In gdb: `break LinkMonitor::on_event if $_caller_matches(".*flush_burst")`, or, without Python, `break gateway.cpp:170`. [MANUAL]{.manual}

::: why
**A finding that reading alone would likely have missed.** The summary line says `data_seen=153`, but `forwarded=54` plus `dropped=6` is 60. Two counters that look like they should agree do not. The caller tally explains it: 153 − 60 = **93**, exactly the number of calls from `flush_burst`. `data_seen_` counts the synthetic burst events as well. Whether that is a bug or intended is a question for the owner. The point is that the probe found the question.
:::

## Step 4 (continued) · A2: how does it work?

Tally every *(state, event)* pair that occurs. [RAN]{.ran} Compare with the table from the requirements.

```out
observed state x event (count of events seen in that state)
                 Tick  Heartbeat     Data
  Down             12          9        9
  Up              160        150      135
  Degraded          8          1        9
```

What this tells you, and what it does not:

* **Every cell was reached at least once.** The scenario exercises the whole table.
* **`Degraded` by `Heartbeat` was reached exactly once.** It is the thinnest cell, and the one with the bug (chapter 21). A cell with one observation is a claim you have barely tested.
* **Counts show coverage, not correctness.** To check correctness you compare each cell's *outcome* with the requirement table. For `Degraded` by `Heartbeat` the requirement says `missed = 0`, and the FILTER probe in chapter 21 showed it was not.

## Step 5 · Pin it

For an understanding task, "pinned" means the map is complete: who calls, under which conditions, and where the state changes. The writer log from chapter 11 gives the last piece: state changes happen at **four sites** in the code, `on_tick` (2) and `on_heartbeat` (2), and only three of them ran in this scenario.

## Step 6 · Prove it (explain it back)

For Family A, "prove" means you can *predict*. Before running the next scenario, write down: "The next time `Data` arrives with `payload >= 99`, `data_seen_` will increase by 4 (1 plus 3 burst events) while `forwarded_` or `dropped_` increases by 1." Then check it.

## Step 7 · The deliverable

```
MODULE      LinkMonitor  (gateway.cpp)
PURPOSE     Decide link health from ticks and heartbeats so data flows only on a healthy link.
STATE       state_ {Down, Up, Degraded}, missed_, good_
EVENTS      Tick, Heartbeat, Data                    (state x event table: see chapter 5)
CALLED BY   Gateway::dispatch   every event          (gateway.cpp:159)
            Gateway::flush_burst rare: Data with payload >= 99, 3 synthetic Data events (gateway.cpp:170)
WRITERS     state_ at lines 96, 101, 114, 120        (on_tick 2, on_heartbeat 2)
OPEN        data_seen_ includes burst events: intended?   Only 1 observation of Degraded x Heartbeat.
```

::: rule
**Static and runtime together.** Search showed what exists. The probe showed what ran. The gap between them (in this case, a rare path and a rarely-seen cell) is where the surprises are.
:::

## Check yourself

* Which two tools gave you the callers, and what does each one not tell you?
* How did the caller tally explain the mismatch between `data_seen` and `forwarded + dropped`?
