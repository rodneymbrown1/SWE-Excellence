# Frame Inspection: "what went in, what's in here, what came out"

One skill: stop in a function and see its inputs, its state, and its result.
Practice target: `demo.c` (`make` builds it with `-O0 -g`).
Chain: `main -> compute_total -> line_total -> apply_discount`.

Commands are gdb first, lldb in `[brackets]`. (This Mac has only lldb, so the lldb column is the one tested here.)

## 1. Get to main
```
gdb ./demo                 [lldb ./demo]
(gdb) break main           [b main]
(gdb) run                  [run]
```
Your own project: build with `-O0 -g` or half the variables will say `<optimized out>`.

## 2. The three questions, in any frame
| Question | gdb | lldb |
|---|---|---|
| Where am I, who called me? | `bt` | `bt` |
| What went IN (arguments)? | `info args` | `frame variable` (args + locals together) |
| What is the state here (locals)? | `info locals` | `frame variable` |
| Everything at once | `info frame` | `frame info` |
| What came OUT? | `finish` (prints `Value returned`) | `finish` |

## 3. Move through the program
| Goal | gdb | lldb |
|---|---|---|
| Next line, skip over calls | `next` (`n`) | `n` |
| Next line, dive into calls | `step` (`s`) | `s` |
| Run until this function returns | `finish` | `finish` |
| Run to a line | `until 33` | `thread until 33` |
| Break in a function | `break line_total` | `b line_total` |
| Continue to next breakpoint | `continue` (`c`) | `c` |

## 4. Look at the caller's frame without leaving
```
(gdb) up          # now inspecting compute_total; `info locals` shows ITS variables
(gdb) down        # back
(gdb) frame 2     # jump to frame number 2 from `bt`
```
Execution does not move; you are only changing which frame you are looking at.

## 5. Looking at data
| Want | gdb | lldb |
|---|---|---|
| A variable | `print sub` | `p sub` |
| Struct behind a pointer | `print *it` | `p *it` |
| One field | `print it->qty` | `p it->qty` |
| Pretty multi-line structs | `set print pretty on` | (default) |
| Array of N from a pointer | `print *arr@5` | `p *arr@5` (or `memory read`) |
| Whole nested object | `print *o` | `p *o` |
| Expression / call | `print sub * 2` | `p sub * 2` |
| Raw bytes | `x/16xb it` | `x/16xb it` |
| Type of something | `ptype it` / `whatis it` | `ta v it` / `p it` |

## 6. Watch it change
```
(gdb) display o->total     # reprinted automatically after every step/next
(gdb) display i
(gdb) info display ; undisplay 1
(gdb) watch o->total       # stop whenever it changes (prints old and new)
```
lldb: `display` does not exist as such; use `target stop-hook add -o 'frame variable'`, and `watchpoint set variable o->total`.

## 7. Exercise: trace demo.c by hand
1. `break main`, `run`, `next` x3 (watch `order.count` go 0 -> 1 -> 2 via `print order`).
2. `break line_total`, `continue`. Run `info args`, `print *it`, `bt`.
3. `finish`. Read `Value returned`. Which call was it: `widget` or `gadget`?
4. `up`, `info locals`: what is `i`? Then `print o->total` (still 0 until the line completes).
5. Predict `apply_discount`'s result for `widget` (qty 12) BEFORE you `finish` out of it. The answer is 27.00, not 30.00.

## 8. Auto-trace every call (in and out, no stepping)
`trace.py` is a gdb Python script (not yet run here: no gdb on this Mac):
```
(gdb) source trace.py
(gdb) trace-funcs ^(add_item|compute_total|line_total|apply_discount)$
(gdb) run
-> add_item(o=0x7ffe..., name=0x... "widget", qty=12, price=2.5)
<- add_item = (void)
-> line_total(it=0x7ffe...)
-> apply_discount(subtotal=30, qty=12)
<- apply_discount = 27
...
```
Your own project: change the regex to the functions you care about, e.g. `^mymodule_`.
lldb equivalent, tested: `breakpoint set -r '^(line_total|apply_discount)$' -C 'frame variable' -C 'continue'` (gives arguments on entry; return values need `finish`).

## Next exercises (when this feels easy)
1. Conditional break: `break line_total if it->qty > 10`: stop only on the interesting call.
2. Breakpoint commands: `commands 2` / `silent` / `info args` / `continue` / `end` for a log without stopping.
3. `tbreak` + `until`/`advance` to skip loops.
4. Corrupt it on purpose: `set var it->qty = 99` mid-run and watch the downstream result change.
5. Core dump: crash a program, then `gdb ./demo core` and ask the same three questions after the fact.
6. Reverse: `record full` then `reverse-next`: ask "how did this value get here" (links to the Going Backwards chapter of the playbook).
