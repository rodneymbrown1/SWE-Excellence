# Family C · Build tasks {.chapter}

<p class="lede">Adding a feature is the same translation problem. You describe the new behavior in terms of what is already declared, defined, and implemented, then pin down the exact places where the change must go.</p>

## The standard build loop

1. **Run it.** See the *nearest existing behavior*. The feature will sit beside it.
2. **Understand it.** What should the new behavior look like, in things you can observe? Who relies on the old behavior?
3. **Card.** Write the feature as a **before and after**: "when P holds, afterwards Q holds." The card's EXPECTED line is the new behavior. Q′ (observed) is what happens *today* in the same situation.
4. **Probe.** LOG the writers and readers of the data the feature touches. Do not guess where the change goes.
5. **Pin it.** List every change point. Mark paths the log did not show.
6. **Build and prove.** Add the change. Show the new behavior in the run. Show the **old** behavior is unchanged.
7. **Log it.** Change points and the checks you used.

::: rule
**A feature is complete when every path that can reach the new behavior has been considered.** Not when the one path you tested works.
:::

## The six types

::: pb
### C1 · New behavior on a condition ("when X, do Y")
**Looks like** "When the link recovers, log how long the outage lasted."

**State signature** A new action Y attached to a state change or event X.

**First probe** TRAP the state that defines X (here `state_`) and LOG every writer with its line and call chain (chapter 11).

**Then** Check **every** way X can become true. In the practice program, "the link becomes Up" happens in two places (from Down, from Degraded). Hooking only one is the classic miss.

**Done when** Y runs on each path in the list, in a run that exercises each.

**Trap** Adding Y at the first path you find.
:::

::: pb
### C2 · New data or state ("keep track of Z")
**Looks like** "Remember when the outage began."

**State signature** A new variable with a lifecycle: created, set, reset, read.

**First probe** Declare Z on the card with its type, owner, and initial value. Find the events that **bracket** its life (where it must be set; where it must be read or cleared).

**Then** Use the writer log of the *related* state to find the brackets. Choose a sentinel for "not set" (for example `-1`) and handle it where Z is read.

**Done when** Z is set on every path that starts the thing it measures, read on every path that ends it, and cleared so it cannot go stale.

**Trap** Forgetting the reset. A value that is never cleared produces a wrong result on the *second* occurrence.
:::

::: pb
### C3 · Change a rule or threshold
**Looks like** "Degrade after 3 missed ticks instead of 4."

**State signature** The rule lives in a guard expression and often in a constant.

**First probe** Find the guard (`missed_ >= kDegradeAfter`) and **all** uses of the constant (`rg kDegradeAfter`). Characterize today's behavior first: save a log of the run (chapter 24's *golden log*).

**Then** Change the rule in one place. Re-run and diff the log: only the transitions you intended should move.

**Done when** The diff shows exactly the intended differences, and tests and docs agree.

**Trap** Changing the constant but not the comment, the test, or the second place that duplicates the number.
:::

::: pb
### C4 · New event or message type
**Looks like** "Handle a new `Reset` event."

**State signature** A new case in a dispatch point (a `switch`, a handler table, a registry).

**First probe** Pick the most similar existing event and follow it end to end (type A4). Its path is your template.

**Then** Add the new event along the same path. Turn on compiler warnings for missing `switch` cases (`-Wswitch`) so every place that must handle it is flagged.

**Done when** The new event travels the same stages as the template event, in a run you can show.

**Trap** Handling it at the dispatch point but not in the state machine that reacts to it.
:::

::: pb
### C5 · Connect to another module
**Looks like** "Report status to the logger service."

**State signature** Data crossing a boundary you do not own.

**First probe** Write the **contract** on the card: what you send, what you expect back, what you assume. Then LOG traffic across the boundary (the send and the receive) to learn what the other side *actually* does.

**Then** Stub the other side if you can, and test your half alone. Check the boundary in both directions.

**Done when** Your half works against the real thing *and* against a stub, and the assumptions are written down.

**Trap** Believing the interface description over the log.
:::

::: pb
### C6 · Refactor, same behavior
**Looks like** "Clean up this class." "Move this into its own file."

**State signature** The *state by event table* must not change.

**First probe** Record a **golden log**: run the probes and the program before you touch anything and save the output.

**Then** After each small step, run the same probes and `diff` against the golden log. Any difference is a behavior change, whether you meant it or not. This is Feathers's idea of a characterization test, done with probes.

**Done when** The diff is empty after the final step.

**Trap** Changing behavior "while you are in there."
:::

## How to find where the change goes, in one table

After the writer and reader logs, fill this in. It is the output of **Pin it** for a build task.

| Where (file:line) | What happens there | Seen in the run? | Needs the change? | Why |
|---|---|---|---|---|
| | | | | |

Rows with *seen = no* are the dangerous ones. Reason about them or make a run that reaches them.

## Check yourself

* What does "complete" mean for a feature?
* In C1, why do you list every way X can become true?
* What does a golden log give you that a unit test does not?
