# Memory: stacks, heaps and budgets {.chapter data-part="PART 3 · SHARE"}

<p class="lede">You will not manage memory addresses, but you will choose stack sizes, allocate buffers and decide whether a queue can grow. On a small system, memory is a fixed budget with no operating system to say "out of memory" politely, and the failure usually arrives after weeks, not on the first run.</p>

## Where RAM goes

{{fig:memory-map | RAM of a small system. The task stacks, task control blocks, queues and buffers all live in the heap in FreeRTOS; static data is sized at link time.}}

| Region | Holds | Lifetime | Sized by | Failure |
|---|---|---|---|---|
| **Static** (`.data`, `.bss`) | globals, statics | whole run | the linker | none at run time (it just does not link) |
| **Stack** (one per task) | locals, call frames, saved registers | while the task runs | **you, at creation** | overflow corrupts a neighbour |
| **Heap** | tasks, queues, buffers, `pvPortMalloc` blocks | until freed | `configTOTAL_HEAP_SIZE` | allocation fails, or fragments |
| **`.noinit`** | data that survives a reset | across resets | linker section | used for post-mortem notes (ch. 19) |

## The no-allocation-after-init policy

Holzmann's "Power of 10" (JPL, 2006), ten rules for safety-critical C, includes: simple control flow (no `goto`, no recursion), **every loop has a fixed upper bound**, assertions (at least two per function on average), and **no dynamic memory allocation after initialization**. The rules are meant to be checked mechanically. The reasoning is timing and failure: allocator time varies, fragmentation is path-dependent, and an allocation can fail where the code has no plan for failure. Many flight and automotive frameworks enforce this for you; **find out whether yours does** (chapter 22).

| Option in FreeRTOS | Behaviour |
|---|---|
| **static allocation** (`xTaskCreateStatic`, …) | every object lives in memory you provide; no heap |
| `heap_1` | allocate only, never free: deterministic, cannot fragment |
| `heap_2` | best-fit, can free, **does not merge** neighbours; "not recommended for new designs" |
| `heap_4` | first-fit **with merging** (coalescing) of adjacent free blocks; the usual choice |
| `heap_5` | `heap_4` across several memory regions |

## Fragmentation, run

[RAN]{.ran} Lab R6, `heap_4`, 48 KB heap. Allocate 40 blocks of 1,000 bytes; free every other one:

| State | Free total | Largest single block | Free blocks |
|---|---|---|---|
| after allocating 40 | 5,728 B | 5,728 B | 1 |
| after freeing every other | **25,888 B** | **5,728 B** | 21 |
| `pvPortMalloc(8000)` | — | — | **fails** (NULL) though 25,888 B are free |
| after freeing the rest | 46,048 B | 46,048 B | 1 |
| `pvPortMalloc(8000)` | OK | — | neighbours merged |

"Free bytes" is a misleading number. Watch the **largest free block** and the **minimum ever free** (`xPortGetMinimumEverFreeHeapSize`): the latter is the margin you actually had.

## Stacks: the quiet way to fail

Each task's stack is a fixed array. A call chain deeper than expected, a large local array, or recursion pushes the stack pointer past the end into **whatever is next in memory** — often another task's stack, a queue, or the kernel's own data — and nothing stops it.

The kernel can *look*, but only occasionally: `configCHECK_FOR_STACK_OVERFLOW` = 1 checks the stack pointer at **context switches**; = 2 additionally checks a fill pattern at the stack's end (the last 20 bytes). The FreeRTOS book: method 1 "can miss stack overflows that occur between context switches."

[RAN]{.ran} Lab R6 part 3: a task with a 512-byte stack recurses to about 1.2 KB. It returns normally and prints "nothing has noticed". At its next context switch the hook fires. By then **720 of 2,048 bytes** of the neighbouring heap block (a canary placed just below) had been overwritten. The check is a *detector after the damage*, not a guard.

**How to size a stack.** Run the system through its worst case (slowest path, deepest call chain, all interrupts firing), read the **high-water mark** (`uxTaskGetStackHighWaterMark`: the minimum free words ever), and keep a written margin. [RAN]{.ran} In Lab R6 the high-water report listed each task's minimum free stack: `manager` 145 of 256 words, `IDLE` 118, `Tmr Svc` 224. A task near zero is one code change from an overflow. Static stack-depth analysis also exists (Regehr et al.; not read here).

::: case
**Toyota throttle software, as testified (2013).** An expert for the plaintiffs reported that the stack was "94% full plus any recursion", that there was "no mitigation for stack overflow" and an "incorrect assumption that overflow always results in a system reset", and that "memory just past stack is OSEK RTOS area", so an overflow could damage the operating system's data. [SEC]{.sec} Expert slides in contested litigation: take it as the *list of questions* a reviewer should be able to answer for any system: *how full is each stack at worst, is recursion banned, what is next to each stack, what detects overflow and what does it do?*
:::

## Resources that grow with mission time

::: case
**Spirit rover, January 2004.** After 18 sols on Mars the rover stopped responding to commands and rebooted repeatedly. The JPL paper by Reeves and Neilson: "The root cause of the anomaly was a design error in the software module that provides file system services. In addition, two significant configuration errors detrimentally affected the overall behavior of the system once the root cause error occurred." In outline: the file system library, at boot, allocated memory based on the number of files on flash (including deleted ones); files accumulated over seven months of cruise and a few days of operation; the memory the file system needed at boot became more than was available; the flight software entered a **delayed reset loop**. Recovery: use commands that avoid the file system ("crippled" mode) each sol, delete files, and later reformat. The lesson is a pattern: **a resource consumed at start-up, that grows with time in service, turns into an unrecoverable boot loop.**
:::

## Message and buffer ownership

A buffer passed between tasks needs an **owner at every moment**. The usual rules: a message is **copied** into the queue (the sender may reuse its buffer at once; the cost is the copy), or a **pointer** is passed and ownership moves with it (cheap; the sender must not touch it again, and *something* must free it). Pool allocators (fixed-size blocks from a static array) give constant-time, fragmentation-free allocation; make the pool depth part of the message's design (chapter 15).

::: rule
**Rule.** For every allocation: who frees it, what happens if it fails, and what is the largest the pool can get. If an answer is "nobody", "we crash", or "unbounded", fix it before you ship.
:::

## Check yourself

::: check
1. A heap shows 30 KB free and a 6 KB allocation fails. Name two measurements that would confirm fragmentation.
2. A task's stack high-water mark is 12 words free of 256. What do you do first, and what do you check afterwards?
3. Which resources in your system grow with uptime or number of files, messages or log entries? What bounds each?
:::

**Lab link.** R6 (stack, heap and overflow); R5 uses `.noinit` for post-mortem data.
