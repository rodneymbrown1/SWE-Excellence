# 05 · Build System & Debug Symbols — "why can't the debugger see anything?"

> The talk's single loudest instruction: *"A **key** that will make your life easier — build/compile
> with debug information"* **[talk]**. Every debugger and profiler in this handbook gets better with it.

## Symbols vs optimization — two separate dials **[talk]**

People confuse "debug build" with "has debug symbols". They are **orthogonal**:

| Flag | Controls | Effect on debugging |
|---|---|---|
| `-g` | Debug **info** (symbols, line tables, types) | Names, source lines, `p variable`, `bt` with args |
| `-O0` / `-O2` / `-O3` | **Optimization** | `-O0`: code runs as written. `-O2`: variables `<optimized out>`, lines jump, functions inlined |

```
-g -O0   Debug            easiest to debug       (CMAKE_BUILD_TYPE=Debug)
-g -O2   RelWithDebInfo   ship-like + symbols    ← use when the bug only shows in release
   -O2   Release          no symbols             (and asserts compiled out: -DNDEBUG)
-g -Og   "debuggable optimized"  good middle ground for GCC/Clang
```
The speakers: it is common (games) to debug the **optimized** build you actually ship — add `-g` to it
rather than switching to Debug **[talk]**.

### ⚠️ "Works in release" — proven on the practice sandbox ✅ tested
```bash
cd practice-sandbox
cmake -S . -B build     -DCMAKE_BUILD_TYPE=Debug   && cmake --build build     && ./build/sandbox
#   Assertion failed … total = -10, exit 134
cmake -S . -B build-rel -DCMAKE_BUILD_TYPE=Release && cmake --build build-rel && ./build-rel/sandbox
#   total = -10, exit 0     ← bug is STILL there; the assert() was compiled out by -DNDEBUG
```
Lesson **[added]**: a green Release build proves nothing if the check was an `assert`.

## The CMake commands you actually need — ✅ tested unless marked

```bash
# configure + build, out-of-source, with symbols and a compile database
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build build -j                          # -j = parallel

# ship-like with symbols
cmake -S . -B build-rwdi -DCMAKE_BUILD_TYPE=RelWithDebInfo

# SEE the real compiler command (flags, -g, -O, -D defines, include paths)
cmake --build build --verbose                   # or:  VERBOSE=1 cmake --build build
#   → prints e.g.  … -g -std=gnu++17 -Wall -Wextra -o …

# what is this build configured with?  (cache variables + help text)
cmake -LAH -N build | less                      # -N = just list, don't re-run configure
grep -E 'CMAKE_BUILD_TYPE|CMAKE_CXX_FLAGS' build/CMakeCache.txt

# what can I build?
cmake --build build --target help

# one target only (much faster than "all")
cmake --build build --target sandbox -j

# multi-config generators (Xcode / Visual Studio / Ninja Multi-Config) need --config
cmake --build build --config Debug              # 📖

# turn on extra tracing when a CMakeLists is a maze
cmake -S . -B build --trace-expand --trace-source=CMakeLists.txt 2>&1 | less   # 📖
cmake --debug-find …                            # 📖 why was/wasn't a library found?
```

### A map of the maze: the target dependency graph ✅ tested
```bash
cmake --graphviz=build/deps.dot build           # writes build/deps.dot (+ per-target files)
dot -Tsvg build/deps.dot -o build/deps.svg      # 📖 needs graphviz (brew/apt install graphviz); not installed here, so not run
```
Gives you "which libraries depend on which" without reading 40 CMakeLists files. Print it, put it in the journal.

### Reading a CMakeLists fast **[added]**
You only need five commands to follow 90% of CMake:
`add_executable` / `add_library` (what gets built) · `target_link_libraries` (who depends on whom) ·
`target_include_directories` (where headers come from) · `target_compile_definitions` /
`target_compile_options` (flags & `-D`s) · `add_subdirectory` (follow the tree). Everything else is detail.
`rg -n 'add_(executable|library)|target_link_libraries|add_subdirectory' --glob 'CMakeLists.txt' .`

### 3rd-party code in debug too **[talk]**
"In some instances this may also include making sure to build 3rd party libraries in debug as well."
With `FetchContent`/`ExternalProject`/vcpkg/Conan the library often builds Release by default.
Symptom: you step into a library call and the debugger shows only assembly/`??`. Fix: pass
`-DCMAKE_BUILD_TYPE=Debug` through to the dependency (or ask for a debug build — see "code you don't own", ch.10).

## Verify you really have symbols (do this BEFORE blaming the debugger)

| Check | macOS ✅ | Linux 📖 |
|---|---|---|
| Is there debug info? | `dsymutil build/app && dwarfdump --debug-info build/app.dSYM \| head` ✅ (on macOS the info lives in the `.dSYM`; `dwarfdump` on the bare binary prints nothing) | `file build/app` → "…with debug_info, not stripped" · `readelf --debug-dump=info build/app \| head` |
| Symbol table | `nm build/app \| c++filt \| grep Foo` | `nm -C build/app \| grep Foo` |
| Compiler flags used | `cmake --build build --verbose` | same |
| Stripped? | `file build/app` | `file build/app` ("stripped") |

In the debugger: `(gdb) info sources` / `(gdb) list main` — if "No symbol table is loaded" or `bt` shows
`?? ()` → no symbols. `<optimized out>` for a variable → optimization, not missing symbols; rebuild `-Og`/`-O0` for that file.

## Symbols for a system you can't rebuild **[talk]**

The slide: *"If you're in a live system, you can `gdb -ex 'attach $PID' app.debug` to add debug info."*
Production binaries are usually stripped with the debug info shipped **separately** (`app.debug`,
a `-dbgsym` package, or a `debuginfod` server). That's what the "downloading debug symbols…"
messages in the live demo were — GDB fetching them on the fly **[added explanation]**.

```bash
# GDB (Linux) — point it at the separate debug file                                     📖
gdb -ex 'symbol-file /path/to/app.debug' -ex 'attach 12345'
# or let it download automatically (distro debuginfod servers)                           📖
export DEBUGINFOD_URLS="https://debuginfod.elfutils.org/"     # set to your org's server if it has one
```
Reading: Red Hat "all about debuginfo" and Undo's symbols guide (links below).

## Make the build easier to live with **[added]**
- **Write down the working build recipe** in the journal the first time it works. The talk: getting
  it to build "can take days" and a good first contribution is documenting it.
- Use a **separate build dir per config** (`build/`, `build-rel/`, `build-asan/`) so you never reconfigure back and forth.
- `ccache` makes rebuilds fast: `cmake -DCMAKE_CXX_COMPILER_LAUNCHER=ccache …`  📖
- `ninja` instead of Make: `cmake -G Ninja -S . -B build` (faster, clean output)  📖
- Compiler warnings are free hints: `-Wall -Wextra`; the talk lists *fixing warnings* as a good first task **[talk]**.

## Links
- CMake `CMAKE_BUILD_TYPE` — <https://cmake.org/cmake/help/latest/variable/CMAKE_BUILD_TYPE.html>
- `cmake(1)` command line (`--build`, `--graphviz`, `-L`, `--trace`) — <https://cmake.org/cmake/help/latest/manual/cmake.1.html>
- CMake tutorial — <https://cmake.org/cmake/help/latest/guide/tutorial/index.html>
- Red Hat: GDB developer's tutorial part 2 — all about debuginfo (from the slides) — <https://developers.redhat.com/articles/2022/01/10/gdb-developers-gnu-debugger-tutorial-part-2-all-about-debuginfo>
- Undo: guide to symbols & debug info (from the slides) — <https://undo.io/resources/guide-to-symbols-debug-info/>
- debuginfod — <https://sourceware.org/elfutils/Debuginfod.html>
