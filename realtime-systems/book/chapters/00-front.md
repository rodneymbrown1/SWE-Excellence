# Read this first

<p class="lede">You are about to write application and middleware code on top of a real-time operating system, inside a framework someone else designed. You will not invent the scheduler. You must still know what it promises, what it quietly assumes, and what happens when your code breaks the assumption. This book is the shortest honest route to that knowledge.</p>

## The core idea

A real-time system is correct only if it is correct **and on time**. Everything in this book is a way of answering one question with evidence:

> *Will this component do the right thing, at the right moment, every time — including on the worst day?*

You will be handed requirements that never mention most of the things that decide the answer: how often a component runs, what it waits on, how big its queue is, what happens when the queue is full, who else touches its data, what restarts it when it hangs. Those are **implicit requirements**. Missing one is how a correct-looking change becomes an incident. Chapter 23 collects them in one list; every earlier chapter earns one or two.

## The six questions

Every chapter belongs to one of six questions. Learn to ask them about any component, in any framework, in any order.

{{fig:six-questions | The six questions. Each one has a chapter group, a handbook checklist, and at least one lab.}}

| # | Question | You can answer it when you can state… | Chapters |
|---|---|---|---|
| 1 | **Timing**: can my component finish on time? | period, deadline, execution-time budget, jitter limit | 1–5, 17 |
| 2 | **Scheduling**: which component runs first? | policy, priorities, preemption rules, worst-case response time | 6–11 |
| 3 | **Messaging**: what if messages arrive too fast? | queue depth, overflow policy, QoS, age limit | 15–16, 18 |
| 4 | **Synchronization**: can components share data safely? | owner, lock or copy rule, blocking time, lock order | 12–14 |
| 5 | **Reliability**: what if a component stops? | detector, reaction, containment, recovery | 19 |
| 6 | **Observability**: how do I prove the system meets its requirements? | one number per requirement, with a histogram, not an average | 20 |

## How the book is organised

| Part | Theme | Starts from | Ends at |
|---|---|---|---|
| **1 · Time** | What "on time" means and how a program finds out what time it is | a loop that prints | a cyclic executive |
| **2 · Order** | Who runs when | the first kernel and its tasks | rate-monotonic analysis, EDF, overload |
| **3 · Share** | What two pieces of code can safely do to the same data | a race | priority inversion, memory |
| **4 · Flow** | How data moves between components | a queue | publish/subscribe, rates, lifecycles |
| **5 · Trust** | Failing safely, and proving things | the watchdog | measurement, multi-CPU systems |
| **6 · Put it together** | Reading a framework, implicit requirements, a worked system | an unfamiliar codebase | a pipeline you debug to its requirements |

The chapters follow history on purpose. Each mechanism appears when the previous one fails: a loop cannot keep time, so we add a timer; a timer cannot interleave jobs, so we add interrupts; interrupts cannot share fairly, so we add a scheduler; a scheduler lets jobs corrupt each other's data, so we add locks; locks invert priorities, so we add protocols. If you know *why* each piece exists you can recognise it in a framework that renamed it.

## Three documents, one method

| Document | Use it to | Style |
|---|---|---|
| **ON TIME** (this book) | learn the discipline, in order | read it, with a pen |
| **Field Handbook** | act on the first day with a new device or framework | checklists, questions, forms |
| **Lab Workbook** | prove each idea to yourself on a real RTOS | run, measure, compare with prediction |

## Marks you will see

| Mark | Meaning |
|---|---|
| [RAN]{.ran} | I ran this and kept the output (`labs/transcripts/`). Runs are deterministic: you will see the same numbers. |
| [MANUAL]{.manual} | Checked against documentation but **not executed** here (for example, a VS Code configuration). Verify before relying on it. |
| [SEC]{.sec} | Taken from a secondary source (a news report, an expert's slides). The source and its weakness are named. |
| **EVIDENCE** | A measured or published result, with its size and its limits. |
| **CASE FILE** | A real incident and what it teaches. |
| **RULE / TRAP / TRY IT / CHECK** | A thing to do always, a common mistake, a small experiment, a self-test. |

## What this book does not do

- It does not teach assembly or hardware design. Chapter 14 and Appendix A give just enough C and memory to read an RTOS application.
- It does not replace your framework's documentation. Chapter 22 teaches you to read it quickly.
- It does not promise numbers from real boards. The labs run on an emulator with a deterministic clock; they prove *relationships* (model against measurement), not any chip's speed.
- Where evidence is thin or a source could not be checked, it says so. Appendix E lists every source and its status; `research/09-claims-we-could-not-verify.md` lists everything we could not confirm.

## A study plan

| Week | Read | Do | You should be able to |
|---|---|---|---|
| 1 | Part 1 (ch. 1–5) | Labs H1, H2, R0, R1 | explain why a loop drifts, how a tick works, and what a frame overrun does |
| 2 | Part 2 (ch. 6–9) | Labs H3, R2, R8 | compute a response time by hand and compare it with a measurement |
| 3 | Part 2 (ch. 10–11), Part 3 | Labs R3, R6, R7, R9 | name an inversion from a timeline and find it with gdb |
| 4 | Part 4 (ch. 15–18) | Labs H4, R4 | size a queue from a burst and say what happens when it is full |
| 5 | Part 5 | Labs H5, R5 | design a watchdog that catches a stuck task and report latency honestly |
| 6 | Part 6 | Lab R10 and the Handbook | take over an unfamiliar pipeline and prove it meets its requirements |

Six weeks at an hour a day. If you have one afternoon, read chapters 1, 7, 9, 13, 15, 19, 20 and 23, and keep the Handbook open.
