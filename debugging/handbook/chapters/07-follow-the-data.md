# 07 · Follow the Data — your "100 instances of one variable" problem

> From your `context.txt`: *"a class that has 100 instances of a variable… in several methods,
> connected to pointers, and even goes in and out the class in a messaging system."*
> The talk's answer **[talk]**: *"Rather than having to follow the **control flow** — which often
> requires you to read hundreds or thousands of lines and work out what function calls what — follow
> the **data**. This is the data I'm interested in. Who touches it? Where does it get modified?"*
> And: *"You don't necessarily need to know a codebase completely to start working on it."*

## The idea in one picture

```
Reading the code (what you were doing)         Watching the data (what the talk does)
────────────────────────────────────────       ─────────────────────────────────────────
grep → 100 hits → read each → trace pointers   find the ONE live object → tell the CPU
→ lose the thread at the message queue          "stop when this memory changes" → read bt
        O(codebase)                                     O(number of times it changes)
```
A **hardware watchpoint** makes the CPU stop the program the instant a specific memory address is
written. It doesn't care which of the 100 textual occurrences did it, whether it went through a
pointer, a reference, a `memcpy`, or a message handler. **The backtrace at that stop *is* the answer to "who touched it?"**

## The 6-step recipe

### 1 · Reproduce & get *the live object* (not the name)
A name is ambiguous (100 hits, many classes). An **address** is not. Run to a point where the object
exists, then get a handle on it.
```gdb
(gdb) break main.cpp:17        # after construction, before the bad thing happens
(gdb) run
(gdb) p tracker                # or:  p *this   p *obj->m_tracker   p &tracker.m_total
(gdb) ptype tracker            # talk hint: look at the struct once you've found the object
```
Can't reach it from `main`? Break in any method of the class and use `p *this`. Found it via a pointer chain? `p *a->b->c`
then `p &a->b->c->field` gives you the address of the field.

### 2 · Watch it — with a *condition* so you only stop on the interesting write
```gdb
# GDB 📖  (-l / -location = watch the ADDRESS, stays valid even when the expression goes out of scope)
(gdb) watch -l tracker.m_total                     # every write
(gdb) watch -l tracker.m_total if tracker.m_total < 0       # only when it goes bad  ("conditional watchpoints blew my mind" — your notes)
(gdb) rwatch -l tracker.m_total                    # stop on READS    (who consumes it?)
(gdb) awatch -l tracker.m_total                    # stop on reads OR writes
(gdb) continue
```
```lldb
# LLDB ✅ tested on practice-sandbox
(lldb) b -f main.cpp -l 17
(lldb) run
(lldb) watchpoint set variable tracker.m_total             # hardware write watch
(lldb) watchpoint modify -c 'this->m_total < 0' 1          # ← condition runs in the frame that WROTE it
(lldb) continue
```
> ⚠️ **Scope trap (found while testing):** my first LLDB condition, `tracker.m_total < 0`, failed with
> *"use of undeclared identifier 'tracker'"* — the write happens inside `Tracker::applyDelta`, where `tracker`
> (a local in `main`) is not visible. Write the condition in terms of what's visible **where the write
> happens** (`this->m_total`), or use a raw address: `*(int*)0x16fdfee98 < 0`. The same caution applies to GDB conditions and `commands` blocks (not run here —
if GDB can't evaluate your condition, rewrite it with `this->` or a cast address). Stack addresses change every run; re-read `p &tracker.m_total`.

Watchpoint facts **[added, from the GDB docs]**: hardware watchpoints are a scarce resource (typically 4 per CPU, each ≤8 bytes —
LLDB on this Mac reports "Number of supported hardware watchpoints: 4"). Watching a local ends when its frame returns. If GDB falls back to
a *software* watchpoint it is very slow — watch the smallest thing possible (one `int`, not a whole struct).
Docs: <https://sourceware.org/gdb/current/onlinedocs/gdb/Set-Watchpoints.html>

### 3 · Read the stop — it answers "who touched it?"
```
Watchpoint 1 hit:  old value: 0   new value: -10
* frame #0: Tracker::applyDelta(this=…, v=-10)   tracker.cpp:14       ← the WRITER
  frame #1: Tracker::onMessage(…)                tracker.cpp:9
  frame #2: Tracker::Tracker(Bus&)::$_0::operator()   tracker.cpp:4    ← the handler registered with the bus
  …
  frame #9: Bus::pump                            bus.hpp:26            ← the DISPATCHER
  frame #10: main                                main.cpp:19
```
You now know the writer (`applyDelta`), the **argument that was wrong** (`v=-10`), and the path.
You didn't read a single other occurrence of `m_total`. Next question moves from *where* to *why that value*.

### 4 · The message trap — the stack ends at the dispatcher, the *sender is gone*
After a queue, `bt` shows who **delivered** the message, not who **sent** it. (This is built into `practice-sandbox/src/bus.hpp`.)
**Move the breakpoint to the producer** and filter on the bad value ✅ tested:
```gdb
(gdb) break Bus::post if m.value < 0                         # GDB 📖
```
```lldb
(lldb) breakpoint set -n Bus::post -c 'm.value < 0'           # LLDB ✅
(lldb) run
* frame #0: Bus::post(this=…, m=(type = Delta, value = -10))   bus.hpp:20
  frame #1: Controller::rebalance(this=…, target=5)            controller.cpp:12   ← THE SENDER (the real bug site)
  frame #2: main                                               main.cpp:18
(lldb) frame variable            # look at believedTotal_ in the caller:  frame select 1 ; p *this
```
That is the whole "goes in and out of the class in a messaging system" problem solved in one breakpoint.
**Rule: break at the *producer* (post / send / enqueue / emit / publish), not the consumer.** Filter on the bad payload.

If the bad value is computed *before* it's posted, you now `up` a frame and ask "why is `believedTotal_` 15 when `Tracker` was reset to 0?"
→ root cause = stale state after a `Reset`. Fix there, not in `applyDelta` ("crash site ≠ bug site", ch.02).

### 5 · Not sure which write was the first bad one? Go backwards
```gdb
(gdb) record full                    # GDB built-in recording; start AFTER you're near the problem (slow)  📖
(gdb) continue                       # run forward until the bug has happened
(gdb) watch -l tracker.m_total
(gdb) reverse-continue               # run BACKWARDS; stops at the previous write to that memory
(gdb) reverse-finish / reverse-step / reverse-next
```
Greg Law's / Chris's demo **[talk]**: watch `profit_this_year`, `continue` → stops each daily running cost; add a condition
(`if value > old`) → stops only when the train *earns*. With UDB/rr you can `reverse-continue` from the crash to the last writer without re-running. → ch.08.

### 6 · Many hits, no need to stop each time? Log instead of breaking
```gdb
(gdb) watch -l tracker.m_total
(gdb) commands
> silent
> printf "m_total now %d\n", *(int*)0x7ffe1234abcd        # ← the address printed by: p &tracker.m_total
> bt 3
> continue
> end
(gdb) continue                        # scrolls a log of every writer + stack; grep it afterwards
```
Or `dprintf` at the textual write sites you found with `rg` (ch.04) — great for cross-checking a hypothesis.

## Decision table: which data tool?

| You know… | You want… | Use |
|---|---|---|
| the variable, it's wrong **now** | who wrote it | `watch -l` (+ condition) |
| the variable, wrong value arrives via a **queue/bus/callback** | the original sender | conditional **break at post/send** |
| the program already crashed/finished wrongly | who wrote it *last* | reverse debugging, `reverse-continue` (ch.08) |
| who **reads** it / depends on it | consumers | `rwatch` / `awatch` |
| a pointer is wrong (dangling/null) | who freed / nulled it | `watch -l ptr` + `bt`, or ASan (ch.12) |
| only some of N instances are wrong | the bad instance | break with condition on `this` (`if this == 0x…`) or on an id field |
| the write is in a hot loop | skip uninteresting hits | `condition`, `ignore N`, or `until` |

### "Which of the 100 `m_total`s is mine?" — instance filtering
```gdb
(gdb) break Tracker::applyDelta if this->m_id == 7         # condition on identity
(gdb) break Tracker::applyDelta if this == 0x7ffe…           # or on the exact object (get the address with `p &tracker`)
```

## Static complement: shrink the haystack before you run

```bash
# every textual writer, 5 seconds, ✅ tested on the sandbox
rg -n 'm_total\s*([-+*/%|&^]|<<|>>)?=[^=]' src/
# who calls the setter / producer
rg -n 'bus_?\.post\(|->post\(' src/
```
Use the list as a **checklist to cross out** after the watchpoint shows you the real writer. If a writer never fires during the failing
run, you've learned the 99 others don't matter for *this* bug — that's the data-first shortcut **[talk]**.

## Practice (15 minutes, safe) — `practice-sandbox/`
```bash
cd practice-sandbox
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug && cmake --build build
./build/sandbox                                    # Assertion failed: total must never be negative
lldb ./build/sandbox                               # (or gdb on Linux)
```
Goal: find the root cause using **only** a watchpoint + one conditional breakpoint — don't read `controller.cpp` first.
Then check your answer against the `// BUG (planted)` comment. Then fix it, `ctest --test-dir build` goes green, revert the fix, watch it go red (ch.02 step 7).

## Links
- GDB watchpoints — <https://sourceware.org/gdb/current/onlinedocs/gdb/Set-Watchpoints.html> · conditions — <https://sourceware.org/gdb/current/onlinedocs/gdb/Conditions.html>
- Reverse execution — <https://sourceware.org/gdb/current/onlinedocs/gdb/Reverse-Execution.html>
- Greg Law, *Time Travel Debugging* (Meeting C++ 2023; the talk's "follow the data" example, ends with a ~15-min SQLite walkthrough) — <https://www.youtube.com/watch?v=qyGdk6QMpMY>
- LLDB watchpoints — <https://lldb.llvm.org/use/tutorial.html> (see "watchpoint set") · GDB↔LLDB — <https://lldb.llvm.org/use/map.html>
