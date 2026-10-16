# 03 · The First 30 Minutes in an Unfamiliar Codebase

> Talk order **[talk]**: measure size → build → **run it** → find the entry point → run it under a debugger.
> Goal of this chapter: a one-page mental map and a working debug build before you read a single function.

## Checklist

```
[ ] 1. Size & languages          cloc
[ ] 2. Layout                    tree / ls, README, docs/, tests/, CMakeLists.txt
[ ] 3. Build it (with -g)        cmake … -DCMAKE_BUILD_TYPE=Debug
[ ] 4. RUN it                    see real behavior
[ ] 5. Find entry points         rg / grep for main; debugger `start`
[ ] 6. Tests exist?              ctest -N / look for tests/ for YOUR component   [notes]
[ ] 7. History                   git log --oneline -20 -- <your dir>
[ ] 8. Journal entry #1          what you learned + open questions
```

## 1 · Size and languages — `cloc` **[talk, notes]**

```bash
cloc .                                   # lines of code by language
cloc --vcs=git                           # only tracked files (skips build/, vendored junk)
cloc src/ --by-file | sort -k5 -n | tail # biggest files in src/
cloc . --exclude-dir=build,third_party   # ignore generated/vendored dirs
```
Install: `brew install cloc` / `apt install cloc`. Alternatives: `tokei`, `scc`.
**Why:** tells you scale (OpenTTD: ~188k C++, ~123k headers) and surprises — *"93,000 lines of 'D'?"
that was CMake mis-detected*. Lots of CMake/Python/shell = the build is part of the problem.
Docs lines ≈ 0 means you'll lean on generated docs (ch.10).

## 2 · Layout

```bash
tree -L 2 -I 'build|.git|third_party'    # ✅ tree installed here
ls; cat README* | head -50
fd -e txt CMakeLists . | head            # or: find . -name CMakeLists.txt | head
find . -type d -name '*test*' -not -path './build/*'
```
Look for: `README`, `docs/`, `CONTRIBUTING`, `tests/` / `test/` / `unittests/`, `examples/`, top-level `CMakeLists.txt`, `src/` vs `include/`.

## 3 · Build with debug info **[talk: "a KEY that will make your life easier"]**

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug -DCMAKE_EXPORT_COMPILE_COMMANDS=ON   # ✅ tested
cmake --build build -j                                                              # ✅ tested
```
Details, 3rd-party libs, gotchas: ch.05. *Can't build it?* That's today's real task — the talk says
bluntly that building isn't trivial ("days to get it compiled"). Ask for the setup doc; if none exists, **write it** as you go (great first contribution).

## 4 · Run it — before reading code **[talk: Step 1]**
Use the app like a user. Note: inputs, outputs, logs, what the UI/CLI exposes, how long it runs.
Add it to the journal: *"app does A, B, C; config comes from X."*

## 5 · Find the entry point **[talk]**

The talk anchors on `main()`: "From main you'll often get hints of the overall architecture — plugins
loaded? event loop?" and "what happens **before** main (init) and **after** (cleanup)".

```bash
# ✅ tested (quote globs in zsh!)
grep -irn -I --include='*.cpp' "main()" .        # talk's exact form: -i case-insens, -r recursive, -n line no., -I skip binaries
rg -n --type cpp '\bmain\s*\(' .                 # ripgrep: faster, respects .gitignore
rg -n 'int main|WinMain|wmain|DllMain|JNI_OnLoad' src/   # per-platform entry points
```
Reading results [talk]: OpenTTD had ~33–37 hits for "main" — shaders, third-party (Catch test
framework), per-OS mains (`unix.cpp`, Windows…), plus the real `openttd_main`. Filter by
file type and parentheses placement; expect multiple entries (one per OS, test runner, tools).
Good sign: `main` is tiny and delegates to a "real main".

Other entry-point types to look for [added]: event handlers, plugin `register` functions, static
initializers (code runs *before* main), signal handlers, thread start routines, message-bus `subscribe` calls.

### Same task, with a debugger — lands you exactly at the entry **[talk]**
```bash
gdb ./build/app            # 📖  then:
(gdb) tui enable           #   source window (what the speaker loves)
(gdb) start                #   temp breakpoint on main + run
(gdb) next  / step         #   n / s   (Enter repeats the last command)
(gdb) bt                   #   where am I
```
LLDB equivalent: `lldb ./build/app` → `breakpoint set -n main` → `run` → `n` / `s` / `bt`.

## 6 · Look for tests early **[notes]**
Your own note: *"look for a tests folder… is there already a test for this component?"*
```bash
ctest --test-dir build -N                     # list tests, run none (CMake ≥ 3.20)  ✅ cmake present
ctest --test-dir build -R <component> -V      # run matching tests verbosely
rg -l 'TEST(_F|_CASE)?\(|TEST_CASE\(' tests/  # gtest / Catch2 style
```
A passing test for your component = a ready-made, tiny entry into the debugger (ch.11).

## 7 · History in your area
```bash
git log --oneline -20 -- path/to/component      # ✅ tested
git shortlog -sn HEAD -- path/to/component      # who knows this code (⚠ needs HEAD or it waits on stdin!) ✅
```

## 8 · Journal entry #1 (template in ch.13)
Record: size, entry points, build recipe, test locations, 3 open questions.
