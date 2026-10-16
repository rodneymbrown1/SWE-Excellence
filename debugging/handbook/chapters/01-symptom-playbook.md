# 01 · Symptom Playbook — "Ohh, this is *that* kind of problem"

> Find the row that matches what you see. Do the **first move** before anything clever.
> Details live in the linked chapter. Tags: **[talk]** from the talk, **[added]** extra best practice.

## Step 0 — 60-second triage (do this every time)

```bash
# 1. Can I make it fail on demand?  (If not, that is the first problem to solve.)
# 2. What exactly did I see?  exact error text / exit code / wrong value — copy it into the journal.
# 3. Did it ever work?  YES → git bisect (ch.04).  NO → keep reading.
# 4. Is the binary built with symbols?  (ch.05)
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug -DCMAKE_EXPORT_COMPILE_COMMANDS=ON && cmake --build build -j
```

## The table

| # | What you see | Problem type | First move | Main tool | Chapter |
|---|---|---|---|---|---|
| 1 | "I have no idea what this program/repo does" | **Orientation** | Build → **run it** → count code → find `main` | `cloc`, `rg`, debugger `start` | 03 |
| 2 | "Where is the code for this feature / message / button?" | **Locate** | Grep the *visible string* (error text, log line, UI label, CLI flag) then walk callers **[added]** | `rg`, clangd "find references" | 04 |
| 3 | "What runs when I do X?" | **Control flow** | Break on a function you *know* is involved, `bt` to see who called it | `gdb`/`lldb`, `perf record -g` | 06, 09 |
| 4 | "Who changes this variable? Where did this value come from?" | **Data flow** | Hardware **watchpoint** (conditioned on the bad value) | `watch -l …  if …`, `reverse-continue` | **07**, 08 |
| 5 | "Variable name appears 100× across methods, pointers, and messages" | **Data flow at scale** | Don't read it — **watch it**. Then break at the *producer* (`post/send/enqueue`), not the consumer **[added]** | conditional watch + conditional break | **07** |
| 6 | "Segfault / abort / assert / uncaught exception" | **Crash** | Get the backtrace first. Remember: *crash site ≠ bug site* **[added]** | debugger, core dump, ASan | 12, 06 |
| 7 | "Wrong output, no crash" | **Logic / data** | Bisect the pipeline: check the value at each stage boundary | `dprintf`, conditional break, UDB/rr | 07, 08 |
| 8 | "It worked last week" | **Regression** | `git bisect run` with a script that exits 0/1 **[added]** | `git bisect`, `git log -S` | 04 |
| 9 | "It's slow / pegging CPU" | **Performance** | Sample first, don't guess | `perf record -g`, callgrind | 09 |
| 10 | "It hangs / freezes" | **Deadlock / blocked** | Attach, dump *all* threads' stacks **[added]** | `gdb -p PID` → `thread apply all bt`; `strace -p` | 12 |
| 11 | "Garbage values, corruption, leak, use-after-free" | **Memory** | Rebuild with sanitizers, rerun | `-fsanitize=address,undefined`, valgrind | 12 |
| 12 | "Only sometimes / only under load / only in release" | **Race / heisenbug** | Make it deterministic: record once, replay forever | `rr record`, UDB, TSan **[added]** | 08, 12 |
| 13 | "Won't build / link / CMake is a maze" | **Build** | See the *real* compiler command; list cache vars | `cmake --build build -v`, `cmake -LAH` | 05 |
| 14 | "Undefined reference / symbol not found / wrong lib loaded" | **Link / deps** | What does the binary need vs. have? | `nm … \| c++filt`, `ldd` / `otool -L` | 10 |
| 15 | "Third-party / closed library misbehaves" | **Code I don't own** | Observe the boundary: what goes in, what comes out | `ldd`, `ltrace`/`strace`, record & inspect API calls | 10, 08 |
| 16 | "I can't hold this class hierarchy in my head" | **Structure** | Generate a map instead of reading | `doxygen`, clangd call hierarchy | 10 |
| 17 | "Is there a test for this component?" | **Shrink scale** | Look in `tests/` *before* touching code; run just that one | `ctest -N`, `ctest -R` | 11 |
| 18 | "Task is huge, I'm drowning" | **Scale** | Find the smallest possible change; run a tiny example | tests, examples, `TODO` hunt | 11 |
| 19 | "AI told me the cause (sounds confident)" | **Unverified claim** | Make it prove it with debugger evidence | watchpoint/replay as the judge | 14 |
| 20 | "I've been stuck 30+ minutes" | **Process failure** | Stop. Write hypotheses. Change angle or ask — bring what you tried **[talk+added]** | journal | 02, 13 |

## Decision tree (when you can't tell which row)

```
Does it fail every time?
├─ NO  → make it deterministic first (loop it, fix seeds, pin threads, record it)  → rows 12
└─ YES
   ├─ Does it crash?                 → backtrace → work BACKWARDS from the bad value     → rows 6,4
   ├─ Wrong value?                   → watch the value; who wrote it last?               → rows 4,5,7
   ├─ Used to work?                  → git bisect                                        → row 8
   ├─ Slow / spinning?               → profile                                           → row 9
   ├─ Stuck / frozen?                → attach + all-thread stacks                        → row 10
   └─ Don't know where code lives?   → run it, grep the visible string, debugger bt      → rows 1–3
```

## The 12 commands to know cold

```bash
rg -n -w SYMBOL src/                                  # every textual use of a name       (✅ tested)
rg -n 'TODO|FIXME|HACK|XXX' src/                      # developer breadcrumbs            (✅ tested)
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug          # get -g                           (✅ tested)
gdb --args ./build/app --flag                         # run under debugger               (📖)
(gdb) start | bt | frame N | info locals | p *ptr      # orient inside the debugger       (📖)
(gdb) watch -l obj->field if obj->field < 0           # who made it bad?                 (📖)
(gdb) break Bus::post if m.value < 0                  # catch it at the sender           (📖)
(gdb) thread apply all bt                             # hang / deadlock                  (📖)
git bisect start BAD GOOD && git bisect run ./check.sh   # find the commit              (✅ tested)
git log -S'symbol' --oneline                          # when did this appear/disappear   (✅ tested)
perf record -g -p PID -- sleep 20 && perf report      # where is time going              (📖)
valgrind --leak-check=full --track-origins=yes ./app  # memory errors                    (📖)
```
