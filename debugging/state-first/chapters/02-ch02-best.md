# What the best engineers agree on {.chapter}

<p class="lede">You asked how to use workflows developed by the best engineers. They disagree on tools and agree on process. Here are seven convictions that show up again and again, and what each became in this book.</p>

## Seven convictions

### 1. Understand before you act

George Pólya's *How to Solve It* (1945) puts "understand the problem" first. The checklist asks for **the unknown, the data, and the condition** that links them. Peter Naur argued in 1985 that a program is really the *theory* held by the people who built it: someone who has the theory can "explain how the solution relates to the affairs of the world," "support the actual program text with a justification," and "respond constructively to any demand for a modification." Modifications made "without a proper grasp of the underlying theory" are what make code decay. David Agans's first debugging rule is "Understand the System."

**In this book:** step 2 and the *Confidence Gate* (ch. 5). Pólya's unknown, data, condition become the Behavior Card (ch. 6).

### 2. Look. Don't guess.

Agans's third rule is "Quit Thinking and Look." He is not against guessing: "guess only to focus the search. You still have to confirm that your guess is correct by seeing the failure." Andreas Zeller's *Why Programs Fail* turns this into the scientific method: observe, form a hypothesis, make a *prediction*, test it with an experiment, refine or replace. Rob Pike's first rule of programming is "You can't tell where a program is going to spend its time." Google's SRE book describes troubleshooting as the hypothetico-deductive method: compare "the observed state of the system against our theories to find confirming or disconfirming evidence."

**In this book:** step 4. **Every probe has a prediction written before you run it.**

### 3. Data first

Pike's fifth rule: "If you've chosen the right data structures and organized things well, the algorithms will almost always be self-evident." He credits Fred Brooks. Brooks's version (chapter 9 of *The Mythical Man-Month*) says that if you show the tables, the flowcharts are rarely needed. Linus Torvalds said the difference between good and bad programmers is that good ones "worry about data structures and their relationships" (git mailing list, 2006, as reprinted by LWN).

**In this book:** the Behavior Card starts with **data**, not functions. You find the code by following the data (step 5).

### 4. A behavior is a sequence of states. A bug is a state that breaks a rule.

Leslie Lamport's approach to specification (TLA+) describes a system as an initial state and a rule for what steps are allowed, and states properties as *invariants* (things that must always hold). Hoare and Meyer give the same idea in program form: `{P} C {Q}`, "if P holds before code C runs, Q holds after", and class invariants that must hold whenever an object can be observed. Zeller's model of a failure is a chain: a **defect** in code causes an **infection** (a bad program state), which propagates to an observable **failure**.

**In this book:** *Declare, Define, Implement* (ch. 6) is exactly this. You are looking for the **first bad state**, not the visible symptom.

### 5. Work in experiments

Zeller's debugging loop and the SRE book agree: hypotheses are cheap and wrong ones are expected. What matters is that each can be *falsified quickly*. Alaboudi and LaToza found that incorrect hypotheses "can cause developers to investigate irrelevant information and block progress", so a wrong hypothesis you keep without testing is expensive.

**In this book:** the Hypothesis Ledger (ch. 24) and the *counterfactual* probe, where you change a value by hand in the debugger to test a hypothesis *before* you edit any code.

### 6. Change one thing at a time, and keep a trail

Agans: "write down what you did, what order you did it in, and what happened as a result." And do not change the mechanism while you are measuring it.

**In this book:** step 7, the journal, and the preference for **probes over edits** while you are still investigating.

### 7. Shrink the problem, and follow your slice

Divide and conquer (Agans), bisection and "what touched it last" (SRE), and, from the talk that started this project, *follow the data instead of the control flow*: "most of us don't get the luxury of four years to understand the codebase before we're given our first bug to solve" (Mike Shah and Chris Croft-White, C++ on Sea 2025). Studies of how people read unfamiliar code describe two strategies: reading systematically, and reading only what the task needs. Systematic readers did better on small programs; experts on large programs read "as needed", driven by their goal (as described in a 2023 survey of the research).

**In this book:** the *slice rule* (ch. 5). Read everything that touches your data, and treat the rest as a black box with a stated assumption.

## Where this book adds something

The authorities above give you principles. They do not tell you **how to get from "the link drops when it should not" to `break file.cpp:81 if e.type == Heartbeat && missed_ != 0`**. This book adds:

| Gap | What fills it |
|---|---|
| Turning a human description of behavior into debugger input | The Behavior Card and the pattern catalog (ch. 6 to 8) |
| Choosing among breakpoint, condition, watchpoint, log, count, rewind | The probe chooser (ch. 9) |
| Finding *which instance* and *which line* | Pin it (ch. 15) |
| Starting the right way for the kind of task, and budgeting time | Intake, three families, time budgets (Part 5) |

## "What about innovation?"

You asked for a process that leads to results *and even innovation*. Here is the honest version.

**What can be supported.** Faster loops between a question and evidence mean you ask more questions. Bret Victor's 2012 talk "Inventing on Principle" argues that creators need an immediate connection to what they create (known to me through secondary write-ups only). In the research on question-driven debugging, Ko and Myers's *Whyline* prototype "reduced debugging time by nearly a factor of 8" in user tests (six scenarios in a teaching environment, so an upper bound and not a forecast).

**What cannot be claimed.** No study shows that this method produces innovation. The argument is narrower and more useful: the main thing that stops people experimenting in unfamiliar code is that every experiment is slow and scary. A process that makes experiments fast and cheap removes that barrier. What you build with the freedom is yours.

::: note
**On printf.** Beller et al. found `printf` debugging remains popular, and it is not wrong. In this book, a print is one kind of probe (LOG). The skill is picking the cheapest probe that answers your question. For long-running loops, debugger probes win because you can add, change, and remove them without rebuilding and without losing the running state.
:::

## Check yourself

* Which of the seven convictions do you currently skip under time pressure?
* What is the difference between a *failure* and an *infection*, and which one do you look for first?
