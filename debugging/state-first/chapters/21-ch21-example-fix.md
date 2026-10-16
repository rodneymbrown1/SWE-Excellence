<section class="part-title"><p class="pn">Part 6</p><div class="ph">Proof by example</div><p>One small program. Three tasks: a fix, an understanding task, and a feature. Every command in these chapters was run, or is marked as not run.</p></section>

# Worked example 1 · Fix {.chapter}

<p class="lede">The task as handed over: "The link is reported Down for a few ticks even though heartbeats are arriving. Look at it around tick 27 in the test scenario." Seven steps, one bug.</p>

{{svg:lab-state-machine}}

## Intake (5 minutes)

* **Family:** B (fix). **Type:** B3, "happened but shouldn't": a transition to Down that the rules forbid.
* **First probe:** FILTER at the end of the function that updates the data.
* **Time plan (4 h):** run 24 min, understand 48, state 36, probe 60, pin 24, change and prove 36, log 12. (The probes below each run in well under a second. The point is that the *plan* says where the time goes, so you notice when you spend it elsewhere.)
* **Unknowns on the card:** three (what the observed `missed_` was; whether every branch clears it; where exactly the Down comes from). That is within the "go" range.

## Step 1 · Run it

```
cd lab && make && ./gateway --max 400
```

```out
[t=  3] Down     -> Up       (missed=0 good=3)
[t= 23] Up       -> Degraded (missed=4 good=0)
[t= 27] Degraded -> Down     (missed=8 good=0)
[t= 29] Down     -> Up       (missed=0 good=3)
[t=123] Up       -> Degraded (missed=4 good=0)
[t=127] Degraded -> Down     (missed=8 good=0)
[t=134] Down     -> Up       (missed=0 good=3)
final: state=Up forwarded=54 dropped=6 data_seen=153
```

**First oddity:** `[t= 27] Degraded -> Down`, only four ticks after `Degraded`. The scenario has a gap in heartbeats for ticks 20 to 25, so Degraded at t=23 is right. Then heartbeats come back at t=26. The link should recover, not drop. The second outage (t=120 to 131) is a real outage and *does* go Down. So the output alone cannot tell the two apart. The requirements can.

## Step 2 · Understand it

Rules R1 to R6 are in the comment block at the top of `gateway.cpp`. **R5** is the one at issue: *a link that is receiving heartbeats must not be declared Down.* The state-by-event table from chapter 5, built from the requirements, says that in **every** state a Heartbeat sets `missed` to 0.

**Gate 1.** *Predict*: "At the next Heartbeat while Degraded, `missed_` will be 0 and the link will go Up after two of them." That prediction is the claim the probes will test. Explain and locate pass (the card, chapter 6, names the module and the data).

## Step 3 · State it

The card is in chapter 6. Its key lines:

```
I  (always)   after any Heartbeat is handled, missed_ == 0
P1 FILTER     stop after on_event if e.type == Heartbeat && missed_ != 0     predict: never
```

## Step 4 · Probe it [RAN]{.ran}

```
breakpoint set -f gateway.cpp -l 81 -c 'e.type == EventType::Heartbeat && missed_ != 0'
run --max 400
```

**The prediction was wrong.** The probe fired:

```out
frame #0: gateway`LinkMonitor::on_event(this=…, e=…) at gateway.cpp:81:3
-> 81      }
(lldb) frame variable
(LinkMonitor *) this = 0x000000016fdfefec
(const Event &) e = 0x000000016fdfef90 (type = Heartbeat, tick = 26, payload = 0)
(lldb) p *this
(LinkMonitor)  (state_ = Degraded, missed_ = 7, good_ = 1, now_ = 26, data_seen_ = 8)
```

It stopped at **tick 26**, one tick *before* the visible Down. A Heartbeat was just handled, `state_` is `Degraded`, and `missed_` is still 7. That is the first bad state: the **infection**. The Down at t=27 is only the **failure**.

The equivalent gdb script is `lab/gdb/01-invariant.gdb`. [MANUAL]{.manual}

## Step 5 · Pin it

Follow the five moves from chapter 15.

* **Bad on entry or made inside?** `missed_` was 7 *before* the heartbeat (the previous tick made it 7), and it is still 7 after. The heartbeat handler did not change it. The data is not "bad on entry": 7 is a legitimate count after seven ticks without a heartbeat. The *handler's job* is to clear it. So the defect is inside `on_heartbeat`.
* **Which branch?** State is `Degraded`. `on_heartbeat` has three branches (Up, Down, Degraded).
* **Read the Degraded branch with the card beside it.** It increments `good_` and only clears `missed_` *inside* the `if (++good_ >= kRecoverAfter)` block. With one heartbeat, `good_` is 1, so `missed_` is not touched.

```cpp
} else {  // Degraded
  if (++good_ >= kRecoverAfter) {
    LinkState from = state_;
    state_ = LinkState::Up;
    missed_ = 0;            // <-- only cleared here, after TWO heartbeats
    announce(from);
  }
}
```

**The sentence:** *`missed_` stays at 7 after the Heartbeat at t=26 because the Degraded branch of `on_heartbeat` clears it only after two consecutive heartbeats; the next Tick makes it 8 and the link goes Down.*

**Experiment before editing.** [RAN]{.ran}

```
(lldb) expression missed_ = 0
(lldb) continue
[t= 27] Degraded -> Up       (missed=0 good=2)
```

With one value changed by hand, `Degraded -> Down` became `Degraded -> Up`, which is what R4 and R5 ask for. The sentence survived. Now you may edit.

## Step 6 · Prove it [RAN]{.ran}

The smallest change: clear `missed_` on every heartbeat in the Degraded branch. (Moving the `missed_ = 0` to the top of `on_heartbeat` for all states would also satisfy the rule. The fix below changes the least.)

```diff
     } else {  // Degraded
+      missed_ = 0;  // R5: a heartbeat always clears the missed-tick count
       if (++good_ >= kRecoverAfter) {
         LinkState from = state_;
         state_ = LinkState::Up;
-        missed_ = 0;
         announce(from);
       }
     }
```

Apply it (`patch -p1 < solutions/01-fix-missed-reset.patch`), rebuild, and run the baseline from step 1:

```out
[t=  3] Down     -> Up       (missed=0 good=3)
[t= 23] Up       -> Degraded (missed=4 good=0)
[t= 27] Degraded -> Up       (missed=0 good=2)
[t=123] Up       -> Degraded (missed=4 good=0)
[t=127] Degraded -> Down     (missed=8 good=0)
[t=134] Down     -> Up       (missed=0 good=3)
final: state=Up forwarded=55 dropped=5 data_seen=153
```

The false Down is gone. The real outage (t=127) is unchanged. Now the **same probe**, on the fixed build: it was evaluated on **493 events** (`hit count = 493`) and **never fired**.

::: gate
**Gate 3: Proof.** Two conditions, both met. (1) The probe *fired* on the broken build (at t=26), so we know it can detect the problem. (2) It stays silent on the fixed build across all 493 events. A probe that never fires proves nothing unless you have seen it fire.
:::

## Step 7 · Log it

```
JOURNAL 2026-10-16   gateway false Down        B3
Cause:   Degraded branch of on_heartbeat cleared missed_ only after 2 heartbeats (R5).
Fix:     missed_ = 0 at top of Degraded branch.  gateway.cpp:118
Proof:   probe 01 fired at t=26 before; silent for 493 events after. Output diff: t=27 Down -> Up.
Saved:   lab/lldb/01-invariant.lldb, lab/gdb/01-invariant.gdb
Learned: the visible failure (t=27) was one tick AFTER the first bad state (t=26).
Wrong hypothesis on the way: none this time (H1 held). Time: see plan vs actual in the journal.
```

## What made it fast

You never stepped through the loop. You never added a print. You never read a function you did not need. The card turned "the link drops when it should not" into one expression, and the debugger stopped on the first event that violated it.

## Check yourself

* Why was the stop at t=26 more useful than the visible Down at t=27?
* What two things did the proof need?
