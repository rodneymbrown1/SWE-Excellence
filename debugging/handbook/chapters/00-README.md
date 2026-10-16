# SWE-Excellence · Debugging & RCA Handbook

> **Goal:** get from "I'm lost in this codebase" to a root cause *fast* by picking the right
> **angle** (what kind of problem is this?) and the right **tool** (what answers that question?).

Source material: *Understanding Large and Unfamiliar Codebases* — Mike Shah & Chris Croft-White,
C++ on Sea 2025 (transcript, slides, and your own notes in `context.txt`), then extended with
best practices the talk doesn't cover. Everything is tagged so you always know which is which.

## How to use this handbook

1. Something is on fire → open **[01-symptom-playbook.md](01-symptom-playbook.md)**. Find your symptom, get the strategy and the first command.
2. Need depth on a tool → jump to its chapter (index below).
3. **Print version → `../print/fire-handbook.pdf`** (16 US-Letter pages, one sheet per problem type; **sheet number = chapter number**).
   Same source as the on-screen page `../print/fire-handbook.html`; rebuild the PDF with `../print/build-pdf.sh`.
4. Want to practice before you need it → `../practice-sandbox/` has a tiny C++/CMake project with a planted bug that mimics your real problem
   (one variable, many writers, a message queue) and a `ctest` that fails until you fix it. Chapter 07 walks through it.
5. The talk's own material (transcript, your notes, the 83-slide PDF as text, the GDB cheat sheet) lives in
   `../../understanding-large-and-unfamiliar-codebases-mike-shah-and-chris-croft-white-cpp-on-sea/` (slides in its `slides/` folder).

## Tags used throughout

| Tag | Meaning |
|---|---|
| **[talk]** | Directly from the C++ on Sea 2025 talk / slides |
| **[notes]** | From your own `context.txt` notes |
| **[added]** | Best practice added for SWE-excellence — *not* in the talk |
| ✅ **tested** | Command was actually run on this Mac (macOS, zsh, Apple clang, CMake 4.x) while writing this |
| 📖 **docs** | Command comes from official docs / the GDB cheat sheet but was **not** run here (no Linux box, no `gdb`/`perf`/`valgrind` on this Mac) — try it once in a safe place before trusting it under pressure |

## Chapter index

| # | Chapter | Use it when… |
|---|---|---|
| 01 | [Symptom playbook](01-symptom-playbook.md) | **Start here.** "It does X, I need to find why." |
| 02 | [The debug loop (method)](02-method-the-debug-loop.md) | You're thrashing; need a process, not a tool |
| 03 | [First 30 minutes in a new codebase](03-first-30-minutes.md) | Day one / new component / new repo |
| 04 | [Search & navigate](04-search-and-navigate.md) | "Where is it?" / "Who touches it?" / git archaeology |
| 05 | [Build system & debug symbols](05-build-system-and-symbols.md) | CMake confusion, no symbols, optimized-away variables |
| 06 | [Debugger fundamentals](06-debugger-fundamentals.md) | Run, break, step, inspect (GDB + LLDB) |
| 07 | [Follow the data](07-follow-the-data.md) | **Your "100 instances of one variable" problem** |
| 08 | [Time-travel debugging](08-time-travel-debugging.md) | "How did I get here?" |
| 09 | [Profilers & call graphs](09-profilers-and-call-graphs.md) | "What actually runs / where is the time?" |
| 10 | [Structure, docs, dependencies](10-structure-docs-dependencies.md) | Need a map: classes, libs, includes |
| 11 | [Shrink the problem: tests, examples, first tasks](11-reduce-scale-tests-first-tasks.md) | Codebase too big to hold in your head |
| 12 | [Memory, crashes, concurrency](12-memory-crash-concurrency.md) | Segfault, leak, race, hang **[added]** |
| 13 | [Workspace & investigation journal](13-workspace-and-journal.md) | tmux/vim layout, notes template |
| 14 | [AI assistance: trust but verify](14-ai-assist.md) | Using AI without being fooled by it |
| 15 | [Resources & links](15-resources-and-links.md) | Every link in one place + the talk map + glossary |

## The whole handbook in 8 lines

```
1. REPRODUCE   make it fail on demand, as small as possible        (run it first)
2. LOCALIZE    which layer? which data? which commit? which moment? (bisect everything)
3. OBSERVE     look with a tool, don't guess                       (debugger / profiler / sanitizer)
4. HYPOTHESIZE one falsifiable sentence                            ("m_total goes <0 in applyDelta")
5. TEST IT     cheapest experiment that could prove you wrong
6. FIX         at the root cause, not the crash site
7. PROVE       regression test; revert fix → bug returns
8. RECORD      one paragraph in the journal                         (future you will thank you)
```

## Things found by actually running the commands (worth knowing)

- **`rg` with no path hangs** when stdin isn't a terminal (scripts, pipes, CI). Always end with a path: `rg 'x' .` (ch.04).
- **LLDB watchpoint conditions run in the frame that wrote the memory**, so a local like `tracker` from `main` is "undeclared" there. Use `this->m_total` or a raw address (ch.07).
- **`assert` disappears in Release** (`-DNDEBUG`): the sandbox prints `total = -10` and exits 0. A green Release proves nothing about an assert (ch.05).
- **macOS `dwarfdump` on a bare binary prints nothing**: debug info lives in the `.dSYM` (`dsymutil` first) (ch.05).
- **`xctrace` needs full Xcode**, not just Command Line Tools (ch.09).
- **A conditional breakpoint on the *producer* (`Bus::post`) found the planted bug in one step**; a watchpoint alone only shows the *delivery* (ch.07).

## A note on your environment

You're on macOS (zsh) now; the Raytheon codebase is most likely built on **Linux** (GDB, perf,
valgrind, ldd). Each chapter gives the Linux command first and the macOS/LLDB equivalent where
one exists. Before installing anything at work, **ask what tools are already approved/installed**
— the speakers explicitly suggest this, and it avoids security-policy surprises **[talk]**.

> ⚠️ `context.txt` links the video as `…watch?v=qmte-ZrzBKUm` — that ID has a stray trailing
> character and probably won't resolve. The slide deck and Greg Law's related talk links are in
> chapter 15.
