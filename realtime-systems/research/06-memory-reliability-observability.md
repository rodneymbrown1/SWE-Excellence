# 06 · Memory, reliability (watchdogs, fault containment), observability

## 1. Memory rules for embedded C

- **Holzmann, "The Power of 10"** (JPL, 2006) [S17, **P**]: ten rules for safety-critical C. Those the book uses (checked in the downloaded copy):
  - simple control flow — no `goto`, `setjmp/longjmp`, recursion;
  - all loops have a fixed upper bound that a checker can verify;
  - **no dynamic memory allocation after initialization**;
  - functions short (about a page);
  - assertions — at least two per function on average;
  - check return values; restrict preprocessor and pointers.
  Rationale given in the paper: rules should be mechanically checkable; allocator behavior after startup is hard to bound. **The book teaches this as a *policy that a framework may already enforce*, not as a universal law.**
- **FreeRTOS heap schemes** (T01 ch. 3, **P**): `heap_1` (allocate only, never free), `heap_2` (best fit, **no coalescing**, deprecated for new designs per the book), `heap_3` (wraps malloc/free), `heap_4` (first fit with **coalescing**), `heap_5` (heap_4 over multiple regions). Utilities: `xPortGetFreeHeapSize()`, `xPortGetMinimumEverFreeHeapSize()`, `vPortGetHeapStats()`; `vApplicationMallocFailedHook`; **static allocation** via `configSUPPORT_STATIC_ALLOCATION` and `xTaskCreateStatic()` etc. (all in ch. 3 headings).
- **Stack:** each task has its own stack, sized in words at creation; `uxTaskGetStackHighWaterMark()` reports the minimum free stack ever; `configCHECK_FOR_STACK_OVERFLOW` 1 or 2 plus `vApplicationStackOverflowHook` (T01 ch. 13 *Troubleshooting*, **P** — heading check). **Methods have limits:** method 1 checks the stack pointer at context switch; method 2 additionally checks a fill pattern at the end of the stack; both can miss an overflow that "recovered" between switches (we state this in words; the book's ch. 13 text is the authority — see the quote block when writing ch. 14).
- **Toyota ETCS (expert slides S22):** "Stack is 94% full PLUS any recursion"; "Incorrect assumption that overflow always results in a system reset"; "Memory just past stack is OSEK RTOS area" — i.e. a stack overflow can corrupt **kernel data**. Carry the expert-witness caveat.
- **Spirit FLASH anomaly (C08, P):** "The root cause of the anomaly was a design error in the software module that provides file system services. In addition, two significant configuration errors detrimentally affected the overall behavior of the system once the root cause error occurred." Mechanics (paper's section "DOS File System Usage" / "The Root Cause" + secondary summary in search results): the bundled DOS file-system library allocated memory at boot based on the number of files on flash (including deleted); accumulated file count exhausted memory at boot → **reset loop** ("delayed reset loop"); recovery on Sol 21 via a "crippled" mode that avoids the FLASH file system; then deletion of obsolete data products on Sol 27; full reformat later. **Lesson:** *a resource whose consumption grows with mission time, consumed during boot, converts into an unrecoverable reboot loop.* (We cite the paper for root-cause statement and the overall sequence; day numbers are as the paper gives them — checked against the text.)
- **Memory-mapped I/O** (C survival kit, Appendix B): `volatile` register access; no source cited other than C semantics + Eide & Regehr.

## 2. Reliability: watchdogs

- **Memfault (T09, P):** hardware watchdog = a counter the software must reload periodically or it resets the CPU. Key practical points verified in the article:
  - a *naive* design — a low-priority thread feeds the watchdog — "is not able to catch deadlocks between tasks": the example in the post has a **high-priority thread suspended waiting for a mutex** while "our low priority thread will be scheduled to run by the RTOS and can keep feeding the watchdog";
  - fix: a **task watchdog**: tasks "register" and the hardware watchdog is fed only if **all tasks have recently checked in**;
  - a **software watchdog** with a slightly shorter timeout can capture diagnostic state (PC/LR, which task) *before* the hardware reset, enabling a post-mortem (the post shows the $pc/$lr in the FreeRTOS idle task and identifies the stuck task);
  - MCU vendors often **pause the watchdog while halted in a debugger**; read the reset-reason register (`RESETREAS` on nRF52) after reboot.
- **Ganssle** (T10, P): the long-standing "guide to watchdog timers" (downloaded; used for: don't kick the dog from a timer ISR; use windowed watchdogs where available; a watchdog is the last resort, not a design). Specific quotes to be added when writing ch. 19 from the local text; none made here.
- **Koopman slides (S22):** "Proper watchdog use includes: kicking from timer tick interrupt service routine usually a bad sign; any single task death must inhibit watchdog kick — that means checking all tasks for liveness before kicking." In the ETCS description (as testified): "Watchdog kicked by a hardware timer service routine"; "Watchdog does not detect death of major tasks, including 'Task X'"; "Task X includes throttle angle calculation & most failsafes"; "Watchdog only detects death of the 1 msec task, not others". **Plaintiff expert; disputed.**
- **AUTOSAR Watchdog Manager** (T11, **Sn**): three supervision types — **alive** (checkpoints at the right frequency), **deadline** (time between two checkpoints), **logical** (checkpoints in the right sequence) — defined in the Health-Monitoring / Adaptive-Watchdog requirement documents (search-result summaries). The book uses the three-way vocabulary and credits AUTOSAR.
- **Pathfinder (C02):** the supervision that mattered was a **software deadline check between two tasks** (`bc_sched` verifying `bc_dist`), with a defined reaction (reset) and a designed recovery path (state in RAM survives reset, activities resumed). Quote: "We knew that if this problem occurred we would reset. We built in mechanisms to recover the current activity …".
- **Apollo (C01):** software-initiated restart (`BAILOUT`) with restart protection; **restart is itself a load-shedding policy**.

## 3. Fault containment and error-handling policy

- **Ariane 501 (C07, P):** the Inquiry Board report: a conversion of a 64-bit floating point value to a 16-bit signed integer produced an **Operand Error** in the Inertial Reference System software; the conversion "was not protected"; "the failure should be indicated on the databus, the failure context should be stored in an EEPROM memory …, and finally, the SRI processor should be shut down. It was the decision to cease the processor operation which finally proved fatal." Both SRIs were identical ("two SRIs operating in parallel, with identical hardware and software"), so redundancy did not protect against a **systematic** software fault. Culture note in the report: error handling designed "for random hardware failures". The affected alignment function "is operative for 50 seconds after starting of the Flight Mode" and was not required for Ariane 5.
  - **Lessons used:** (1) the *policy* "on exception, halt" is a design decision with system consequences; (2) redundant copies of the same software share the same bugs; (3) reused code carries assumptions about the envelope.
- **Partitioning/containment tools**, named without detailed claims: MPU (FreeRTOS-MPU port, T01 ch. 1/2 headings), ARINC 653 time/space partitioning (not researched in this pass), process-per-component on Linux/ROS 2. The book's guidance is the *generic* decision: for each component, "what is the blast radius if it hangs / crashes / corrupts memory / floods the bus?".
- **Ingenuity (C11):** the watchdog issue in commissioning: "a computer protection and reliability feature" prevented transition to the "flight-state" (Sol 49); fixed by a flight-controller microcontroller software update. We cite the blog text (P) and note that the exact internal cause is not described in the post.
- **Blackout (C09):** silent loss of a monitoring function: the operators "were unaware". A system whose failure produces *no signal* is the worst class; monitoring needs its own monitor.

## 4. Observability: tracing, profiling, histograms

- **Pathfinder (C02):** ring-buffer trace/log facility instrumented around kernel services, left in flight by design; produced a "voluminous dump" when the scheduler detected the error; the failure was reproduced in <18 h — "We could not have figured this out ever if we did not have the tools to give us the insight."
- **FreeRTOS built-ins** (T01 ch. 12 *Developer Support*, **P**): `configASSERT()`, trace hook macros (`traceTASK_SWITCHED_IN`, …), run-time statistics (`vTaskGetRunTimeStats`, requires a time base 10–100× the tick), `uxTaskGetSystemState`, stack high-water marks, heap stats. Ch. 12 headings checked; details re-read when writing ch. 20.
- **Commercial/OSS trace tools** (not researched in depth): Percepio Tracealyzer, SEGGER SystemView, Linux ftrace/LTTng/Perfetto. The book describes the *capability* (task timeline, ISR timing, CPU load per task, event ordering) and the lab builds a minimal trace (hook → ring buffer → timeline) so the reader understands what those tools do.
- **GPIO toggle + logic analyser** as the zero-overhead method to measure period/jitter/latency: standard practice; Memfault/SEGGER/Percepio all describe variations (**Sn**). The lab simulates the GPIO with a timer-stamped marker.
- **Histograms and percentiles**: S19 (Tene), T14 (HdrHistogram). **Acceptance wording the book teaches:** "p99.99 ≤ X over N hours, observed max M, zero deadline misses, histogram attached" — not "average 2 ms".
- **Debugger changes timing** (state-first connection): stopping at a breakpoint stops the world — timers keep counting in real hardware, watchdogs may be paused (Memfault note) — use hardware watchpoints / tracepoints / dprintf / ring-buffer logs for timing-sensitive questions. Gillian Minnehan's Embedded Online Conference "GDB Deep Dive" (T04 of the debugging project) is the user-supplied source on gdb workflows.

## 5. Use in documents

| Item | Where |
|---|---|
| Power of 10, heap, stack | Book ch. 14; Lab R6 |
| Spirit | Book ch. 14, 18, 19 |
| Watchdog patterns, Toyota, Pathfinder | Book ch. 19; Lab R5 |
| Ariane | Book ch. 19 |
| Blackout | Book ch. 15, 19 |
| Tracing, histograms | Book ch. 20; Lab R8, H5 |
