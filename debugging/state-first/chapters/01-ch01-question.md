<section class="part-title"><p class="pn">Part 1</p><div class="ph">The idea</div><p>Why a debugger is only as good as your understanding, what the best engineers agree on, and the seven steps this book is built from.</p></section>

# The tool is only as good as the question {.chapter}

<p class="lede">A debugger does not find bugs. It answers questions. If you cannot state the question as data and conditions, you cannot ask it.</p>

## The moment this book starts from

You described it yourself. You are placed on a real code base. The task touches a class with a hundred instances of a variable. You are sure the one you want is in there, but it appears in several methods, connects to pointers, and passes in and out of a messaging system. You trace imports and re-read the same functions, and nothing converges.

Then you learned breakpoints and watchpoints, and for a moment it felt solved. Then the second realization: **the tool works only as well as you understand the problem.** You do not know which instance. You do not know which condition. So you cannot tell the tool where to look.

That second realization is correct, and it is the thesis of this book.

## What a debugger is, in one sentence

A debugger is a machine for answering questions shaped like this:

> *At this **place**, when this **condition** is true, what is the value of this **data**?*

Every command you have learned is one of those three things, or a way of combining them.

| You want to say | The debugger's word | Which part is it? |
|---|---|---|
| "Stop in this function" | breakpoint | **place** |
| "…but only when `count > 100`" | condition (`break … if …`) | **condition** |
| "Tell me when this value changes" | watchpoint | **data** |
| "Show me the object" | `print *this` | **data** |

The tool supplies the machinery. **You supply the place, the condition, and the data.** And you only know those if you understand what the code is supposed to do.

## What the evidence says

::: why
**Experts say the condition *is* the understanding.** In a study of how developers debug (survey of 176 developers, plus instrumentation of 458 developers' IDE use), two expert interviewees said that specifying a condition is "fuzzy" and that "once one knows the condition, one almost automatically understands the problem. Then, there is no need for the conditional breakpoint anymore." (Beller et al., ICSE 2018.) That is your insight, from people who debug for a living.
:::

::: why
**Most people never use the powerful features.** The same study observed that developers "did not run the debugger in 91% of IDE sessions", and that "while many developers knew and used conditional breakpoints, they were widely ignorant of hit counts and the debugger's other more advanced functions." It was Java in Eclipse and IntelliJ, so treat the direction as meaningful, not the exact percentages.
:::

::: why
**A correct early hypothesis predicts success.** In a controlled experiment with 20 developers, "having a correct hypothesis early strongly predicted later success", developers held about two hypotheses per bug, and being *shown the fault location* did not help them debug better. Being offered a plausible *hypothesis* did (Alaboudi and LaToza, 2020; small sample). Knowing *where* is not enough. You need to know *what you expect to be true there*.
:::

::: why
**Understanding is where the time goes.** A field study of 78 professional developers over 3,148 hours found they spend about 58% of their time on program comprehension (Xia et al., IEEE TSE 2018). The average hides large differences between tasks, but it says that the part of the job you are least trained for is the biggest part.
:::

## Three ways people get stuck without the translation

1. **Guess and print.** Add `printf`, rebuild, run, read, repeat. It can work, but every rebuild is slow, it changes the program, and each print answers a question you did not choose carefully.
2. **Read in circles.** Re-read the same functions hoping that understanding appears. Nothing in the code tells you which part matters.
3. **Step through the loop.** Fine for a program that runs and ends. Useless in an endless event loop, where stepping changes the timing and the state you are trying to observe, and where the thing you want happens on loop iteration 40,000.

The way out is the same for all three: **write down what should be true, in terms of data and conditions, before you touch the tool.**

## What you get from this book

* A **process**: seven steps that work for any task (ch. 3).
* A **language**: declare, define, implement, turned into a one-page Behavior Card (ch. 6 and 7).
* **Probes**: conditional breakpoints, watchpoints, logging and counting, matched to the question you are asking (Part 4).
* A **classification** of tasks so you start the right way and budget your time (Part 5).
* A **lab**, so you can practice on a real bug before you need it at work.

::: try
Take the last task you struggled with. In two sentences, write what the code *should* have done and what it *did*. If you cannot name a variable or a condition in those sentences, you have found exactly where the time went.
:::

## Check yourself

* Can you state a debugger's job as place, condition, data?
* For your current task, can you name one variable, one place, and one condition? If not, which of the three is missing?
