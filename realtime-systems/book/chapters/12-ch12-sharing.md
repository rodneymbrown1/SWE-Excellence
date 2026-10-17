# Shared state and races {.chapter data-part="PART 3 · SHARE"}

<p class="lede">The moment two flows of control touch the same data — two tasks, or a task and an interrupt — correctness depends on interleaving. The interleaving that breaks you will be rare, will not appear in a debugger, and will take the form of one of two small patterns.</p>

## What the evidence says concurrency bugs look like

Lu, Park, Seo and Zhou (ASPLOS 2008) examined **105 randomly selected real concurrency bugs** (74 non-deadlock, 31 deadlock) from four large programs (MySQL, Apache, Mozilla, OpenOffice). Their findings, as the paper states them:

| Finding | Number | What it means for you |
|---|---|---|
| Non-deadlock bugs that are **atomicity violations** or **order violations** | **97%** | learn these two patterns and you have covered almost all of them |
| Non-deadlock bugs that are **order violations** | **32%** | "A must happen before B" bugs are common, and locks do not fix them |
| Bugs that need only a **partial order between 2 threads** to manifest | **96%** | tests with two tasks find most bugs |
| Non-deadlock bugs involving **one variable** / **several** | **66% / 34%** | a lock per variable misses a third |
| Bugs that manifest if a partial order among **≤ 4 memory accesses** is enforced | **92%** | the window is tiny: rare, timing-dependent |
| Non-deadlock bugs **fixed without adding or changing locks** | **73%** | the cure is usually a redesign: ownership, ordering, copying |

::: why
**Limits.** These are server and desktop programs in C, C++ and Java, not RTOS code. The authors caution that results "are associated with the four examined applications". Use the patterns, not the percentages, as a prior for what to look for.
:::

## The two patterns

**Atomicity violation.** A region of code assumed to execute without interruption is interleaved by another flow. The classic form is *check, then act*, or *read two related values at different times*.

**Order violation.** Two operations are assumed to occur in one order but nothing enforces it: a consumer reads data a producer has not yet initialised; a task starts using a queue before the task that creates it ran.

::: case
**Therac-25, 1985–87.** The Leveson and Turner investigation of six radiation overdoses found, among other causes (process, interlocks, reporting), that the control software "allows concurrent access to shared data stored in shared variables, and that the 'test' and 'set' for such variables are not indivisible operations." The report describes race conditions on shared variables between the operator-interface task and the setup tasks, where a fast edit by an operator could be missed. The earlier machine's hardware interlocks had masked such defects; removing them exposed the software's. Two lessons carry over: **a shared flag's test-and-set must be one indivisible operation**, and **a safety net that hides a bug hides it from you too.**
:::

## A bug from the labs

[RAN]{.ran} Lab R10: a filter task publishes an attitude estimate in a shared struct; a control task reads it at 100 Hz. The code reads one field, computes for 150 µs, then reads another assuming it describes the same sample:

```c
int32_t  a  = att.angle;            /* read 1 */
uint32_t s1 = att.seq;
burn_us(150);                       /* compute with 'a' */
uint32_t ts = att.t_us;             /* read 2: assumes the SAME sample as 'a' */
uint32_t s2 = att.seq;
if (s1 != s2) torn++;               /* nothing prints this counter */
```

Of 309 control cycles, **47** read two different samples. The control loop worked, the mean latency looked fine (715 µs), and no log line mentioned it. The sensor ran from its own 997 µs clock, so the collision drifted instead of repeating, which is why a test that passed once told you nothing.

The fix is to take **one snapshot, atomically**, and then use only the copy:

```c
att_t snap;
taskENTER_CRITICAL();               /* a few instructions: copy 16 bytes */
snap = att;                         /* (field-by-field in the lab) */
taskEXIT_CRITICAL();
/* use snap.* from here on */
```

Torn reads fall to 0. The same data could be passed by value in a queue, so the reader owns its copy and no one else touches it.

## The tools, from least to most powerful

| Tool | What it protects against | Cost and cautions |
|---|---|---|
| **Don't share**: one owner writes, others receive a copy (queue, message) | everything | a copy; the best default (chapter 15) |
| **Single writer, atomic word**: one task writes a 32-bit aligned word that others only read | torn reads of *one word* | atomic only for naturally aligned word-size accesses; **not** for structs, not for 64-bit values on 32-bit cores |
| **Disable interrupts / critical section** | interrupts and tasks | adds latency to *every* interrupt; keep to a few instructions (ch. 4) |
| **Suspend the scheduler** | other tasks (not interrupts) | blocks every task for its duration |
| **Mutex** | other tasks | may block; can invert priorities (ch. 13); never from an interrupt |
| **Atomics / lock-free ring buffer** | one producer + one consumer | subtle; for experts and well-tested library code |
| **Double buffer / snapshot** | readers needing a consistent set | memory, plus a swap that must itself be atomic |

::: trap
**Trap: `count++` on a `volatile`.** `volatile` forces the compiler to re-read and re-write the variable. It does **not** make read-modify-write atomic: an interrupt between the load and the store loses an increment. Eide and Regehr's EMSOFT 2008 study also found `volatile` accesses miscompiled in each of thirteen compilers tested (2008-era). Use the kernel's primitives or a language atomic.
:::

::: rule
**Rule.** For every piece of shared data write down five facts: **owner** (who writes), **readers**, **protection** (copy, critical section, mutex, atomic word), **longest hold time**, and **what it blocks**. If any one is missing, there is a race you have not found yet.
:::

## Races between a task and an interrupt

An interrupt is a thread that can run between any two instructions of a task, and that cannot wait. So:

- The ISR **may not take a mutex**. It can write a word, post to a queue (FromISR), or set a flag.
- The task **must protect** multi-instruction sequences the ISR also touches (disable that interrupt or use a lock-free structure).
- A flag the ISR sets and the task clears needs thought about **both orders**: clear-then-check, or check-then-clear, can lose an event.

## Why "it passed the test" means little

If a bug needs a specific ordering of a few accesses, then the probability of hitting it per run is the width of that window divided by the period of the thing that moves it. Phase-locked rates (a 1 kHz sensor and a 100 Hz controller from the same clock) can make the collision *always* or *never* happen; independent clocks make it intermittent. Review shared data by reading, and use invariants (a field and its complement; a sequence number read twice) that make the corruption *detectable*.

## Check yourself

::: check
1. A 32-bit counter is incremented in an ISR and read in a task on a 32-bit core. Is the read safe? What if the counter is 64 bits?
2. Find, in code you know, one place where two related variables are read at different times. What invariant could detect a mismatch?
3. A colleague proposes protecting a 12-byte struct with `volatile`. What do you answer?
:::

**Lab links.** R10 (the torn read), R9 (watch a shared variable with gdb).
