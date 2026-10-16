# 06 · Debugger Fundamentals — GDB (Linux) and LLDB (macOS) side by side

> The talk's point: a debugger isn't only for finding bugs — *"it's also a great tool for code
> understanding"* **[talk]**. Use it to **land on `main`, then follow whatever you care about.**

Source for the GDB commands: the talk slides (p.34) and the *GDB Cheat Sheet* by Marc Haisenko
(copy in `slides/GDB-Cheat-Sheet.pdf`). LLDB column: items marked ✅ were run on this Mac against `practice-sandbox/`; unmarked LLDB items come from the LLDB docs.
GDB column: 📖 from docs (no `gdb` on Apple Silicon macOS — try it once on the Linux box before you depend on it).

## Start it (4 ways)

| I want to… | GDB 📖 | LLDB ✅/📖 |
|---|---|---|
| Debug a program | `gdb ./build/app` | `lldb ./build/app` |
| …with arguments | `gdb --args ./build/app -x 5` | `lldb -- ./build/app -x 5` |
| Attach to a running process | `sudo gdb -p PID` (slides) | `sudo lldb -p PID` · `lldb -n appname -w` (wait for launch) |
| Post-mortem on a crash dump | `gdb ./build/app core` | `lldb ./build/app -c core` |
| Script it / non-interactive | `gdb -batch -x cmds.gdb ./app` | `lldb -b -s cmds.lldb ./build/app` ✅ |
| Find the PID | `pgrep -fl openttd` · `ps aux \| grep openttd` (slides) | same |

Attaching needs permission (`sudo`, or on Linux `ptrace_scope`: `cat /proc/sys/kernel/yama/ptrace_scope`). **[talk: "I need super user permissions to attach"]**
Attach lets you skip startup and dive in *after* something interesting happened (e.g. after the train exists) **[talk]**.

## The core commands (learn these 12 and you can do 90%)

| Action | GDB (short) | LLDB | Notes |
|---|---|---|---|
| Run to `main` and stop | `start` | `breakpoint set -n main` then `run` (`b main`, `r`) | lands you at the entry point **[talk]** |
| Run | `run` / `r` | `run` / `r` | |
| Pause a running program | `Ctrl-C` | `Ctrl-C` | **[talk]** |
| Breakpoint at function | `break Foo::bar` / `b` | `b Foo::bar` | |
| Breakpoint at line | `b file.cpp:42` | `b -f file.cpp -l 42` ✅ | |
| **Conditional** breakpoint | `b Bus::post if m.value < 0` | `b -n Bus::post -c 'm.value < 0'` ✅ | the workhorse (ch.07) |
| One-shot breakpoint | `tbreak X` | `b -o true X` | `start` = `tbreak main` + `run` |
| Continue | `c` | `c` | |
| Next line (step **over**) | `n` | `n` | **Enter repeats the last command** **[talk]** |
| Step **into** | `s` | `s` | |
| **Finish** current function | `finish` / `f`* | `finish` | *slides call it `f`; careful: `frame` also abbreviates to `f` in GDB* |
| Run until line | `until 50` / `advance 50` | `thread until 50` | skip loops |
| Backtrace | `bt` / `bt full` (locals too) | `bt` ✅ / `bt all` (all threads) | **[talk]** |
| Pick a frame | `frame 2` / `up` / `down` | `frame select 2` / `up` / `down` | inspect locals in the *caller* |
| Locals / args | `info locals` / `info args` | `frame variable` ✅ | |
| Print | `p x` · `p *ptr` · `p arr[0]@10` · `p/x n` | `p x` · `p *ptr` · `p/x n` | `@10` = array slice (GDB) |
| Type of thing | `ptype obj` / `whatis x` | `image lookup -t Foo` · `p -T -- obj` | **`ptype` — talk hint**: once you find an object, look at its struct |
| Print every stop | `display x` | `display x` | |
| Kill but stay in debugger | `kill` | `process kill` | **[talk]** |
| Quit | `q` | `q` | |

### Source view
- GDB: `tui enable` (or `gdb -tui`) — the speaker's favourite: source + commands in one terminal **[talk]**. `Ctrl-x a` toggles. `layout split` adds assembly.
- LLDB: `gui` (curses) or `settings set stop-line-count-after 6` to show surrounding lines automatically.
- `list`, `list file:func`, `list 40,60` (GDB) · `source list -n func` (LLDB).

## Breakpoint power-ups

```gdb
# GDB 📖
b Bus::post if m.value < 0          # condition at creation
condition 3 m.value < 0              # add/change condition on breakpoint #3
ignore 3 99                          # skip the next 99 hits  (hit #100 is the one you want)
tbreak file.cpp:120                  # temp: auto-deletes after first hit
rbreak ^Tracker::                    # breakpoint on every function matching a regex (explore a class!)
commands 3                           # run a script when #3 hits
  silent
  bt 3
  continue
end
dprintf file.cpp:42,"v=%d total=%d\n", v, m_total   # print WITHOUT stopping or recompiling
info breakpoints                     # list all, with hit counts
delete 3 / disable 3 / enable 3
```
```lldb
# LLDB ✅ (the first two were run here)
breakpoint set -n Bus::post -c 'm.value < 0'
breakpoint list
breakpoint modify -c 'm.value < 0' 1
breakpoint set -n Tracker::applyDelta -G true      # -G = auto-continue
breakpoint command add 1                           # then type commands, 'DONE' to end
breakpoint set -r '^Tracker::'                     # regex = every function in a class
breakpoint disable 1 / breakpoint delete 1
```
`dprintf` is "add a `printf` to code you can't recompile" — perfect for logging **before main / after main** and
who-calls-what flow **[talk: "things you can actively log: what happens before main … after (cleanup)"]**.

## Stack & threads
```gdb
bt                          # who called me?  (frame #0 is where you are)
bt full                     # + locals in every frame
frame 3 / up / down         # climb to a caller, then `info locals`
info threads                # all threads and where each is
thread 2                    # switch
thread apply all bt         # EVERY thread's stack — the hang/deadlock command (ch.12)
set scheduler-locking on    # only the current thread runs when you step 📖
```
LLDB: `thread list`, `thread select 2`, `bt all`, `thread backtrace all`.

## Exceptions, signals, libraries
```gdb
catch throw                 # stop where any C++ exception is thrown (see the real origin)
catch catch / catch syscall write / catch signal SIGSEGV
handle SIGPIPE nostop noprint pass
info sharedlibrary          # which .so are loaded (code you don't own)
info signals
```
LLDB: `breakpoint set -E cxx` (C++ throw) · `image list` (loaded libs) · `process handle SIGPIPE -s false`.

## Change things while it runs (experiments, not fixes)
```gdb
set var m_total = 0         # force a value to test a hypothesis  (GDB cheat sheet)
return 5                    # force the current function to return 5 immediately
call foo(3)                 # call a function in the program (careful: side effects)
```
LLDB: `expr m_total = 0` · `thread return 5` · `expr foo(3)`. Use these to **falsify** a hypothesis in seconds ("if total were 0 here, would the assert still fire?").

## Make GDB pleasant — `~/.gdbinit` 📖
```gdb
set pagination off
set confirm off
set print pretty on
set print object on           # show the real (derived) type of a base pointer
set history save on
set debuginfod enabled on     # auto-download symbols (GDB 12+)
```
LLDB: `~/.lldbinit` — e.g. `settings set target.x86-disassembly-flavor intel`, `settings set stop-line-count-after 8`.
Tip: make a **project-local** `.gdbinit` with your breakpoints and `source` it: `gdb -x debug.gdb ./app`.

## GDB ↔ LLDB translation (official map) — <https://lldb.llvm.org/use/map.html>
Biggest gotchas: LLDB `frame variable` ≠ `print` (the first reads the stack cheaply, the second evaluates an expression);
LLDB breakpoint conditions are evaluated as **expressions in the stopped frame**, so names must be in scope there (ch.07).

## When the plain debugger isn't enough
- "How did I get here?" / "who wrote this value **last**?" → reverse debugging, ch.08
- "Where is the time going?" → profiler, ch.09
- Crashes with no repro → core dump + sanitizers, ch.12

## Links
- GDB manual — <https://sourceware.org/gdb/current/onlinedocs/gdb/>
  · Breakpoints/conditions — <https://sourceware.org/gdb/current/onlinedocs/gdb/Conditions.html>
  · Dynamic printf — <https://sourceware.org/gdb/current/onlinedocs/gdb/Dynamic-Printf.html>
  · TUI — <https://sourceware.org/gdb/current/onlinedocs/gdb/TUI.html>
  · Attach — <https://sourceware.org/gdb/current/onlinedocs/gdb/Attach.html>
- LLDB tutorial — <https://lldb.llvm.org/use/tutorial.html> · GDB→LLDB map — <https://lldb.llvm.org/use/map.html>
- GDB cheat sheet (the one on slide 34) — <https://darkdust.net/files/GDB%20Cheat%20Sheet.pdf> (local copy: `slides/GDB-Cheat-Sheet.pdf`)
- How debuggers work (AOSA ch. on GDB, from the slides) — <https://aosabook.org/en/v2/gdb.html>
- Greg Law talks (from the slides): *GDB — A Lot More Than You Knew* <https://www.youtube.com/watch?v=-n9Fkq1e6sg> ·
  *Debugging Linux C++* <https://www.youtube.com/watch?v=V1t6faOKjuQ> ·
  *Back to Basics: Debugging in C++* <https://www.youtube.com/watch?v=qgszy9GquRs> ·
  Mike Shah, *Back to Basics: Debugging* <https://www.youtube.com/watch?v=YzIBwqWC6EM>
