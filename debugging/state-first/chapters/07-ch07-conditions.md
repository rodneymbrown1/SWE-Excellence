# From English to conditions {.chapter}

<p class="lede">Most behavior descriptions fall into ten patterns. Each pattern has a logical form and a standard probe. Learn the patterns once and translation becomes lookup.</p>

## The pattern catalog

Find the phrase in the left column. Write the logic in the middle column on your card. Use the probe in the right column. `END` means "the last line of the function that changes the data".

| If the English says… | The logic | The probe |
|---|---|---|
| "This must **always** / **never** be true" (invariant) | `I` holds at every observation point | Conditional breakpoint at `END` of every function that changes the data: `break END if !(I)` |
| "**After** X, Y should hold" (postcondition) | `{P} X {Q}` | Breakpoint at X's exit with `if !(Q)`. Or `finish` and read the result |
| "**When** X, do Y" (guard and action) | `if (G) A` | Breakpoint **at A** (did it run?), and at the line that tests G, showing G's operands |
| "Y **didn't happen**" / "why not?" | G was false, or never evaluated | Breakpoint at the decision, log each operand; count hits of the function (is it even reached?) |
| "Y happened but **shouldn't have**" | A ran while G was false | Breakpoint at A with `if !(G_expected)`; `bt` shows which path |
| "**Only if** X" (precondition) | `P` required before `C` | Breakpoint at C's entry with `if !(P)` |
| "The **Nth time**" / "after N events" | a counter | Ignore count, or a counter variable; a conditional on the counter |
| "**In this order**" | sequence S1 then S2 | Log both with a sequence number; or **arm**: breakpoint 1 enables breakpoint 2 |
| "It's **stuck** / never finishes" | progress variable `p` must change | Interrupt and `bt`; tripwire on an iteration counter; a watchpoint on `p` that never fires |
| "Only for **this one** user / device / instance" | scope to one thing | Add `this == $target`, a thread, or a string compare to any condition above |

Each probe is covered in Part 4. Here you only need to *choose* it from the card.

## Worked translations

**"The link should not go Down while heartbeats are arriving."**
It says *should not* and *while*. That is an **invariant** over the state. Find the data: `state_`, `missed_`. A heartbeat is an event. Rewrite: "after a heartbeat is handled, `missed_` is zero." Probe: stop at the end of `on_event` if that is false.

```
break gateway.cpp:81 if e.type == EventType::Heartbeat && missed_ != 0
```

**"Nothing is logged when the link recovers."** [illustrative]
It says *nothing happened*. That is a **didn't happen**. The action A is the log call. The guard G is whatever decides to log. Probe: a breakpoint on the logging function (zero hits?). If it is never reached, stop at the decision above it and print the operands.

**"The first alarm fires, but the second one never does."** [illustrative]
*The Nth time*, plus *didn't happen*. Count how many times the alarm function is reached, then compare against the guard. A counter works well here (chapter 10).

## Writing conditions that work

* **Say it aloud.** `break … if e.type == Heartbeat && missed_ != 0` reads as "stop after handling a heartbeat where the counter was not cleared." If it does not read as the behavior, rewrite it.
* **Use names the debugger knows.** In C++, use scoped enum names (`EventType::Heartbeat`), member names, and `this->member`. [RAN]{.ran} in lldb; standard in gdb. [MANUAL]{.manual}
* **Parentheses around negations:** `!(a && b)`, not `!a && b`.
* **Strings:** `$_streq(name, "x")` in gdb (needs a Python-enabled gdb). [MANUAL]{.manual} Comparing `char*` with `==` compares addresses, not text.
* **Avoid side effects and function calls in a condition.** The GDB manual says "Break conditions can have side effects, and may even call functions in your program", and recommends command lists for side effects. In lldb I tried `strstr(...)` in a condition and got `'strstr' has unknown return type; cast the call to its declared return type`. [RAN]{.ran} Calls are fragile and slow.
* **Know the cost.** In gdb the program stops every time the location is reached, then the condition is evaluated and, if false, it resumes. Cheap in a small loop, noticeable in a tight one. For remote targets, `set breakpoint condition-evaluation target` lets the target evaluate it (default is `auto`). [MANUAL]{.manual}

::: trap
**The condition that never fires.** Common causes: comparing floats with `==`; a typo that parses as a different variable; a condition placed on a line that is not reached; or a condition about the *wrong instance*. Before you trust silence, make sure the probe *can* fire. Temporarily loosen it, or test it on a known-bad case.
:::

## Choosing the *place*

The place matters as much as the condition.

* **For an invariant, put the probe at the end of the function that changes the data.** The data was just updated, so a violation is fresh and the backtrace points at the culprit.
* **For a postcondition, put it at the exit.**
* **For a "didn't happen", put it at the decision** (where the guard is tested), not at the action that never ran.
* **Put it where the data is in scope.** A condition can only use names visible at that line.

::: try
Take the DEFINE section of your current card. For each line, find its row in the table, name the probe, and write the place. If a line does not fit any row, it is probably two behaviors. Split it.
:::

## Check yourself

* Which pattern is "the screen never updates"? (A *didn't happen*.)
* Where would you put the probe for "`count` must never exceed 10"? (At the end of every function that changes `count`.)
