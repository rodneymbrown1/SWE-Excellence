# Working with other people, and with AI {.chapter}

<p class="lede">The method is personal, but the output is shareable. A card is something you can hand to a colleague. A probe file is something a teammate can run. This chapter is about using that, and about using AI tools without giving up the part only you can do.</p>

## Share the card, not the confusion

* **In a ticket or pull request:** paste the **sentence**, the **card** (or just EXPECTED, OBSERVED, and the probe), and the **proof**. Reviewers can check the reasoning, not only the diff.
* **When you ask for help:** hand over the card with the `?` marks. "Here is what I expect, here is what I see, here is the probe I ran, here is my hypothesis, and here is where I am stuck" takes a minute to read and gets better answers than "it's flaky." (In Alaboudi and LaToza's experiment, being offered a plausible hypothesis was the aid that helped; a bare location did not.)
* **In handoffs:** the Understand deliverable (chapter 17) is the handoff document.

## Ask for a fresh view on a schedule

Agans lists "Get a Fresh View" as a rule because the person who has been staring at a problem has a stale picture of it. Build it into the clock (chapter 20): when a step reaches 1.5 times its budget, you ask, within 15 minutes. Say so up front: "my check-in is at 2 hours."

## Put probes where the team can find them

* `tools/probes/` in the repository, or a shared notes folder, whichever your team uses.
* One file per probe, with the card reference and the prediction in the header (chapter 14).
* A short `README` listing the file names and what each answers. A probe nobody can find is not shared.

## Code review with cards

When you review someone else's fix, ask three questions from the method:

1. What is the **first bad state**, and where was it observed?
2. What **probe** showed it, and was it seen to fire *before* and stay silent *after*?
3. Which **other paths** reach this code, and how do we know?

## Contracts in the code

Where a card's DEFINE line is a rule the system must always obey, make it **executable**: an `assert`, a unit test, or a runtime check that logs loudly (chapter 24). Bertrand Meyer's Design by Contract gives the vocabulary: preconditions, postconditions, class invariants. You have been writing them on cards. Moving the important ones into the code is how a team stops re-discovering the same bug.

## Using AI tools

AI assistants can help with this method. They can also tempt you to skip it. Here is where they fit.

**Good uses**

* **Draft a card** from a code excerpt and a log. You check every line against the run.
* **Explain an unfamiliar API or idiom** you hit while reading (a template, a macro, a library call).
* **Draft a probe script** (a gdb command file, a Python breakpoint class) from the card. Then **run it, read gdb's errors, and verify**. Commands from any source, including this book, should pass your own smoke test (Appendix C).
* **Suggest hypotheses.** Treat them as input to the ledger, not as answers.
* **Rewrite your journal** into a clean summary or a commit message.

**What not to delegate**

* **Step 1.** Running the program and looking at the output is yours. Without it you will accept a plausible explanation of behavior you never saw.
* **The Confidence Gate.** If you cannot explain it, predict it, and locate it, an AI's explanation does not change that. It gives you something to *test*.
* **The expected behavior.** Only the spec, the ticket, or a person knows what *should* happen.
* **The proof.** The probe must fire on the old build and stay silent on the new one, on your machine.

::: rule
**An AI can propose a hypothesis. Only a probe can confirm it.** Put the proposal on the ledger, write the prediction, and run the probe.
:::

::: trap
**Work code and external tools.** Pasting proprietary code, logs, or data into an external AI service can break your employer's rules. I do not know your employer's policy. Ask before you paste anything from a work code base, and use only the tools your team has approved. The method does not require any AI tool.
:::

Your `handbook/` chapter 14 covers AI assistance in more depth.

## Check yourself

* What do you hand someone when you ask for help?
* What are the three questions you ask in review?
* Which two steps do you never hand to an AI tool?
