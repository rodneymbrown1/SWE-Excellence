# Family B · Fix tasks {.chapter}

<p class="lede">A bug is behavior: the system will not do something it should, or does the opposite of what you want. Describe the behavior as a state, find the <em>first</em> bad state, and everything else follows.</p>

## The standard fix loop

Every B type uses the same loop, with a different first probe.

1. **Run it.** Reproduce. Save the run record.
2. **Card.** Expected, observed, Declare, Define (P, Q, I).
3. **First probe** from the type (below). **Predict first.**
4. **Pin it.** First bad state, then the one sentence (chapter 15).
5. **Experiment.** Change a value by hand (`set var`) and see if the symptom changes.
6. **Change the code.** The smallest change that makes the sentence false.
7. **Prove it.** Re-run the same probes; they must be silent. Prove they could fire (chapter 24).

## The eight types

::: pb
### B1 · Wrong value
**Looks like** "It shows 7 but should show 0."

**State signature** Variable `v` has a value that violates Q at a known place.

**First probe** FILTER at that place: `break PLACE if v != EXPECTED` (or the rule as an expression).

**Then** `up`, compare arguments to the wrong value. Bad on entry: go up one stage. Made inside: TRAP the writes to `v`.

**Done when** You can name the line that produces the first wrong value.

**Trap** Fixing where the wrong value is *shown* instead of where it is *made*.
:::

::: pb
### B2 · Didn't happen ("why didn't it?")
**Looks like** "The alarm never fires." "Nothing is logged." "The second message is never sent."

**State signature** The action A never ran, so either its guard G was false or G was never evaluated.

**First probe** Breakpoint on A. If it has **zero hits**, go up. Break at the **decision** that should lead to A, and log each operand of G.

**Then** Find the first operand that is not what the rule says. If the decision is never reached, repeat one stage up the call chain.

**Done when** You can say which operand made G false, or which call never happened.

**Trap** Putting the probe on the action. If it never runs, the probe never fires and tells you nothing. Probe the *decision*. (This is the Whyline's *why didn't* question, by hand.)
:::

::: pb
### B3 · Happened but shouldn't have
**Looks like** "It dropped the link while heartbeats were arriving." "It sent the message twice."

**State signature** Action A ran while the rule says G_expected was false.

**First probe** Breakpoint at A with `if !(G_expected)`. A `bt` shows *which path* led here.

**Then** Compare the guard that let it through with G_expected. The guard is too loose, or reads stale data (`missed_` in the practice program).

**Done when** You can show the exact state in which A ran and say which part of the guard was wrong.

**Trap** Stopping at the first path you find. There may be two callers. Check `bt` each time (chapter 8).
:::

::: pb
### B4 · Wrong order, timing, or race
**Looks like** "S2 happened before S1." "Fine with one client, fails with two."

**State signature** Events or writes interleave in an order the rule forbids.

**First probe** LOG both events with a sequence number or timestamp. Compare the order. For threads, log the thread id too.

**Then** ARM: break at S1, enable the probe on S2. If it is a data race, TRAP the shared data with `watch -l`, and use `thread` scoping. Consider rr for replay.

**Done when** You have a log that shows the bad order, and the lock or ordering rule that should have prevented it.

**Trap** Stopping changes timing. Prefer logs and counters to long stops. A race that disappears under the debugger is data.
:::

::: pb
### B5 · Stuck, never settles
**Looks like** "It hangs." "The loop never exits." "The link never recovers."

**State signature** A state with no way out, or a progress variable that stops changing.

**First probe** Let it hang. Interrupt (Ctrl-C). `bt` and `thread apply all bt`. Where is it spinning or waiting?

**Then** Put a TRAP on the progress variable. If it never fires, nothing is progressing. Add a **tripwire**: break when an iteration counter passes a limit.

**Done when** You can name the state it is stuck in and the transition that should have left it.

**Trap** Assuming a hang is a loop. It is often a wait (a lock, a read) with nothing to wake it. `bt` tells you which.
:::

::: pb
### B6 · Crash
**Looks like** "Segmentation fault." "Core dumped."

**State signature** A signal at a line. The line is the *failure*, rarely the cause.

**First probe** Run under the debugger; it stops at the signal. `bt`, then `up` to the frame with the bad pointer or index.

**Then** Where did that value come from? That is a TRAP question: restart with `watch -l`, or use rr and `reverse-continue`. For a field crash, use the core dump (chapter 13).

**Done when** You can name where the bad value was created, not only where it was used.

**Trap** Adding a null check at the crash site. That hides the infection and moves the failure.
:::

::: pb
### B7 · Only sometimes
**Looks like** "One run in fifty fails."

**State signature** Behavior depends on something you are not controlling: timing, threads, uninitialized data, input.

**First probe** Make it deterministic: fixed seed, single thread, fixed input (step 1). Run it in a loop until it fails and keep the *failing* log.

**Then** Compare a failing log with a passing one (Agans: compare a bad run to a good one). `diff` them. The first difference is your lead. Record the failing run with rr if you can.

**Done when** You have a failing run you can replay, and you have found the first difference.

**Trap** Debugging the run that passed.
:::

::: pb
### B8 · Slow or growing
**Looks like** "It gets slower." "Memory keeps climbing."

**State signature** A resource grows or a rate drops over time.

**First probe** **Measure first.** Pike's rules: "You can't tell where a program is going to spend its time" and "Don't tune for speed until you've measured." Use a profiler or a memory tool, not a guess (your `handbook/` chapter 09 covers profilers). In gdb, hit counts (`info breakpoints`) show which paths run unexpectedly often.

**Then** Once the tool names a hot spot or a growing allocation, switch to B1 on it: what value or count should it have been?

**Done when** A measurement, not an opinion, shows the cause.

**Trap** Optimizing the code that looks slow.
:::

## Two habits that apply to every B

::: rule
**Look for the first bad state, not the loudest symptom.** The failure is far downstream. The cause is the first state that violates the rule.
:::

::: rule
**One change at a time.** If you change two things and the bug goes away, you do not know which one fixed it (Agans). Make the change, run the probes, then make the next.
:::

## Check yourself

* Which type is "the screen never refreshes"? Where does the probe go?
* Why is a null check at the crash site usually wrong?
* How do you debug a bug that only happens one run in fifty?
