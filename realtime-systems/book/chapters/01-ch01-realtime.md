# What "real-time" means {.chapter data-part="PART 1 · TIME"}

<p class="lede">A real-time system is one whose correctness depends on <em>when</em> a result appears, not only on <em>what</em> it is. That single sentence changes how you read requirements, how you test, and what you are allowed to assume.</p>

## Correct and on time

Most software is judged by its output. A report that takes two seconds instead of one is slower, not wrong. A real-time component has a **deadline**: a result that arrives after it is a *failure*, even if every bit is right. The definition is usually credited to Stankovic's 1988 paper, "Misconceptions About Real-Time Computing"; its best-known point is that real-time computing is not the same as fast computing.

It is not. Speed is an average-case property. Real-time is a **worst-case** property measured against a stated deadline. A controller that answers in 1 ms on average and 60 ms once an hour has a fast average and a missed deadline.

| Class | If the deadline is missed | Example you will meet |
|---|---|---|
| **Hard** | the result is wrong or the system is unsafe | a motor-control loop, a safety interlock, a bus transaction cycle |
| **Firm** | the result is worthless but nothing breaks; the miss is counted | a video frame, a periodic sensor sample used in a filter |
| **Soft** | the result is still useful, only less valuable | a display refresh, a log flush |

The class is a **requirement**, and it is rarely written down. You usually have to ask.

## The timing contract of a component

Every component that does periodic or event-driven work has a contract. Whether or not it is written, it exists.

| Term | Meaning | Typical symbol |
|---|---|---|
| **Trigger** | what starts a job: a timer (periodic), an event (sporadic), another component's output | — |
| **Period** | time between releases for a periodic component; **minimum inter-arrival** for a sporadic one | T |
| **Deadline** | latest acceptable completion, relative to release (often equal to T) | D |
| **Budget (WCET)** | the execution time you promise the job never exceeds | C |
| **Response time** | completion time minus release time, *including* waiting for the CPU | R |
| **Jitter** | variation in release or completion time between jobs | J |
| **Miss policy** | what happens when R > D: skip, abort, continue late, reset | — |

The whole subject is one inequality: **R ≤ D**. Chapters 6–11 teach how to compute and bound R; chapters 3 and 20 teach how to measure it; chapters 12–19 explain what makes R larger than you expected.

::: rule
**Rule.** A component without a stated period, deadline, budget and miss policy is not finished. When the spec is silent, write down what you assume and get it confirmed.
:::

## What the theory assumes (and what breaks it)

The first complete result in this field is Liu and Layland's 1973 paper. It proves what is schedulable under five assumptions. They double as a checklist of what real systems violate.

| Assumption (Liu & Layland, 1973) | Where real code breaks it |
|---|---|
| (A1) hard-deadline requests are **periodic** with a constant interval | events arrive in bursts; timers drift (ch. 3) |
| (A2) the deadline is the **next request** of the same task | work backs up; the next release arrives before the last job finished (ch. 11) |
| (A3) tasks are **independent** | locks, shared buffers, queues (ch. 12–15) |
| (A4) run-time per task is **constant** (interpreted as the maximum) | caches, data-dependent branches, a rare slow path (ch. 9, 20) |
| (A5) non-periodic work is special: initialization and recovery | logging, retries, error handling at the worst moment |

Later chapters remove assumptions one at a time: blocking (A3) in chapter 13, varying execution time (A4) in chapters 9 and 20.

## Why not simply be fast?

Three reasons the answer is "no".

1. **You cannot test the worst case by running the average case.** The worst case needs a rare combination: a slow path, a burst, a preemption at the wrong instant. Pathfinder's flight-software lead wrote that the failure "would only manifest itself when ASI/MET data was being collected and intermediate tasks were heavily loaded", and that pre-launch testing used the "best case" data rates.
2. **Speed does not remove the ordering problem.** A 10× faster CPU runs a priority inversion 10× faster. It still blocks the high-priority task for as long as it takes the medium-priority work to finish.
3. **Fast hardware is not the constraint you were given.** You are handed a processor, a framework and a rate. Your job is to show your component fits.

::: case
**Apollo 11, 1969: the machine that shed work.** During the powered descent the computer raised program alarms 1201 and 1202. The guidance software's authors later explained the cause: an interface to the rendezvous radar, left in the wrong configuration, "stole approximately 13% of the computer's duty cycle" from a margin that had shrunk to about 10%. The software kept flying. The reason is a design decision made years earlier: a **priority-driven executive** whose jobs ran highest-priority first, with a fixed pool of eight job slots and a restart mechanism that kept critical jobs and dropped the rest. The authors contrast it with a "boxcar" executive, which "breaks down completely as soon as any function takes longer than the time it is allocated." (Eyles 2004.) You will meet this design twice more: as the cyclic executive in chapter 5 and as overload handling in chapter 11.
:::

## From the loop to the RTOS: why each piece exists

{{fig:history | Milestones used in this book. Interrupt dates follow Smotherman's history; the rest are from the papers and reports cited in research/01.}}

The sequence is the plot of Parts 1 to 3:

1. **A loop** polls inputs and does work. Its period is whatever the code takes (ch. 2).
2. **A hardware timer** lets the program learn what time it is and wait precisely (ch. 3).
3. **Interrupts** let events announce themselves instead of being polled (ch. 4).
4. **A cyclic executive** divides time into fixed slots so many jobs share one CPU predictably (ch. 5).
5. **A preemptive scheduler** lets an urgent job interrupt a long one without a hand-built table (ch. 6–7).
6. **Analysis** tells you whether the result meets deadlines (ch. 8–11).
7. **Synchronization** protects data the jobs share, and **protocols** stop the protection from defeating the priorities (ch. 12–13).

## Check yourself

::: check
1. State, for any component you own, its trigger, period or minimum inter-arrival, deadline, budget and miss policy. Which did you have to guess?
2. Why is "the average response time is 2 ms" not an answer to "does it meet its deadline?"
3. Which of Liu and Layland's five assumptions does a queue between two components violate, and what does that mean for analysis?
:::

**Lab link.** Lab H3 (scheduler workbench) lets you test the assumptions by breaking them.
