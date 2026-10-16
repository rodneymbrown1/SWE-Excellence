<section class="part-title"><p class="pn">Part 7</p><div class="ph">Habits</div><p>Steps 6 and 7 in full, then how to work with other people and with AI tools without losing the discipline.</p></section>

# Steps 6 and 7 · Prove it and log it {.chapter}

<p class="lede">The work is not finished when the symptom disappears. It is finished when you can show why, and when the next person can repeat it. Proof makes the result trustworthy. The log makes the next task faster.</p>

## Step 6 · Prove it

### The seven checks

1. **The sentence was tested first.** You changed a value by hand and saw the symptom respond (chapter 15). If not, go back.
2. **The change is the smallest one that makes the sentence false.** One change at a time (Agans: "If you didn't fix it, it ain't fixed", and if you changed two things you cannot say which one did).
3. **The baseline run behaves.** Re-run step 1 exactly. `diff` the output against the saved run. The *only* differences should be the ones you intended.
4. **The same probes are silent.** Re-run the probes from your card. Read their **hit counts**. In chapter 21 the probe was evaluated 493 times and never stopped. That number matters: it proves the probe was alive.
5. **The probe could fire.** You saw it fire on the broken build. (Keep the old binary, or `git stash`, to confirm.) A silent probe means nothing until you have seen it fire.
6. **Neighbors are unchanged.** Run the tally probe (chapter 22) before and after, and diff. Cells you did not mean to touch must not move.
7. **The card is now code.** Next section.

### Turn the card into code: the permanent probe

A probe in your debugger disappears. The same condition, written as an `assert`, stays forever and runs on every build. The DEFINE line of your card is already the expression.

```cpp
// at the end of LinkMonitor::on_event:
// R5 as an executable invariant: after any Heartbeat is handled, missed_ is 0.
assert(!(e.type == EventType::Heartbeat && missed_ != 0) && "R5 violated");
```

I built the practice program both ways. [RAN]{.ran}

```out
(buggy build)
Assertion failed: (!(e.type == EventType::Heartbeat && missed_ != 0) && "R5 violated"),
  function on_event, file gateway.cpp, line 83.            exit status: 134

(fixed build)
final: state=Up forwarded=55 dropped=5 data_seen=153        exit status: 0
```

The bug now cannot return silently. This is the connection to **Design by Contract**: the invariant that was in your head is in the code, where it is checked, read, and run by everyone. For a longer-lived guard, or for code where an `assert` is compiled out in release builds, write a **unit test** with the same condition.

### Proof for a fix versus a feature

| | Fix | Feature |
|---|---|---|
| Show | The first bad state no longer occurs | The new behavior occurs on every path |
| And | The probe is silent and was seen to fire | The old behavior is unchanged (diff) |
| Keep | An assert or test of the invariant | A test for each path in the change-point table |

::: gate
**Gate 3: the Proof Gate.** Checks 1 to 6 pass, and you have decided what stays behind (an assert, a test, a saved probe). If you cannot say what would catch this if it came back, you are not done.
:::

## Step 7 · Log it

You do this *after every task*, in about 5 percent of the time. It is the cheapest step and the one most often skipped. Agans: "write down what you did, what order you did it in, and what happened as a result."

### The journal entry

```
JOURNAL  <date>   <task>                    type: ___
Cause / change:   one sentence ("X is Y because line L ...")
Fix / feature:    file:line, commit
Proof:            what you ran, what you saw (counts, diff)
Saved:            probe scripts, test names
Learned:          what you would tell the next person
First wrong assumption:  ______________________________
```

### The Hypothesis Ledger

Alaboudi and LaToza found that people hold few hypotheses (about two per bug) and that a correct early hypothesis predicts success. Writing them down makes the first one explicit and the wrong ones cheap.

| # | Hypothesis | Prediction | Probe | Result |
|---|---|---|---|---|
| H1 | Degraded branch does not clear `missed_` | `missed_` is 7 after the t=26 heartbeat | P1 FILTER | **confirmed** |
| H2 | | | | |

### Plan versus actual

| Step | Planned (min) | Actual (min) | Note |
|---|---|---|---|
| 1 Run | | | |
| 2 Understand | | | |
| 3 State | | | |
| 4 Probe | | | |
| 5 Pin | | | |
| 6 Prove | | | |
| 7 Log | | | |

After five tasks, read the "Actual" column across all of them. Which step is always over? Which is always skipped? That is how the budgets in chapter 20 become yours.

### Weekly, five minutes

Read the "First wrong assumption" line from each entry. Is there a pattern? A pattern here is worth more than any single fix.

### Commit messages

Put the sentence in the message. Whoever runs `git blame` later will thank you.

```
Fix false Down: clear missed_ on every heartbeat (R5)

Degraded branch cleared missed_ only after 2 heartbeats, so the next Tick
pushed it to 8 and the link went Down while heartbeats were arriving.
Found with a conditional probe at the end of on_event
(tools/probes/stale-missed.gdb); probe is silent on 493 events after the fix.
```

## Check yourself

* Which of the seven checks do people skip most? Which would you skip under pressure?
* What does a hit count prove that a silent run does not?
* What stays in the code after you finish?
