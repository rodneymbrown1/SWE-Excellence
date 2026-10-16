# Command map: gdb and lldb {.appendix}

<p class="lede">The commands used in this book, side by side. A mark means I ran it ([RAN]{.ran}, lldb on macOS) or checked it against the GDB manual ([MANUAL]{.manual}). Unmarked lldb entries are from general knowledge and were not run.</p>

## Run, stop, move

| Goal | gdb | lldb |
|---|---|---|
| Start with arguments | `run --max 400` [MANUAL]{.manual} | `run --max 400` [RAN]{.ran} |
| Stop at a function | `break Gateway::run` [MANUAL]{.manual} | `breakpoint set -n Gateway::run` [RAN]{.ran} |
| Stop at file and line | `break gateway.cpp:81` [MANUAL]{.manual} | `breakpoint set -f gateway.cpp -l 81` [RAN]{.ran} |
| One-shot | `tbreak LOC` [MANUAL]{.manual} | `breakpoint set … -o true` [RAN]{.ran} |
| Continue | `continue` | `continue` [RAN]{.ran} |
| Finish this function (show return) | `finish` | `finish` |
| Stack | `bt`, `bt 5`, `bt full` | `bt`, `bt 5` [RAN]{.ran} |
| Look at the caller / back | `up`, `down`, `frame N` | `up` [RAN]{.ran}, `down`, `frame select N` |
| Kill the program | `kill` | `kill` [RAN]{.ran} |

## Conditions, counts, logs

| Goal | gdb | lldb |
|---|---|---|
| Conditional breakpoint | `break LOC if COND` [MANUAL]{.manual} | `breakpoint set … -c 'COND'` [RAN]{.ran} |
| Add or change a condition | `condition N COND` [MANUAL]{.manual} | `breakpoint modify -c 'COND' N` |
| Ignore the next C hits | `ignore N C` [MANUAL]{.manual} | `breakpoint set … -i C` [RAN]{.ran} |
| Hit counts | `info breakpoints` [MANUAL]{.manual} | `breakpoint list` [RAN]{.ran} |
| Print and keep going | `dprintf LOC,"fmt",args` [MANUAL]{.manual} | callback returning False [RAN]{.ran} |
| Run commands at a stop | `commands N` … `end` [MANUAL]{.manual} | `breakpoint command add -F mod.fn N` [RAN]{.ran} |
| Counter | `set $n = $n + 1` [MANUAL]{.manual} | Python variable in a callback [RAN]{.ran} |
| By caller | `$_caller_matches(".*fn")` [MANUAL]{.manual} | callback checks parent frame [RAN]{.ran} |
| Disable, enable, delete | `disable N`, `enable N`, `delete N` | `breakpoint disable N`, … |
| Enable once / count | `enable once N`, `enable count C N` [MANUAL]{.manual} | |
| Save and reload | `save breakpoints F`, `source F` [MANUAL]{.manual} | |

## Watchpoints

| Goal | gdb | lldb |
|---|---|---|
| Watch for writes | `watch EXPR` [MANUAL]{.manual} | `watchpoint set variable EXPR` [RAN]{.ran} |
| Watch the memory location | `watch -l EXPR` [MANUAL]{.manual} | `watchpoint set variable this->a.b` [RAN]{.ran} |
| Watch reads / reads and writes | `rwatch`, `awatch` [MANUAL]{.manual} | `watchpoint set variable -w read_write …` |
| Conditional watchpoint | `watch EXPR if COND` [MANUAL]{.manual} | `watchpoint modify -c 'COND' N` [RAN]{.ran} |
| Run commands on a hit | `commands N` | `watchpoint command add -F mod.fn N` [RAN]{.ran} |
| List and remove | `info watchpoints`, `delete N` | `watchpoint list`, `watchpoint delete N` [RAN]{.ran} |

## Looking at and changing state

| Goal | gdb | lldb |
|---|---|---|
| Arguments | `info args` [MANUAL]{.manual} | `frame variable` [RAN]{.ran} |
| Locals | `info locals` [MANUAL]{.manual} | `frame variable` [RAN]{.ran} |
| Whole object | `print *this` | `p *this` [RAN]{.ran} |
| One value | `print missed_` | `p missed_` [RAN]{.ran} |
| Type definition | `ptype T` | `type lookup T` [RAN]{.ran} |
| Pretty output | `set print pretty on` [MANUAL]{.manual} | (default) |
| **Change a value by hand** | `set var missed_ = 0` [MANUAL]{.manual} | `expression missed_ = 0` [RAN]{.ran} |
| Search functions | `info functions Link` | `image lookup -r -n Link` [RAN]{.ran} |

## Time travel, crashes, scripts

| Goal | gdb | lldb |
|---|---|---|
| Reverse | `reverse-continue`, `reverse-step`, `reverse-next`, `reverse-finish` (after `record`, or under rr) [MANUAL]{.manual} | not used here |
| Catch a C++ exception / a signal | `catch throw`, `catch signal` [MANUAL]{.manual} | `breakpoint set -E c++` |
| Core dump | `gdb ./prog core` | `lldb ./prog -c core` |
| Run a script, then exit | `gdb -q -batch -x f.gdb ./prog` [MANUAL]{.manual} | `lldb -b -s f.lldb ./prog` [RAN]{.ran} |
| Python probe | `class P(gdb.Breakpoint): def stop(self)` [MANUAL]{.manual} | `breakpoint command add -F mod.fn` [RAN]{.ran} |
| Load a Python file | `source file.py` | `command script import file.py` [RAN]{.ran} |

## Convenience: breakpoint numbers and variables in gdb

`$bpnum` holds the number of the last breakpoint you created. `$_hit_bpnum` holds the one just hit (`disable $_hit_bpnum` turns off whichever breakpoint stopped you). `init-if-undefined $n = 0` sets a convenience variable only if it does not exist. [MANUAL]{.manual}
