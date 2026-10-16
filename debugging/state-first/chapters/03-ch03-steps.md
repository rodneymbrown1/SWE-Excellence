# The seven steps {.chapter}

<p class="lede">One flow for every task. Bug, feature, or "I just need to understand this" all go through the same seven steps. What changes is the first probe and how you split your time.</p>

{{svg:seven-steps}}

## The steps in plain language

**1. Run it.** Build with debug symbols, run the program, and watch what it does. Write down the command, the input, and the output you saw. This is always first. You are looking at behavior, not code.

**2. Understand it.** Decide what the code is *for* and what "working" looks like, then decide which part of the system is yours. This is at least half reading the problem conceptually. If you do not understand the purpose, the premise, and the desired state, you cannot turn them into data and conditions.

**3. State it.** Translate the behavior into the three building blocks: **Declare** (what exists), **Define** (what must be true), **Implement** (what changes it). Write them on the **Behavior Card**. Anything you do not know yet becomes a `?` on the card.

**4. Probe it.** Aim the debugger with the card. Each `?` and each condition becomes a probe: a conditional breakpoint, a watchpoint, a counter, a log line. Write your prediction first.

**5. Pin it.** Use the probes to find the *first bad state* (for a bug) or the *change points* (for a feature): the exact instance and line. End with one sentence naming it.

**6. Prove it.** Test your sentence cheaply (change a value by hand in the debugger), make the smallest real change, then run the *same probes* again. They should now be silent. You must also have seen them fire on the old code.

**7. Log it.** Record what you did, what you learned, and save the probe scripts. This is how the next task gets faster.

## The three gates

A gate is a pass/fail check. If you cannot pass, do not move on. Going on anyway is how the time disappears.

::: gate
**Gate 1: Confidence (after step 2).** Can you *explain* the behavior in three plain sentences? Can you *predict* the next thing the program will print? Can you *locate* the module, the data, and a candidate function? (Chapter 5.)
:::

::: gate
**Gate 2: Card (after step 3).** Is every line testable? Does it name data, a place, and a condition? Are unknowns marked `?` with a plan for each? (Chapter 6.)
:::

::: gate
**Gate 3: Proof (after step 6).** Did you see the probe fire on the broken code and stay silent on the fixed code? Does the original run now behave? (Chapter 24.)
:::

## Why this order

* Step 1 before step 2 because you can only understand a system you have watched. Reading code first is how you get lost in a code base.
* Step 2 before step 3 because the card needs *meaning* (purpose, expected values). You cannot invent expected values.
* Step 3 before step 4 because the debugger needs *names and conditions*. Without them you stop at random places.
* Step 5 before step 6 because a fix applied before you can name the exact place is a guess that happens to compile.

## The same steps, three kinds of task

| Step | Understand (Family A) | Fix (Family B) | Build (Family C) |
|---|---|---|---|
| 1 Run | See the behavior you must explain | Reproduce the bug | See the nearest existing behavior |
| 2 Understand | Purpose and boundary | What should have happened | Desired new behavior and where it lives |
| 3 State | State machine or data path | Expected vs observed state | New behavior as before/after states |
| 4 Probe | Log who touches the data | Conditional stop at the bad state | Log writers and readers near the change |
| 5 Pin | The map is complete | First bad state, exact line | Every place the change must go |
| 6 Prove | Explain it back; predictions hold | Probe silent after fix | New behavior observed; old behavior unchanged |
| 7 Log | Diagram and summary | Cause and fix | Change points and tests |

## Time

Where does the time go? Measured averages say more than half of a developer's time is comprehension. Do not budget the steps equally. The starting defaults (chapter 20) put roughly **45 to 60 percent of the time into steps 1 to 3**, because that is what makes steps 4 to 6 fast. These percentages are a starting proposal from this book, **not a research result**. Calibrate them with your own journal.

## Check yourself

* Which step do you usually skip? What did it cost last time?
* State Gate 1 in your own words, without looking.
