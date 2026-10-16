# Worked example 3 · Build {.chapter}

<p class="lede">The task as handed over: "When the link recovers to Up, log how long the outage lasted." (This runs on the fixed build from chapter 21.) The skill is the same: describe the new behavior as before and after states, then find every place the change belongs.</p>

## Intake

* **Family C.** Types **C1** (new behavior on a condition: when the link becomes Up) and **C2** (new data: when the outage began).
* **First probe:** LOG every writer of `state_` with its line and call chain.
* **Time plan (4 h, Family C):** run 12 min, understand 60, state 36, probe 36, pin 24, build and prove 60, log 12.

## Step 1 · Run it

Run the fixed build and look at the nearest existing behavior: the `X -> Up` lines.

```out
[t=  3] Down     -> Up       (missed=0 good=3)
[t= 23] Up       -> Degraded (missed=4 good=0)
[t= 27] Degraded -> Up       (missed=0 good=2)
[t=123] Up       -> Degraded (missed=4 good=0)
[t=127] Degraded -> Down     (missed=8 good=0)
[t=134] Down     -> Up       (missed=0 good=3)
```

Two recoveries: **t=27** (from Degraded) and **t=134** (from Down, after a real outage). The feature must report on both. The first line, t=3, is the initial connection, not a recovery. It should *not* report an outage.

## Steps 2 and 3 · Understand and state

```
BEHAVIOR CARD — outage duration                         Family C · C1 + C2
RUN       ./gateway --max 400  -> "[t=134] Down -> Up"  (no duration printed today)
EXPECTED  When the link returns to Up after being off Up, print how many ticks it was off Up.
PURPOSE   Let an operator see how long each outage lasted.

DECLARE
  D1  state_         LinkState    exists (gateway.cpp:132)
  D2  now_           int          exists: current tick
  D3  outage_start_  int          NEW. tick when we left Up. -1 means "no outage open".

DEFINE
  P   state_ changes from Up to Degraded               -> set outage_start_ = now_
  Q   state_ changes to Up from Down OR from Degraded  -> print now_ - outage_start_, set -1
  I   outage_start_ >= 0 exactly while state_ != Up (except before the first connect)
  Q'  today: nothing printed

IMPLEMENT
  ? Every place state_ is written. Which of them are "leave Up" and which are "enter Up"?

PROBES
  P1 LOG+TRAP   log every write to state_ with line and caller      predict: I see the writers
```

## Step 4 · Probe it [RAN]{.ran}

The writer log from chapter 11, on the **fixed** build. The call chain is shortened here (`via` shows the function that wrote). The values and line numbers are the real output. The annotations in parentheses are mine, read from the code at those lines.

```out
state_ written -> Up        after line 115   via on_heartbeat   (Down -> Up)
state_ written -> Degraded  after line 97    via on_tick        (Up -> Degraded)
state_ written -> Up        after line 122   via on_heartbeat   (Degraded -> Up)   <- a new site: it ran this time
state_ written -> Degraded  after line 97    via on_tick
state_ written -> Down      after line 102   via on_tick        (Degraded -> Down)
state_ written -> Up        after line 115   via on_heartbeat   (Down -> Up)
```

A watchpoint reports the line *after* the write, so the writes are at lines 114, 96, **121**, 96, 101, 114 in the fixed file. Compare with chapter 11, where the same log, on the **buggy** build, had no line-122 entry. The fix made a fourth write site reachable.

## Step 5 · Pin it: the change-point table

| Where (fixed file, file:line) | What happens there | Seen in the run? | Needs the change? | Why |
|---|---|---|---|---|
| `on_tick` 96 | Up → Degraded | yes | **yes** | the outage starts: set `outage_start_ = now_` |
| `on_tick` 101 | Degraded → Down | yes | no | still the same outage |
| `on_heartbeat` 114 | Down → Up | yes | **yes** | the outage ends: report and clear |
| `on_heartbeat` 121 | Degraded → Up | **no, before the fix of chapter 21** | **yes** | the outage ends here too: report and clear |

::: trap
**The path the bug hid.** With the original (buggy) code, the Degraded → Up write (line 120 in the original file, 121 after the fix) never ran in this scenario. A feature hooked only where the log showed "Up" would have covered one of the two ways to recover. It would have *looked* complete in the test run, and been wrong in production the first time a short outage ended. This is why the table has a column for "seen in the run." Rows marked *no* are decided by reading the code.
:::

## Step 6 · Build and prove [RAN]{.ran}

The change has three parts, one for each row marked *yes*, plus the new field and a helper that reports and clears it (full patch: `solutions/02-feature-outage-duration.patch`).

```diff
       state_ = LinkState::Degraded;
       good_ = 0;
+      outage_start_ = now_;                 // outage begins
       announce(from);
 ...
         state_ = LinkState::Up;             // Down -> Up
         announce(from);
+        report_outage();
 ...
         state_ = LinkState::Up;             // Degraded -> Up
         announce(from);
+        report_outage();
 ...
+  void report_outage() {
+    if (outage_start_ < 0) return;          // first connect: there was no outage
+    std::printf("[t=%3d] link recovered after %d ticks\n", now_, now_ - outage_start_);
+    outage_start_ = -1;
+  }
+  int outage_start_ = -1;
```

New behavior, in the run:

```out
[t=  3] Down     -> Up       (missed=0 good=3)
[t= 23] Up       -> Degraded (missed=4 good=0)
[t= 27] Degraded -> Up       (missed=0 good=2)
[t= 27] link recovered after 4 ticks
[t=123] Up       -> Degraded (missed=4 good=0)
[t=127] Degraded -> Down     (missed=8 good=0)
[t=134] Down     -> Up       (missed=0 good=3)
[t=134] link recovered after 11 ticks
```

* **t=27:** 27 − 23 = 4 ticks. Correct, and from the *Degraded* path.
* **t=134:** 134 − 123 = 11 ticks. Correct, and from the *Down* path. The Down in the middle did not restart the clock.
* **t=3:** no report. The sentinel `-1` handled the first connect.

**Old behavior unchanged.** Remove the new lines from the output and compare with the output before the feature:

```
$ diff <(./gateway_feature --max 400 | grep -v recovered) <(./gateway_fixed --max 400)
$                                   # empty: identical apart from the new lines
```

[RAN]{.ran} Both ways into `Up` are covered, and nothing that already worked changed.

::: gate
**Gate 3: Proof for a feature** means two things: (1) the new behavior shows up on *every* path in the change-point table that your runs reach, and (2) the old behavior is byte-for-byte unchanged. Run a scenario that reaches each *no* row, or reason about it and say so in the journal.
:::

## Step 7 · Log it

```
JOURNAL   outage duration                C1 + C2
Change points: gateway.cpp 96 (start), 114 and 121 (report). Table in the card.
Hidden path:   Degraded -> Up (line 121 in the fixed file) was unreachable until the R5 fix. Feature depends on it.
Proof:         t=27 -> 4 ticks, t=134 -> 11 ticks, t=3 silent. Output diff vs fixed build: empty.
Saved:         lab/lldb/02-log-state-writes.lldb, solutions/02-feature-outage-duration.patch
Open question: should "Down" lasting longer than N ticks raise an alarm? (new card, not this one)
```

## Check yourself

* Why does the change-point table have a "seen in the run" column?
* What would have gone wrong if the feature had been built before the fix in chapter 21?
