# Read this first

<p class="lede">You get handed work in a code base you did not write. You have to fix something, add something, or just understand something. This book is a procedure for doing that quickly, accurately, and the same way every time.</p>

## The core idea in four lines

1. A debugger can only answer questions you can state as **data** and **conditions**.
2. Stating them is the hard part. That *is* understanding the problem.
3. So: first build confidence in the behavior, then translate it into a short written **Behavior Card** (what exists, what must be true, what changes it), then aim the debugger with it.
4. Every task follows the same **seven steps**. Only the first probe and the time split change with the kind of task.

## The method on one page

| # | Step | The question it answers | You produce | Done when |
|-|-----|----------|----------|----------|
| 1 | **Run it** | What does it actually do? | Command, input, and the output you saw | You can repeat the run on demand |
| 2 | **Understand it** | What is it *supposed* to do, and where do I work? | Purpose, premise, desired state, boundary | You pass the **Confidence Gate** (ch. 5) |
| 3 | **State it** | What are the data and conditions? | A filled **Behavior Card** | Every line is testable, unknowns are marked `?` |
| 4 | **Probe it** | What does the running program say? | Probes: conditional breakpoints, watchpoints, logs | Each probe has a prediction written first |
| 5 | **Pin it** | Which instance, which line? | One sentence: "X is Y because line L does not Z when C" | You can name the exact place and instance |
| 6 | **Prove it** | Did the change do what I claimed? | Minimal change + the same probes re-run | Probes that fired before are silent now |
| 7 | **Log it** | What will I (or the next person) need? | Journal entry, saved probe scripts | Someone else could repeat it |

::: rule
**Always start with step 1.** Run the program and look at what it does before you read anything else.
:::

## How to use this book

* **30 seconds.** Open the Field Cards (the separate sheets). Card 1 is the method. Card 2 is the blank Behavior Card.
* **90 minutes.** Read Parts 1 to 4, then one worked example in Part 6. That is enough to start using it.
* **On the job.** Use chapter 16 to classify the task, the matching playbook in chapters 17 to 19, and chapter 20 to split your time.
* **Practice.** The `lab/` folder has a small program with a real bug. Three worked examples run on it.

## Marks you will see

| Mark | Meaning |
|----|--------------------|
| [RAN]{.ran} | I ran this command and captured the output. (lldb, on macOS.) |
| [MANUAL]{.manual} | Checked against the official GDB manual, **not executed** by me. Run the smoke test on your Linux box (Appendix C) before relying on it. |
| [SEC]{.sec} | A claim about a source I could only read through a reliable secondary page. Details in Appendix D. |

Commands are written for **gdb first**. The lldb equivalent is given where I tested it.

## What this book does not do

* It does not teach assembly or memory layout. You said you do not need that yet; chapter 11 has one page of "just enough" for pointers.
* It does not replace profilers or sanitizers. It says when to reach for them.
* It does not promise that hard problems become easy. It makes your time visible and your guessing small.
* Where the evidence is thin or a quote could not be verified, it says so. Appendix D lists every source and its status.
