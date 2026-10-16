<section class="part-title"><p class="pn">Part 5</p><div class="ph">The three families</div><p>Every task is one of three kinds: understand, fix, or build. The seven steps are the same. The first probe and the time split change.</p></section>

# Intake: classify the task in five minutes {.chapter}

<p class="lede">When you are handed work, you want to allocate time based on a process. That starts with naming what kind of work it is. Five minutes of intake decides your first probe, your budget, and when you ask for help.</p>

## Three questions

1. **What is being asked?** To *explain* something (Family A), to make something *stop being wrong* (B), or to make it do something *new* (C).
2. **How sure am I of the expected behavior?** Can you write the EXPECTED line of the card, with a source? If not, your first job is step 2.
3. **How many unknowns?** Start a card, fill what you can, and count the `?` marks.

{{svg:intake-tree}}

## The eighteen types

Find the closest row. If two fit, you have a mixed task (see below).

| Type | It sounds like… |
|---|---|
| **A1** Who calls this? | "Where is this module used? Is that the only place?" |
| **A2** How does this module work? | "I don't know how this code works." |
| **A3** What controls it? | "Which variable do I change to get this behavior?" |
| **A4** Where does the data go? | "What happens to this value between input and output?" |
| **B1** Wrong value | "It shows 7 but should show 0." |
| **B2** Didn't happen | "The alarm never fires." "Nothing is logged." |
| **B3** Happened, shouldn't | "It sent the message twice." "It dropped the link while heartbeats arrive." |
| **B4** Wrong order or timing | "A should come before B." "Works alone, fails with two clients." |
| **B5** Stuck | "It hangs." "The loop never exits." "It never recovers." |
| **B6** Crash | "Segmentation fault." "Core dumped." |
| **B7** Only sometimes | "One run in fifty fails." |
| **B8** Slow or growing | "It gets slower." "Memory keeps climbing." |
| **C1** New behavior on a condition | "When the link recovers, log the outage length." |
| **C2** New data or state | "Track how many times the link flaps." |
| **C3** Change a rule | "Degrade after 3 missed ticks, not 4." |
| **C4** New event or message | "Handle a new `Reset` message." |
| **C5** Connect to another module | "Report status to the logger service." |
| **C6** Refactor | "Clean this up, same behavior." |

## The Intake Line

Write one line at the top of the card. It is the whole plan in a sentence.

```
INTAKE   B3 · first probe: FILTER at end of on_event · 4 h · 3 unknowns · check-in at 2 h
```

* **Type** from the table.
* **First probe** from the playbook (chapters 17 to 19).
* **Time** you will spend before you ask someone. Chapter 20 splits it.
* **Unknowns** from the card.
* **Check-in**: when you will tell your lead where you are.

## Unknown count: a rule of thumb

This is a heuristic from this book, not a measured result.

| Unknowns on the card | What to do |
|---|---|
| 0 to 2 | Go. |
| 3 to 5 | Add extra time to step 2. Your first job is to turn unknowns into names (chapter 8). |
| 6 or more | The task is not yet defined. Split it, or get the expected behavior clarified before you probe. |

## Mixed tasks

Most real tasks are a mix. Handle them in this order:

* **A bug fix usually contains an A.** "Why does X happen" often needs A2 (how does this module work) first. Do the A, then the B.
* **A feature often contains an A3 or A1.** To add behavior you must find what controls the related behavior and where it is called.
* **Do the smaller family first.** Understanding tasks are cheap and make the other two faster.
* **Write one card per behavior.** If you have two behaviors, you have two cards, even in one ticket.

::: try
Pick three tasks from your history: one bug, one feature, one "figure out how this works". Find their types. Which row had you spent the most time on without realizing what kind of task it was?
:::

## Check yourself

* What are the three questions at intake?
* When do you stop and clarify instead of probing?
* What goes on the Intake Line?
