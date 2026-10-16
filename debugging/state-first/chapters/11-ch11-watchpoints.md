# Watchpoints {.chapter}

<p class="lede">A breakpoint follows code. A watchpoint follows data. When you know <em>what</em> is wrong but not <em>where</em> it was made wrong, a watchpoint finds the writer.</p>

## Just enough memory

You said your C knowledge stops at the edge of memory, and that you only need what you can see in an editor. One page is enough for now.

* A **variable** is a named box. It lives at an **address**.
* A **pointer** is a box that holds another box's address. `*p` means "the box `p` points at."
* `&x` means "the address of `x`."
* An **object** is one set of boxes. `this` is the address of the one you are inside. Two objects of one class are two sets of boxes at two addresses.

That is why you can ask three different questions about a pointer `p`:

| You type | You are watching | It stops when… |
|---|---|---|
| `watch p` | the **pointer box** | `p` is reassigned to point elsewhere |
| `watch *p` | the **pointee box**, as `p` currently points | the target changes (and GDB re-evaluates if `p` moves) |
| `watch -l *p` | the **memory location** it points at *right now* | that exact location changes, even after `p` changes |

If a pointer value is changing and affecting the system but you do not know where, start with `watch p`. Then, once you have the address you care about, use `watch -l` on it. You do not need to read assembly for any of this.

## The three kinds

| Command | Stops when… | Notes |
|---|---|---|
| `watch EXPR` | the value is **written** (and changes) | the common one |
| `rwatch EXPR` | the value is **read** | hardware only |
| `awatch EXPR` | the value is **read or written** | hardware only |

Add `-l` (or `-location`) to watch the **memory** the expression refers to, not the variable's scope. The manual: "The `-location` argument tells GDB to instead watch the memory referred to by expr." [MANUAL]{.manual}

## Rules you must know

From the GDB manual unless noted. [MANUAL]{.manual}

* **Hardware first.** "GDB sets a *hardware watchpoint* if possible." Hardware watchpoints do not slow the program. Software watchpoints single-step and "report the change in value at the next *statement*, not the instruction."
* **Limited supply.** The manual gives no number. "If you set too many hardware watchpoints, GDB might be unable to insert all of them when you resume." The warning reads `Could not insert watchpoint`. On Cortex-M parts, the comparators live in the DWT unit. The Memfault example dump shows 4 on one nRF52840. Read `DWT_CTRL.NUMCOMP` for yours.
* **Scope.** A watchpoint on a local is deleted when the function returns: "GDB automatically deletes watchpoints that watch local (automatic) variables … when they go out of scope." Use `-l` to keep it.
* **Same value, no stop.** If a write stores the value that is already there, plain `watch` does not stop. The Memfault article says GDB "will suppress the debug event generated and auto-resume the processor." To see *every* write, use `awatch` or a breakpoint.
* **The stop is after the write.** The program has already moved on. The Memfault article says that on its target the PC "has already advanced" and the halt can be a couple of instructions late. In source terms: you stop on the line *after* the assignment.
* **Alignment (embedded).** "it is only possible to watch ranges of addresses that are aligned on the size being watched."
* **Conditions work.** `watch EXPR if COND`.
* **Constants cannot be watched.** `watch 0x600850` fails with "Cannot watch constant value." Use `watch *(int *) 0x600850`.

## Recipes

### 1. Who writes this? (LOG + TRAP) [RAN]{.ran}

Stop in a frame where the object is visible, put a location watchpoint on the field, and log each write without stopping. This is the recipe for **"which instance, which line"**.

```
break Gateway::run
run --max 400
watch -l monitor_.state_            # gdb: put the log in a commands list (lab/gdb/02-log-state-writes.gdb)
```

lldb, with a Python callback. Real output:

```out
state_ written -> Up        after line 115   via LinkMonitor::on_heartbeat() <- LinkMonitor::on_event
state_ written -> Degraded  after line 97    via LinkMonitor::on_tick() <- LinkMonitor::on_event
state_ written -> Down      after line 102   via LinkMonitor::on_tick() <- LinkMonitor::on_event
state_ written -> Up        after line 115   via LinkMonitor::on_heartbeat() <- LinkMonitor::on_event
state_ written -> Degraded  after line 97    via LinkMonitor::on_tick() <- LinkMonitor::on_event
state_ written -> Down      after line 102   via LinkMonitor::on_tick() <- LinkMonitor::on_event
state_ written -> Up        after line 115   via LinkMonitor::on_heartbeat() <- LinkMonitor::on_event
```

Seven writes, three distinct places. This is a **complete list of where the state changes**, at runtime. (Notice one place that never appears. Chapter 23 explains why that matters.)

### 2. Only the bad values (TRAP with a condition) [RAN]{.ran}

```
watchpoint set variable this->monitor_.missed_
watchpoint modify -c 'missed_ == 7'
```

It stopped in `on_tick` right after `++missed_` made it 7, at t=26. In gdb: `watch -l monitor_.missed_ if missed_ == 7`. [MANUAL]{.manual} Note that in a condition the names are looked up in the frame where the stop happens, so write `missed_`, not `this->monitor_.missed_`.

### 3. Who reads this? (`rwatch`)

`rwatch -l monitor_.state_` stops when anything *reads* `state_`. That finds the consumers: the code that reacts to the value. Expect a lot of hits in a loop. Combine with a condition or an arm. [MANUAL]{.manual}

### 4. Only one instance

`watch -l` on one object's field already watches one location. If you pick the field through `this` while stopped inside the object you want, you have chosen that instance. To scope a *breakpoint* to one instance, use `this == $target` (chapter 10).

### 5. Arm, then watch (cuts the noise)

A busy field changes thousands of times. Keep the watchpoint disabled until a trigger event, then switch it on. [MANUAL]{.manual}

```
watch -l monitor_.missed_
disable 2                                  # keep watchpoint 2 off
break LinkMonitor::announce if state_ == LinkState::Degraded
commands
  silent
  enable 2                                 # armed: now watch missed_
  continue
end
```

The full script is `lab/gdb/06-arm-then-watch.gdb`.

### 6. The program ends and the watchpoint fires anyway

I hit this. With a watchpoint on a variable inside `main`'s objects, lldb kept resuming from watchpoint hits after the program had printed its summary and was shutting down (my reading: the stack memory was being reused). [RAN]{.ran} Put a breakpoint near the end of the run and `delete` the watchpoint there. The lab scripts do this at `Gateway::summary`.

## Embedded notes

* Data watchpoints are implemented in silicon, so the count is small and chip-specific.
* The stop happens just *after* the access. Read the line above the stop line.
* Writes of an identical value may not stop. If a peripheral register is rewritten with the same value, use `awatch`.
* Memfault's article "Faster Debugging with Watchpoints" walks through Cortex-M specifics with an nRF52840.

## Check yourself

* What is the difference between `watch p`, `watch *p`, and `watch -l *p`?
* Why do you stop on the line *after* the write?
* How do you keep a watchpoint from disappearing when the function returns?
