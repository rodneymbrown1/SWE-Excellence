# 15 · Resources, Links & the Talk Map

## A · The talk in one page — and where each part lives in this handbook

*Understanding Large and Unfamiliar Codebases* — Mike Shah & Chris Croft-White (Undo), C++ on Sea, 24 June 2025, 60 min, 83 slides.
Demo codebase: **OpenTTD** (≈188k C++, 123k headers; "93,000 lines of D" was CMake mis-detected).

| Talk section (slides) | Core message | Tools shown | Handbook chapter |
|---|---|---|---|
| **Why it's hard** (11–14) | Scale, complexity, no docs, Conway's law, human factors; you can't hold 1M lines (≈18,000 pages ≈ 14× *War and Peace*) in your head | — | 02 |
| **Why this talk / reading code** (15–19) | We write far less than we read; school rarely teaches reading big codebases | — | 02, 13 |
| **Three themes** (20) | 1) control flow, 2) scale, 3) human factors | — | 02 |
| **Project scale** (24) | Measure first | `cloc` | 03 |
| **Run it; find entry points** (26–29) | Run the program; anchor on `main()`; log what's before/after main | `grep -irn -I --include=*.cpp "main()"` | 03, 04 |
| **Debug symbols** (30–31) | The KEY: build with `-g` / `CMAKE_BUILD_TYPE=Debug`; symbols ⟂ optimization | `cmake -DCMAKE_BUILD_TYPE=Debug ..`, `gdb -ex 'attach $PID' app.debug` | 05 |
| **Step-by-step debugging** (32–34) | Debugger = code-understanding tool; attach to a running process; pause with Ctrl-C | `gdb`, `sudo gdb -p PID`, `next/step/finish/bt/kill` | 06 |
| **Reverse debugging** (35–43) | Step & run backwards; record on a symbol; replay anywhere; **watchpoints = follow the data** | GDB `reverse-*`, **UDB**, `live-record --record-on`, `nm`, `ptype`, rr | 07, 08 |
| **Keep a journal** (44) | Greppable text/Google Doc; Carmack `.plan` | — | 13 |
| **Profilers** (45–51) | Sampling shows hot paths; attach with `-p`; callgraph visual | `perf record -g [-p PID]`, `perf report`, `valgrind --tool=callgrind`, `kcachegrind` | 09 |
| **Scale** (52–53) | Reduce what you need to understand — subsystems, not everything | — | 11 |
| **Screens / window mgmt** (54–55) | Big screen; tmux + vim | `tmux`, `vim` | 13 |
| **Generate docs** (56–59) | No docs? generate; learn naming/error conventions | `doxygen -g`, `doxygen Doxyfile` | 10 |
| **Code you don't own** (60–61) | Shared libs; offline docs | `ldd`, Dependency Walker, `otool`, Zeal/Dash | 10 |
| **Tests & examples** (62) | Run tests/samples to shrink scale | CTest/gtest | 11 |
| **Other tips** (63–65) | Reformat; design patterns; software cities; AOSA | `clang-tidy`, `indent` | 10 |
| **Human factors** (67–73) | Pick a good first task; grep TODO/FIXME; fix warnings; ask well; be kind | `grep -irn -I --include=*.cpp "TODO" ./src/` | 11, 02 |
| **AI bonus** (74–78) | Helpful, overconfident; trust but verify; TTD constrains AI | Sourcegraph, ChatDBG, Claude Code | 14 |
| **Summary / resources** (79–81) | Tools for control flow; reduce scale; ask for help | — | all |

**Q&A points worth remembering:** attaching to a *live* process lets you skip startup; closed-source library → ask for debug build, else record the API calls;
"ask what tools are already in use"; "bring something to the table when you ask."

## B · Your own notes → chapter map (`context.txt`)

| Your note | Where |
|---|---|
| "Looking for main… `cloc`… step 1 run your program" | 03 |
| "Debug symbols… treasure hunt… run with debug symbols" | 05 |
| "Step-by-step debugging… running application… backwards (time travel)" | 06, 08 |
| "GDB Cheat Sheet.pdf", AOSA GDB | 06 (+ `slides/`) |
| "**Conditional watchpoints blew my mind**" | **07** |
| "perf seemed useful… perfing a running process is crazy" | 09 |
| "tmux today… vim for a couple weeks" | 13 |
| "doxygen… dependency walker tools" | 10 |
| "look for a tests folder… is there already a test for this component?" | 11 |
| "100 instances of a variable… pointers… messaging system" | **07** (+ practice sandbox) |
| "cmake files everywhere" | 05 |

## C · Every link, grouped

### From the talk's slides
- Slides repo — <https://github.com/philsquared/cpponsea2025-slides> (PDF: `Presentations/Understanding_Large_and_Unfamiliar_Codebases.pdf`) · local copy: `../understanding-large-and-unfamiliar-codebases-…/slides/`
- OpenTTD — <https://www.openttd.org/> · issues — <https://github.com/OpenTTD/OpenTTD/issues> · development — <https://www.openttd.org/development>
- GDB cheat sheet (Haisenko) — <https://darkdust.net/files/GDB%20Cheat%20Sheet.pdf>
- How a debugger works (AOSA) — <https://aosabook.org/en/v2/gdb.html> · AOSA index — <https://aosabook.org/en/>
- GDB reverse debugging wiki — <https://sourceware.org/gdb/wiki/ReverseDebug>
- Debug info: Red Hat — <https://developers.redhat.com/articles/2022/01/10/gdb-developers-gnu-debugger-tutorial-part-2-all-about-debuginfo> · Undo — <https://undo.io/resources/guide-to-symbols-debug-info/>
- UDB free trial — <https://undo.io/udb-free-trial/> · MySQL + overconfident AI — <https://undo.io/resources/time-travel-debugging-tames-complex-codebases-and-overconfident-ai/>
- KCachegrind usage — <https://kcachegrind.sourceforge.net/html/Usage.html> · Doxygen — <https://www.doxygen.nl/> · Doxygen 1-min demo — <https://www.youtube.com/watch?v=tLPHQMosF9M>
- Carmack `.plan` — <https://garbagecollected.org/2017/10/24/the-carmack-plan/> · note-taking talk — <https://www.youtube.com/watch?v=SW1fzrB-UEg>
- MIT Missing Semester — <https://missing.csail.mit.edu/> · Conway's law — <https://www.jeffwinterinsights.com/insights/conways-law-enterprise-architecture>
- JetBrains data-flow analysis (slide 12) — <https://blog.jetbrains.com/clion/2023/11/striving-for-better-cpp-code-part-i-data-flow-analysis-basics/>
- Software cities — <https://ieeexplore.ieee.org/document/4290706> · <https://www.cs.nmt.edu/~jeffery/city-surv.pdf>
- Sourcegraph — <https://sourcegraph.com/> · ChatDBG — <https://github.com/plasma-umass/ChatDBG>
- **Talks (slide 80):** Greg Law, *Time Travel Debugging* (Meeting C++ 2023) <https://www.youtube.com/watch?v=qyGdk6QMpMY> ·
  *Back to Basics: Debugging in C++* (CppCon 2023) <https://www.youtube.com/watch?v=qgszy9GquRs> · Mike Shah (CppCon 2022) <https://www.youtube.com/watch?v=YzIBwqWC6EM> ·
  *Cool New Stuff in GDB 9 and 10* <https://www.youtube.com/watch?v=xSnetY3eoIk> · *Debugging Linux C++* (2018) <https://www.youtube.com/watch?v=V1t6faOKjuQ> ·
  *GDB – A Lot More Than You Knew* (2016) <https://www.youtube.com/watch?v=-n9Fkq1e6sg>
- Case studies: Quake 2 — <https://www.jwhitham.org/2015/05/review-undodb-reversible-debugger.html> · Doom — <https://www.youtube.com/watch?v=tjJLZ1da6xs>

> Note: `context.txt` links the video as `…watch?v=qmte-ZrzBKUm`. That ID has an extra trailing "m" (YouTube IDs are 11 characters) so it likely won't resolve;
> search for the title on the C++ on Sea YouTube channel. <https://cpponsea.uk/2025/session/understanding-large-and-unfamiliar-codebases>

### Official tool docs (added)
| Tool | Docs |
|---|---|
| GDB | <https://sourceware.org/gdb/current/onlinedocs/gdb/> |
| LLDB | <https://lldb.llvm.org/> · GDB→LLDB map <https://lldb.llvm.org/use/map.html> |
| rr | <https://rr-project.org/> |
| perf | <https://perfwiki.github.io/main/> · <https://www.brendangregg.com/perf.html> |
| FlameGraph | <https://github.com/brendangregg/FlameGraph> |
| Valgrind | <https://valgrind.org/docs/manual/manual.html> |
| Sanitizers | <https://clang.llvm.org/docs/AddressSanitizer.html> · <https://clang.llvm.org/docs/ThreadSanitizer.html> · <https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html> |
| CMake | <https://cmake.org/cmake/help/latest/> · CTest <https://cmake.org/cmake/help/latest/manual/ctest.1.html> |
| ripgrep | <https://github.com/BurntSushi/ripgrep/blob/master/GUIDE.md> |
| git bisect / log / blame | <https://git-scm.com/docs/git-bisect> · <https://git-scm.com/docs/git-log> · <https://git-scm.com/docs/git-blame> |
| clangd | <https://clangd.llvm.org/> |
| Doxygen / Graphviz | <https://www.doxygen.nl/manual/> · <https://graphviz.org/> |
| tmux / vim | <https://github.com/tmux/tmux/wiki> · <https://vimhelp.org/> |
| cppreference | <https://en.cppreference.com/> |
| Zeal / Dash | <https://zealdocs.org/> · <https://kapeli.com/dash> |

### Books worth owning (added; names only, find them at your bookstore)
- *Debugging: The 9 Indispensable Rules* — David J. Agans (method, ch.02)
- *Working Effectively with Legacy Code* — Michael Feathers (characterization tests, ch.11)
- *Design Patterns* ("Gang of Four") — cited in the talk (ch.10)
- *Why Programs Fail* — Andreas Zeller (systematic/"scientific" debugging, delta-debugging)
- *The Linux Programming Interface* — Michael Kerrisk (processes, signals, /proc — makes `strace`/`gdb -p` make sense)

## D · Glossary (the words that kept tripping you up)
| Term | Meaning |
|---|---|
| **Debug symbols / debug info** | Extra data in the binary (names, types, line numbers) that lets a debugger map machine code ↔ source. Flag: `-g`. |
| **Optimization** | Compiler rewriting your code to be faster. `-O0` none, `-O2` typical release. Orthogonal to symbols. |
| **Breakpoint / watchpoint** | Stop at a *place in code* / stop when *a memory location* changes. |
| **Backtrace (`bt`)** | The chain of calls that led to the current point, innermost first. |
| **Frame** | One entry on the call stack (a function call and its locals). |
| **Sampling profiler** | Periodically checks "what is running now?" thousands of times, then counts. |
| **Time-travel / reverse debugging** | Record a run, then step/continue backwards. |
| **Core dump** | A snapshot of a crashed process's memory — debug it afterwards. |
| **Sanitizer** | Compiler-inserted checks (ASan/UBSan/TSan) that report memory/UB/race bugs at the exact line. |
| **Entry point** | Where execution starts: `main`, plus static initializers, thread starts, event handlers. |
| **Compile database** | `compile_commands.json` — exact compile command per file; powers clangd. |
| **RCA** | Root-cause analysis — the *decision* that made the bug possible, not just the line that crashed. |
