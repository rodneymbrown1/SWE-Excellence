# Time: budgets, checkpoints, and when to ask {.chapter}

<p class="lede">When you get handed work you want to allocate time based on your process. Here is a way to do it: a starting split by family, checkpoints tied to the gates, and a rule for when to stop and ask.</p>

::: note
**Read this first.** The percentages in this chapter are **a proposal from this book, built from one research fact (comprehension takes more than half of developers' time on average) and common sense.** They are not a research result. Treat them as defaults to calibrate against your own journal.
:::

## The starting budgets

{{svg:time-budgets}}

| Step | A · Understand | B · Fix | C · Build |
|---|---|---|---|
| 1 Run it | 10% | 10% | 5% |
| 2 Understand it | 30% | 20% | 25% |
| 3 State it | 20% | 15% | 15% |
| 4 Probe it | 25% | 25% | 15% |
| 5 Pin it | 5% | 10% | 10% |
| 6 Prove it (includes the change) | 5% | 15% | 25% |
| 7 Log it | 5% | 5% | 5% |
| **Total** | **100%** | **100%** | **100%** |

**Why steps 1 to 3 are heavy.** Xia et al. measured about 58% of developer time as program comprehension in a field study of 78 professionals. A fix that skips understanding is not faster. It reaches the debugger without a condition to type. That is the reasoning behind giving steps 1 to 3 roughly 45 to 60 percent of the time.

**Why C spends more on step 6.** Building is mostly writing and checking the new behavior, plus confirming the old behavior survived.

## How to use it

1. After intake (chapter 16), choose a total time **T**. Pick the time you will work before you ask someone, not a promise of the finish.
2. Multiply T by each percentage.
3. Write the plan at the top of the card. Look at the clock at each step boundary.

Here is a 4-hour task in each family.

| Step | A · Understand | B · Fix | C · Build |
|---|---|---|---|
| 1 Run it | 24 min | 24 min | 12 min |
| 2 Understand it | 72 min | 48 min | 60 min |
| 3 State it | 48 min | 36 min | 36 min |
| 4 Probe it | 60 min | 60 min | 36 min |
| 5 Pin it | 12 min | 24 min | 24 min |
| 6 Prove it | 12 min | 36 min | 60 min |
| 7 Log it | 12 min | 12 min | 12 min |
| **Total** | **240** | **240** | **240** |

For a 2-hour task, halve these numbers. For a full day (8 hours), double them. The shape stays the same.

## Checkpoints tied to the gates

| Gate | When it should pass | A | B | C |
|---|---|---|---|---|
| Gate 1: Confidence | after steps 1 and 2 | by 40% | by 30% | by 30% |
| Gate 2: Card | after steps 1 to 3 | by 60% | by 45% | by 45% |
| Gate 3: Proof | after steps 1 to 6 | by 95% | by 95% | by 95% |

If a gate has not passed at its checkpoint, you are not behind on *tools*. You are behind on *knowledge*. Go to the stuck clock.

## The stuck clock

::: rule
**If any step has used 1.5 times its share, stop.** Do not keep going harder. Run the four-question reset, and then ask someone, within 15 minutes.
:::

**The four-question reset:**

1. **Is the expected behavior written down, with a source?** (If not, nothing else matters. Get it clarified.)
2. **Is the data on my card the data that matters?** Check by changing the data by hand and seeing whether the symptom responds.
3. **Can I make the problem smaller?** Fewer events, one instance, a shorter run (Agans: divide and conquer).
4. **What would I ask, and what is my best hypothesis?** Write both. (Alaboudi and LaToza: being offered a hypothesis made developers six times more likely to succeed in their experiment, so *bring one*.)

This is Agans's rule "Get a Fresh View" with a time limit attached. Asking after 15 minutes of structure is different from asking after four hours of flailing: you can hand the other person a card.

## Adjusting for unknowns

From chapter 16 (also a heuristic):

* 0 to 2 unknowns: use the defaults.
* 3 to 5: add about a quarter to step 2.
* 6 or more: do not start probing. Split the task or get the expected behavior clarified.

## Calibrate

Your journal (chapter 24) has columns for planned and actual minutes per step. After five tasks, look for patterns:

* A step that is *always* over: raise its share and lower another.
* A step that is *always* under: you are probably skipping part of it.
* Gate 1 failing late: your understanding step is shorter than it should be, or your sources (chapter 5) are too slow.

The goal is a split that is **yours**: one you can use to say "this will take about four hours, and here is where they go."

## Check yourself

* What is the 4-hour split for a fix? For a feature?
* What triggers the stuck clock?
* What is the difference between being behind on tools and behind on knowledge?
