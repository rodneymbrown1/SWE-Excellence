# Step 5 · Pin it {.chapter}

<p class="lede">You often know the module or component you are in, then start guessing which instance of a variable to change. Pinning ends the guessing. The goal is one sentence that names the exact line and the exact instance.</p>

## What "pinned" looks like

> *`missed_` stays at 7 after the Heartbeat at t=26, because `on_heartbeat` does not reset it when the state is Degraded.*

That sentence names **the data** (`missed_`), **the instance** (the one `LinkMonitor`, seen at tick 26), **the place** (`on_heartbeat`, the Degraded branch), **the condition** (state is Degraded), and **the reason** (it is not reset). You can test it. That makes it a hypothesis, not a hunch.

## Zeller's chain, as a search

Every failure you can see is the end of a chain. Each link is a **state**.

```
defect (a line of code)  ->  infection (the first bad state)  ->  ...  ->  failure (what you saw)
```

Your observed symptom (the link went Down) is the *failure*. Somewhere upstream is the *first bad state*, the **infection**. Everything between the infection and the failure is the infection spreading. Your job is to walk back until you reach the first state that is wrong, because the cause is in the code that produced exactly that state.

{{svg:pin-it}}

## The five moves (for a bug)

**1. Find the first bad observation.** Use the FILTER probe from your card. It stops at the earliest moment the rule is broken. Not the visible symptom, which comes later.

**2. Is the data bad on entry, or made bad inside?** At the stop, look at the arguments and the object (`info args`, `print *this`). Then look at the caller (`up`, `print`). If the data was already bad when this function started, the infection is earlier. If it was good on entry and bad now, the bad write is inside.

**3. If bad on entry, go up one stage and repeat move 1.** Same question, one stage earlier. This is bisection along the data path (Agans's *divide and conquer*; the SRE book's *bisection* of communication paths).

**4. If made bad inside, find the writer.** Read the function with the card beside it, and check which branch does not do what P and Q say. Or TRAP: put a `watch -l` on the data and log each write with its line (chapter 11). Compare the writes you see with the writes the Card says should happen.

**5. Name it.** Write the one sentence. Then test it.

::: rule
**Test the sentence before you edit any code.** Stop at the first bad state, change the value by hand, continue, and see whether the symptom goes away. That is the experiment in Zeller's loop: hypothesis, prediction, test.
:::

```
(lldb) expression missed_ = 0
(lldb) continue
[t= 27] Degraded -> Up       (missed=0 good=2)        <- the behavior the requirements ask for
```

[RAN]{.ran} Changing one value by hand turned `Degraded -> Down` into `Degraded -> Up`. The sentence survived the experiment. Now you are allowed to change the code (step 6). If it had not, you would revise the card.

## Which instance? (the "100 instances" problem)

Your original problem: a variable that shows up a hundred times, in several methods, through pointers, and in and out of a messaging system. Use these rules in order.

1. **Do not pick by name. Pick by state.** Let the FILTER probe stop *in* the instance that is wrong. `this` at that stop *is* your instance. (`print this` gives the address.)
2. **Record it.** `set $target = this` in gdb. In lldb, copy the address from `p this`. Now you can say "this one."
3. **Scope the next probe to it.** `condition N this == $target`, or `watch -l` on that object's field (which fixes one memory location).
4. **If data crosses a message boundary, follow the value, not the variable.** Tag it: a sequence number, an id, or any distinctive field. Put a LOG probe on the *send* and on the *receive*, filtered on the tag. The two log lines show the same message on both sides.
5. **If the instance is rebuilt or copied, re-find it.** Addresses change. A stable field (`id`, `name`) plus `$_streq` finds it again.

::: trap
**Changing "the variable that looks right."** A name that appears in ten places means ten candidate writes. Choosing one because the name matches is the guess this chapter exists to remove. Let the *first bad state* choose for you.
:::

## Pinning for a feature: find every change point

For a feature there is no bad state. You are looking for **where the new behavior has to go** and **everywhere that must agree with it**. The same probes answer it.

1. From the card, the feature is a *before and after*: "when the link returns to Up, report how long the outage lasted."
2. List the **writers and readers** of the data involved. Use the writer log from chapter 11.
3. For each writer, ask: is this a place my feature has to hook into?
4. Mark **paths the log did not show**. They are places the code *can* reach that your test run did not.

In the practice program, the writer log shows **three** places where `state_` is written during the run, but the code has **four**. One path, `Degraded` to `Up`, never ran, because the bug prevented it. A feature added at "the place the link becomes Up" would have been added to only one of two places. Chapter 23 walks through exactly this.

::: rule
**Runtime shows what ran. Reading shows what exists.** Use both. Compare the list of writers you *saw* with the list in the code. Every difference is a path you must reason about or exercise.
:::

## How long should this take?

About 5 to 10 percent of the task (chapter 20). Past 1.5 times that with no sentence, stop probing blindly. Re-check the card: is the **expected** value right, and is this really the data that matters? Or ask, with your best hypothesis in hand.

## Check yourself

* What is the difference between the failure and the infection?
* How do you know whether to go up one stage or look inside this function, and why test the sentence before you edit the code?
