# 09 · Profilers & Call Graphs — "what actually runs? where does the time go?"

> **[talk]** A profiler isn't only for speed. *"A sampling profiler can be another good tool to see
> 'what is going on' … the **hot paths** in a codebase."* It tells you which subsystems matter, which
> loop is the heartbeat, which threads exist — a map of an unfamiliar program, drawn by the program itself.

## Two jobs, same tool

| Job | Question | Output you want |
|---|---|---|
| **Explore** (orientation) | "I do X in the app — which functions run?" | call graph / hot list **while doing only X** |
| **Perform** (slow/CPU-bound bug) | "Where is the time going?" | top self-time functions, flame graph |

Method for *explore*: start the app, get to the idle state, **start profiling, do exactly one action, stop** (the talk: "build some road and profile
a little bit to see if I could capture that"). Then the report is dominated by that feature's code.

## perf (Linux) — sampling profiler **[talk, slides 45–46]** 📖

```bash
# whole run
sudo perf record -g ./build/app            # -g = record call stacks
sudo perf report                           # interactive TUI; Enter on a symbol to drill in
# attach to an already-running process (slides 46)
sudo perf record -p $(pgrep -n app) -g -- sleep 20     # sample 20 s, then stop
sudo perf report --no-children --stdio | head -60
# live view, like top for functions
sudo perf top -p $(pgrep -n app)
# quick counters (cache misses, branch misses, IPC)
perf stat -d ./build/app
```
Better stacks: build with `-fno-omit-frame-pointer` (GCC/Clang) **or** use `perf record --call-graph dwarf` (bigger files, works with symbols).
If perf says *"Access to performance monitoring… restricted"*: `sysctl kernel.perf_event_paranoid` (needs ≤1 for non-root; ask IT before changing — **[added]**).
Docs: <https://perfwiki.github.io/main/> · man page <https://man7.org/linux/man-pages/man1/perf-record.1.html> · Brendan Gregg's cheat sheet <https://www.brendangregg.com/perf.html>

### Flame graphs — the best 1-picture orientation **[added]** 📖
```bash
git clone https://github.com/brendangregg/FlameGraph    # one-time
sudo perf record -F 99 -g -p $(pgrep -n app) -- sleep 30
sudo perf script | ./FlameGraph/stackcollapse-perf.pl | ./FlameGraph/flamegraph.pl > flame.svg
open flame.svg    # width = share of time; stack height = call depth; click to zoom
```
Paste `flame.svg` into your journal (ch.13) — the talk does the same with the call graph.

## Valgrind callgrind + KCachegrind — call graph you can browse **[talk, slides 47–51]** 📖

```bash
valgrind --tool=callgrind ./build/app                    # writes callgrind.out.<pid> (20–50× slower!)
# the talk's version: take a sample every 10M basic blocks
valgrind --tool=callgrind -v --dump-every-bb=10000000 ./build/openttd
kcachegrind callgrind.out.12345                          # GUI: run from the dir where the output was dumped
callgrind_annotate callgrind.out.12345 | head -40        # text-only summary (SSH-friendly)
# only profile the part you care about — start with instrumentation OFF, toggle it on in another terminal (slide 48)
valgrind --tool=callgrind --instr-atstart=no ./build/app &
callgrind_control --instr=on        # …do the action in the app…
callgrind_control --instr=off       # (callgrind_control -d to dump now)
```
What the KCachegrind screen gives you **[talk]**: left list of functions with inclusive/self cost and **call counts** (the "called" column
finds what matters); top: a treemap where *box size = time spent*; **Call Graph / Call Tree** tab shows what *actually* called what at runtime. 
Search for a function you care about, then **take that function name to the debugger and set a breakpoint on it** (slide 51 recommends exactly this).
Docs: <https://kcachegrind.sourceforge.net/html/Usage.html> · callgrind manual <https://valgrind.org/docs/manual/cl-manual.html>

## macOS equivalents — ✅ `sample` tested; `xctrace` 📖 (needs full Xcode)

```bash
# Sample a running process for 5 s — no sudo needed for your own processes. ✅
sample $(pgrep -n app) 5 -file /tmp/sample.txt ; less /tmp/sample.txt
#   shows "Call graph:" with sample counts per call path, per thread
# Instruments from the CLI (Time Profiler)                                                     📖
# NOTE: needs FULL Xcode. On this Mac (Command Line Tools only) it fails with
#   "xcode-select: error: tool 'xctrace' requires Xcode".
xctrace record --template 'Time Profiler' --output app.trace --time-limit 10s --launch -- ./build/app
open app.trace                                   # opens in Instruments
xctrace list templates                           # what's available
```
Note from the test run (`-O1` build): the hot function showed up as `main` because the compiler **inlined** it — a profiler reports what the
*binary* contains. Build with `-g -fno-inline` (or `-O0`) when you want the call graph to look like the source **[added]**.

## gprof / instrumented profiles (older, any Unix) 📖
`g++ -pg …; ./app; gprof ./app gmon.out | less` — coarse, but needs no root and no perf counters.

## Reading a profile without fooling yourself **[added]**
- **Self** time = in this function alone. **Inclusive/children** = this + everything it calls. Sort by *self* to find hot loops, by *inclusive* to find hot subsystems.
- A sample-based profile is **statistical**: tiny functions can be missing — that's normal.
- A function being **hot ≠ bug**. It tells you *where to look*, then go to the debugger (ch.06/07).
- Profile the **release-like** build (`RelWithDebInfo`), not `-O0`, for performance questions — `-O0` shifts the hot spots.
- Concurrency: look at per-thread views (`perf report --sort comm,tid`; `sample` prints per-thread) — one busy thread vs many blocked ones is a different problem.

## Links
- perf — <https://perfwiki.github.io/main/> · Brendan Gregg — <https://www.brendangregg.com/perf.html> · FlameGraph — <https://github.com/brendangregg/FlameGraph>
- Valgrind manual — <https://valgrind.org/docs/manual/manual.html> · Callgrind — <https://valgrind.org/docs/manual/cl-manual.html> · KCachegrind — <https://kcachegrind.sourceforge.net/html/Usage.html>
- macOS `man sample`, `man xctrace`; Instruments user guide — <https://help.apple.com/instruments/mac/current/>
