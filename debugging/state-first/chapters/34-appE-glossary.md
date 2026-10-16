# Glossary {.appendix}

Plain-language meanings, as used in this book.

| Term | Meaning |
|---|---|
| **Address** | Where a variable lives in memory. A pointer holds one. |
| **Arm** | Keep a probe switched off until another probe fires and turns it on. |
| **Backtrace (`bt`)** | The list of function calls that led to the current stop, innermost first. |
| **Behavior Card** | The one-page translation of a behavior into data and conditions (chapter 6). |
| **Breakpoint** | A *place* where the program stops. |
| **Catchpoint** | A breakpoint on an event class, such as a C++ exception or a signal. |
| **Condition** | A true-or-false expression that decides whether a breakpoint or watchpoint stops. |
| **Confidence Gate** | The explain, predict, locate test at the end of step 2. |
| **Core dump** | A file with the memory and thread state of a crashed process. You inspect it; you cannot run it. |
| **Counterfactual** | Changing a value by hand in the debugger to test a hypothesis before changing code. |
| **Declare** | What exists, and where: the data and places involved. |
| **Define** | What must be true, and when: initial values, expected values, the condition that makes the behavior right or wrong. |
| **Defect** | The line of code that is wrong. (Zeller.) |
| **Dprintf** | A gdb breakpoint that prints and continues. |
| **Failure** | What you can see go wrong. (Zeller.) Usually far downstream of the cause. |
| **Family (A, B, C)** | The kind of task: Understand, Fix, or Build. |
| **Frame** | One function call on the stack, with its own arguments and local variables. |
| **Gate** | A pass or fail check between steps. |
| **Golden log** | Saved probe output from before a change, used to `diff` after it. |
| **Hit count** | How many times a breakpoint location was reached. |
| **Hypothesis** | A testable statement about the cause. It makes a prediction. |
| **Ignore count** | Skip the next N times a breakpoint is reached. |
| **Implement** | What changes the data, and how: writers, readers, and the branches that decide. |
| **Infection** | The first bad program state. (Zeller.) |
| **Instance** | One object of a class, at one address. `this` points at it. |
| **Invariant** | A condition that must always hold. |
| **Location watchpoint (`-l`)** | A watchpoint on a memory location, not on a variable's scope. |
| **Probe** | A small instruction to the debugger: when this happens, do that. FILTER, COUNT, LOG, TRAP, ARM, REWIND. |
| **Postcondition** | What must hold after code runs (`Q` in `{P} C {Q}`). |
| **Precondition** | What must hold before code runs (`P`). |
| **Slice** | The part of the system on your card: everything that reads or writes your data. |
| **State** | The values of the data at a moment. |
| **Stuck clock** | The rule: a step over 1.5 times its budget triggers a reset and a question to someone. |
| **Symbols** | The names and line numbers a debug build carries so the debugger can show them. |
| **TRAP** | A probe that stops when data changes (a watchpoint). |
| **Watchpoint** | A *data* breakpoint: stops when a value is written (or read). |
| **Writer / reader** | Code that changes data / code that looks at it. |
