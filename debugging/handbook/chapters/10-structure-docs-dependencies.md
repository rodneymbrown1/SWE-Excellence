# 10 · Structure, Docs & Dependencies — "I need a map"

> **[talk]** *"No documentation — no problem. Generate your own."* And for code you don't own: look at
> what it links against, and read fast offline docs. Seeing the same code **represented in different ways**
> (raw source → generated docs → diagrams) is how you build a mental model.

## 1 · Generate documentation: Doxygen **[talk, slides 56–59]**

```bash
doxygen -g                    # writes a default Doxyfile (slide 57)
doxygen Doxyfile              # generates html/ (and latex/ unless disabled)   (slide 57)
open html/index.html          # macOS   |   xdg-open html/index.html  (Linux)
```
Install: `brew install doxygen graphviz` / `apt install doxygen graphviz`. 📖 (not installed on this Mac)

The default config produces almost nothing for undocumented code. Flip these in `Doxyfile` **[added — standard Doxygen options]**:

```ini
INPUT                = src include
RECURSIVE            = YES
EXTRACT_ALL          = YES     # document everything, even uncommented code   ← the key one
EXTRACT_PRIVATE      = YES
EXTRACT_STATIC       = YES
HAVE_DOT             = YES     # needs graphviz: inheritance + collaboration diagrams
CLASS_GRAPH          = YES
COLLABORATION_GRAPH  = YES
CALL_GRAPH           = YES     # who does this function call
CALLER_GRAPH         = YES     # who calls this function   ← "incoming calls" for free
INCLUDE_GRAPH        = YES
SOURCE_BROWSER       = YES     # click from docs into source
GENERATE_LATEX       = NO
```
**What you get [talk]:** class lists, **inheritance diagrams**, members with types, call/caller graphs.
**What it teaches you:** naming conventions, return types (`int32_t`? `StringID`? snake_case?), whether errors are codes or exceptions —
"conventions you can learn about… and often tell you where this code is coming from: *my* code or a library?" Take notes; it pays off at **code review** **[talk]**.
Video the speakers pointed to (1-minute demo + config options): <https://www.youtube.com/watch?v=tLPHQMosF9M>
Docs: <https://www.doxygen.nl/manual/> · alternative mentioned: DoxyPress.

## 2 · Dependency maps you can generate in 10 seconds

| What | Command | Status |
|---|---|---|
| Target graph (CMake) | `cmake --graphviz=build/deps.dot build && dot -Tsvg build/deps.dot -o build/deps.svg` | ✅ `.dot` produced |
| Which headers does this file pull in? | `clang++ -H -fsyntax-only -Isrc src/foo.cpp 2>&1 \| grep -v '^\.\.\.' \| head -50` | 📖 |
| Make-style dependency list | `clang++ -MM -Isrc src/foo.cpp` | ✅ prints the headers `foo.cpp` includes |
| Include "who includes me?" | `rg -n '#include\s+"bus.hpp"' src/` | ✅ |
| Class diagram from clang | `clang++ -Xclang -ast-dump -fsyntax-only src/foo.cpp \| head` (verbose) | 📖 |
| Header-only usage lint | `include-what-you-use` | 📖 optional |

## 3 · Code you don't own — shared libraries **[talk, slide 60 + Q&A]**

The slide: *"Finding shared libraries is easy — just run `ldd`; Dependency Walker on Windows."* The talk points out macOS has `otool`.

| Question | Linux 📖 | macOS ✅ |
|---|---|---|
| What libs does the binary need? | `ldd ./build/app` · `readelf -d app \| grep NEEDED` | `otool -L build/app` ✅ |
| What symbols does it **define**? | `nm -C --defined-only app` | `nm build/app \| c++filt` ✅ |
| What symbols does it **need** (undefined)? | `nm -C -u app` | `nm -u build/app \| c++filt` |
| What's exported by a library? | `nm -D --defined-only -C libfoo.so` | `nm -gU libfoo.dylib` |
| Which lib did the loader actually pick? | `LD_DEBUG=libs ./app 2>&1 \| head` | `DYLD_PRINT_LIBRARIES=1 ./build/app` |
| Windows | Dependency Walker / `dumpbin /dependents app.exe` | — |

`ldd` output → "which graphics / network / crypto libs does this use?" → those are the boundaries where code isn't yours **[talk]**.
**Do not run `ldd` on untrusted binaries** (it can execute them) — use `readelf -d` instead **[added, security hygiene]**.

### Library misbehaves and you have no source? **[talk Q&A]**
1. Ask for a **debug build** or symbols (ch.05) — first choice.
2. **Record** a run (rr/UDB, ch.08): you can see every API call, the arguments passed in, and what came back — then compare to the API docs. "Am I using it correctly?"
3. No recorder? Intercept at the boundary: `ltrace -f -e 'libfoo*' ./app` (Linux), `strace -f -e trace=network ./app` for syscalls, or a breakpoint on the library function and `bt` + `info args`.
4. Last resort — debugging from disassembly. The speakers: "not great… ideally we don't recommend it." ⚠️

## 4 · Offline docs — fast lookup **[talk, slide 61]**

*"No latency, usually easier to organize and keep tabs; more powerful search (e.g. fuzzy)."*
- **Zeal** (free, Linux/Windows) — <https://zealdocs.org/> · **Dash** (macOS) — <https://kapeli.com/dash>
- Docsets to install first: *C++* (cppreference), *CMake*, *Boost*/whatever third-party libs your repo links (use `ldd`/`otool -L` to find them).

## 5 · Reformat and recognize patterns **[talk, slides 63–65]**

- Ugly/inconsistent code? Reformat a **copy** to read it: `clang-format -style=LLVM file.cpp > /tmp/readable.cpp` (or `-i` on a scratch branch). Don't commit
  drive-by reformatting of files you don't own **[added]**. `clang-tidy` finds bug patterns and modernization hints.
- **Study design patterns** — the talk: *observer, visitor… event-loop, component pattern, plugin system* tend to show up. Your messaging system **is** the
  **Observer / publish–subscribe** pattern (`subscribe` + `post` in `practice-sandbox/src/bus.hpp`). Naming the pattern tells you what to look for:
  *who subscribes, who posts, where's the dispatch loop?* "Writing a toy version of these patterns can help you understand the context in a larger system." (That's what the sandbox is.)
- **Find a similar, smaller system** and read how *it's* documented — AOSA (Architecture of Open Source Applications) has case studies: <https://aosabook.org/en/>
- Game-ish projects: look at a small open-source game's main loop for the "event loop" mental model **[talk]**.

## 6 · Software visualization (awareness only) **[talk, slide 63]**
"Software cities": blocks = directories/namespaces, buildings = files; useful as AI-generated code grows. References on the slide:
<https://ieeexplore.ieee.org/document/4290706> · <https://www.cs.nmt.edu/~jeffery/city-surv.pdf>. Try-it-now substitute: the CMake graph + Doxygen caller graphs.

## Links
- Doxygen — <https://www.doxygen.nl/> · manual — <https://www.doxygen.nl/manual/> · Graphviz — <https://graphviz.org/>
- `ldd(1)` — <https://man7.org/linux/man-pages/man1/ldd.1.html> · `nm(1)` — <https://man7.org/linux/man-pages/man1/nm.1.html> · `c++filt` (binutils)
- clang-format — <https://clang.llvm.org/docs/ClangFormat.html> · clang-tidy — <https://clang.llvm.org/extra/clang-tidy/>
- Design Patterns (the "Gang of Four" book, cited on slide 64) · AOSA — <https://aosabook.org/en/>
- Conway's Law (slide 14) — <https://www.jeffwinterinsights.com/insights/conways-law-enterprise-architecture>
