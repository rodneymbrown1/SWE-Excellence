# 01 · Evidence: the tool is only as good as the developer's understanding

Your thesis (notes.txt): *conditional breakpoints and watchpoints only work if you can say what condition or
what data you care about — and that comes from understanding the problem.* Here is what the evidence says.

## 1. Comprehension is where the time goes (S15, S16)
- Xia et al.: field study of **78 professional developers, 7 projects, 3,148 working hours**; developers spend
  "∼58% of their time on program comprehension activities". [S15 abstract]
- The paper's own comparison cites an earlier estimate near 70% (Minelli et al., 2015) — treat the true figure as
  "more than half", not a precise number. [S15 via search summary; Sn]
- Robillard et al. (5 developers, medium-size open-source system): "a methodical and structured approach to program
  investigation is the most effective." Small study, qualitative. [S16 abstract, P]
- **Use in the book:** budget more time for Understand + State than feels natural (ch. 18). Present the 58% as an
  average over all tasks, not a prediction for any one task.

## 2. Most developers don't use the powerful debugger features — and experts say why (S14)
- Survey of **176 developers** + instrumentation of **458 developers'** IDE use (WatchDog 2.0, Eclipse/IntelliJ). [P]
- "Our developers did not run the debugger in 91% of IDE sessions" (they observed a debugger run in 9% of 723 sessions). [P]
- "line breakpoints are by far the most used breakpoint type. The other, more advanced, types account for less than
  7% of all breakpoints." [P, paraphrase of WR5]
- "While many developers knew and used conditional breakpoints, they were widely ignorant of hit counts and the
  debugger's other more advanced functions." [P]
- **The key interview quote** (experts I1/I2): conditions are "fuzzy (is it going to happen the 16th, 17th, or 18th
  time?)" and "once one knows the condition, one almost automatically understands the problem. Then, there is no need
  for the conditional breakpoint anymore." [P]
- Same paper: debugging is "an internal thought process not usually shared" and breakpoints are "like a one-shot…
  I just set them anew" (I4). [P] → book chapter on saving/sharing probes as scripts.
- Caveat: Java, Eclipse/IntelliJ, not C++/gdb. Direction of the result (printf stays popular; advanced features
  under-used) is what we use, not the exact percentages.
- **Use in the book:** supports "state the condition first" (the condition *is* the understanding), and supports
  teaching the underused features (hit counts/ignore counts, logpoints/dprintf, watchpoints).

## 3. Hypotheses decide success (S13)
- Controlled experiment, **20 developers**: "developers have few hypotheses, two per defect. Having a correct
  hypothesis early strongly predicted later success." [P abstract]
- "Offering fault locations did not help developers formulate more correct hypotheses or debug more successfully.
  In contrast, offering potential hypotheses made developers six times more likely to succeed." [P abstract]
  (Small sample; the comparison baseline is described in the paper body, which we did not fully read.)
- Preliminary study: "incorrect hypotheses can cause developers to investigate irrelevant information and block
  progress." [P]
- **Use in the book:** (a) *knowing where* is not enough — a fault location without a hypothesis didn't help; so the
  Behavior Card forces a falsifiable statement. (b) The Hypothesis Ledger in the journal. (c) "Ask for hypotheses,
  not just answers" in the team chapter.

## 4. The questions developers actually ask are "why didn't…?" (S12)
- Ko & Myers (CHI 2004): "programmers tend to ask why did or why didn't something happen." In their earlier
  observations, "68% of questions were why didn't questions". [P]
- Whyline user tests (Alice, six scenarios): "reduced debugging time by nearly a factor of 8, enabling programmers to
  complete 40% more tasks." [P abstract] — a research prototype in a teaching environment, small study; an upper bound,
  not a forecast for gdb.
- **Use in the book:** the "didn't happen" symptom (type B2) gets its own recipe: break at the *decision point* and
  display the guard's operands — a manual Whyline.

## 5. Understanding is a theory, not text (S01)
- Naur: a programmer who has the theory "can explain how the solution relates to the affairs of the world that it
  helps to handle", "is able to support the actual program text with a justification of some sort", and "is able to
  respond constructively to any demand for a modification of the program."
- "the decay of a program text as a result of modifications made by programmers without a proper grasp of the
  underlying theory becomes understandable." [P]
- **Use in the book:** the **Confidence Gate** (explain / predict / locate) is Naur's three abilities turned into a
  pass/fail check before any debugger work.

## 6. How much to read: systematic vs as-needed (S17, S18)
- Littman et al. (1986), as described in a 2023 survey: programmers who used a systematic strategy ("extensive
  symbolic execution of the data flow paths between subroutines") were "more successful at the requested
  modification task"; as-needed readers had weaker mental models. [S, secondary]
- Koenemann & Robertson (1991): experts on larger programs followed "an 'as-needed' strategy" driven by goals; the
  survey says comprehension is "mainly a top-down process and bottom-up is used in cases of missing or failing
  hypotheses." [S, secondary]
- Reconciliation we use (this is **our synthesis**, not a finding): go *systematic inside a small slice* (everything
  that reads/writes the data in your Behavior Card) and *as-needed outside it*. The slice is bounded by the data, not
  by the module.

## 7. Caveats about all of the above
Studies are mostly Java/IDE, small N, or lab tasks. They justify the *direction* of the method, not its numbers.
The time budgets in chapter 18 are **our starting defaults**, to be calibrated with your own journal.
