# 08 · Time-Travel (Reverse) Debugging — "how did I get here?"

> **[talk]** Everyone has stepped one `next` too far. *"You get to the point where you should have
> started and step over and you just get so infuriated."* Reverse debugging **records** the run so you can
> step — and `continue` — **backwards**, with the whole program state (stack, all threads) unwound to that moment.

## When to reach for it

| Situation | Why reverse helps |
|---|---|
| Bad value found, need **who wrote it last** | `watch` + `reverse-continue` stops at that exact write |
| Crash far from the cause (memory corruption, use-after-free) | Run backwards from the crash to the corrupting write |
| Heisenbug / race / "once in 50 runs" | Record the failing run **once**, replay it deterministically forever |
| Unfamiliar code, no idea of flow | Record a feature (click, request), then walk it forward *and back* (the talk's OpenTTD train demo) |
| Third-party library misbehaving | Recording shows every API call, args in, values out → compare with its docs **[talk Q&A]** |
| Need to share a failure with a teammate | A recording file can be replayed on another machine **[talk]** |

## The three options (pick by platform)

| Tool | Platform | Cost | Speed | Notes |
|---|---|---|---|---|
| **GDB built-in** `record full` | Linux (GDB ≥7.0, **[talk]**) | free | very slow — "single-stepping and noting everything that changed"; fine for *tight loops* | Doesn't scale to big apps **[talk]** |
| **rr** | Linux x86 (needs HW perf counters; flaky in VMs/containers 📖) | free, open source | low overhead (~1–2× typical) | `rr record` / `rr replay`, chaos mode for races |
| **UDB / Undo LiveRecorder** | Linux | commercial (free trial) | "50% slower to ~5–10× slower"; multithread can cost more **[talk]** | Talk's tool; same GDB commands; record on a symbol; save/share recordings |
| WinDbg Time Travel Debugging | Windows (Visual Studio ecosystem) | free | — | **[talk]** mentioned |

macOS/Apple Silicon: none of these run natively. Use a Linux VM/box for time-travel work (and note that rr needs access to
CPU performance counters, which many cloud/VM setups hide) **[added]**. **Ask what your team already has licensed** before installing anything **[talk]**.

## A · GDB built-in (works anywhere GDB does) 📖

```gdb
(gdb) break main.cpp:17
(gdb) run
(gdb) record full                   # start recording from HERE (recording from start of a big app is too slow)
(gdb) continue                      # run until the failure
(gdb) reverse-continue              # go back to the previous breakpoint/watchpoint
(gdb) reverse-next / reverse-step / reverse-finish
(gdb) watch -l tracker.m_total      # then ↓
(gdb) reverse-continue              # stops at the previous WRITE to that memory
(gdb) bt                            # the writer, as it was at that moment
(gdb) record stop
```
Set `set record full insn-number-max unlimited` if it stops recording. Docs:
<https://sourceware.org/gdb/current/onlinedocs/gdb/Process-Record-and-Replay.html> · wiki (linked in the slides): <https://sourceware.org/gdb/wiki/ReverseDebug>

## B · rr (open source, Linux) 📖

```bash
rr record ./build/app --case 42           # run normally; trace saved under ~/.local/share/rr/
rr replay                                 # replays the LATEST recording inside GDB, deterministically
(rr) continue
(rr) watch -l tracker.m_total
(rr) reverse-continue                     # same commands as GDB
rr record --chaos ./build/app             # randomizes scheduling → shakes out races, then replay the failure
rr ls                                     # list recordings;  rr replay ~/.local/share/rr/app-0
```
Docs: <https://rr-project.org/> · usage: <https://github.com/rr-debugger/rr/wiki/Usage>
Tip: a recording that reproduces is **permanent** — you can sleep on it and keep investigating tomorrow.

## C · UDB / LiveRecorder (the talk's tool) 📖 (commands from slide 41)

```bash
# 1) Record — optionally START recording only when a symbol is hit (skip startup noise)
nm build/openttd | grep MainLoop                       # find the mangled symbol name  (nm is on slide 41)
live-record --record-on symbol:_Z12PostMainLoopv ./build/openttd
#   → writes a recording like  openttd-466718-2025-06-10T19-18-20.511.undo
# 2) Replay & explore — same GDB commands plus reverse-*
udb openttd-466718-2025-06-10T19-18-20.511.undo
(udb) reverse-next / reverse-step / reverse-finish
(udb) watch -l train->profit_this_year      # the talk's demo: stops on EVERY change (daily running costs)
(udb) continue                               # each stop shows old → new value; the talk then added a
                                             # "value went UP" condition to stop only when the train earned money
(udb) reverse-continue                       # …and back to the previous write
```
Recording can be done on a server and analyzed elsewhere ("record and replay separately") **[talk]**.
Free trial (QR code on slides): <https://undo.io/udb-free-trial/> · guide to symbols: <https://undo.io/resources/guide-to-symbols-debug-info/>

## The three reverse recipes to memorize

```gdb
# 1. Who wrote this value last?
watch -l OBJ.FIELD        →  reverse-continue          →  bt

# 2. How did I get into this function with this argument?
break FUNC if ARG == BAD  →  continue  →  reverse-step / reverse-finish ... or up + reverse-continue to the caller

# 3. Where did this pointer become null / get freed?
watch -l PTR              →  reverse-continue          →  bt
```

## What the talk's demos showed **[talk]**
1. **Step backwards** with the whole app state unwound — "every time you step backwards the entire state of the application is unwound".
2. **Reverse to a watchpoint:** "set a watch point and do `reverse-continue` and it will run backwards and stop at the point that data was last modified."
3. **Follow the data** (OpenTTD train): watch `profit_this_year` → stops daily on running costs; add condition "gets larger" → stops when the train unloads. *Then explore from there.*
4. **AI constrained by evidence** (MySQL bug): the AI confidently proposed wrong root causes; recording + making the AI prove each hypothesis against the recording got to the real cause (ch.14).

## Gotchas **[added]**
- Record **late** (near the bug), not from process start, unless your recorder is fast.
- Non-deterministic inputs (time, network, random) are fine for rr/UDB — they record them; GDB `record full` can fail on some syscalls/instructions.
- A recording only contains what ran: if the bug never happened in that run, there is nothing to find. Loop until the failing run is captured (`while rr record ./app; do :; done`).
- Debug symbols still matter (ch.05). Recording an optimized build works but variables may be `<optimized out>`.

## Links
- GDB reverse execution — <https://sourceware.org/gdb/current/onlinedocs/gdb/Reverse-Execution.html> · wiki — <https://sourceware.org/gdb/wiki/ReverseDebug>
- rr — <https://rr-project.org/>
- Undo: *Time travel debugging tames complex codebases and overconfident AI* (Chris's MySQL article, slide 78) — <https://undo.io/resources/time-travel-debugging-tames-complex-codebases-and-overconfident-ai/>
- Greg Law, *Time Travel Debugging* (Meeting C++ 2023) — <https://www.youtube.com/watch?v=qyGdk6QMpMY>
- Greg Law, *Cool New Stuff in GDB 9 and GDB 10* (CppCon 2021) — <https://www.youtube.com/watch?v=xSnetY3eoIk>
- Case studies from the slides: Quake 2 — <https://www.jwhitham.org/2015/05/review-undodb-reversible-debugger.html> · Doom, "Reviving a zombie" — <https://www.youtube.com/watch?v=tjJLZ1da6xs>
