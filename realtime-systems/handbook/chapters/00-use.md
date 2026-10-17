# How to use this handbook

<p class="lede">Open it when you are handed a device and a task. It does not teach; the book does. It tells you what to do next, what to ask, and what to check, in the order that finds problems earliest.</p>

## The three jobs

| You are asked to… | Start at | Then | Finish with |
|---|---|---|---|
| **Understand** an application on a device | §1 First hour | §2 Inventory forms, §7 Trace one message | a filled recon sheet and one traced message |
| **Build** a component or feature | §1, §3 Component card | §4 Timing budget, §5 Build checklist | the card, the budget, a passing evidence table |
| **Debug** a problem on the device | §6 Triage | §9 Measuring recipes | the first bad state, with evidence, not a guess |

## The shape of every task

1. **Run it.** Build with debug symbols, run it (hardware or emulator), read the log. Write down what you saw. (The *State First* book's step 1.)
2. **Inventory it.** Tasks, interrupts, queues, shared data, rates. Forms in §2.
3. **State it as numbers.** Period, deadline, budget, depth, owner, margin: the Component Card (§3) and Timing Budget (§4).
4. **Probe it.** Trace, counters, histograms. Predict first, then measure (§9).
5. **Prove it.** One number per requirement, with a method and a margin (book ch. 20).
6. **Log it.** Keep the cards, the traces and the counters with the code.

## What to bring

| Item | Why |
|---|---|
| the framework's configuration file(s) | the first document (book ch. 22) |
| a way to run: board or emulator, and a debugger | step 1 |
| the book's Appendix B (formulas) and this handbook, printed | forms to fill in |
| `labs/host/rtcalc.py` | schedulability in one command |
| a pen | forms are meant to be written on |

## Marks

**[book ch. N]** points to the explanation. **☐** is a check to tick. A blank line is a question you must answer or hand to someone who can.

::: rule
**One rule above all.** If you cannot fill in a line, do not guess it. Write `?` and make "find out" a task. A `?` on a form is a finding.
:::
