# 04 · Search & Navigate — "Where is it? Who touches it? When did it change?"

> The talk uses `grep` to find `main` and warns it can become **"a treasure hunt if we do not know
> what we're looking for"** **[talk]**. The fix is not a cleverer grep — it's choosing *what* to
> search for, and switching to the debugger when text search stops paying off.

## The three questions and their tools

| Question | Tool | Chapter |
|---|---|---|
| **Where** is the code? (text) | `rg` / `grep` | here |
| **Who** calls / writes / reads it? (semantic) | clangd (find references, call hierarchy), `ctags` | here |
| **When** did it change, and **why**? (history) | `git log -S`, `git blame`, `git bisect` | here |
| **What actually ran?** (runtime truth) | debugger / profiler | 06, 07, 09 |

Text search finds *spelling*. It cannot tell a read from a write, or `m_total` in `Tracker` from
`m_total` in some other class. Once grep returns >20 hits, stop reading them — go to chapter 07.

## 1 · Search with ripgrep (talk used `grep`; `rg` is the same idea, faster)

The talk's exact form **[talk]** — ✅ tested:

```bash
grep -irn -I --include='*.cpp' "main()" .
#     │││ │   └ only .cpp files          (quote the glob in zsh!)
#     │││ └ -I  skip binary files
#     ││└ -n  line numbers
#     │└ -r  recursive
#     └ -i  case-insensitive
```

Same thing, nicer defaults (respects `.gitignore`, skips binaries, colors, line numbers) **[added]**:

```bash
rg -n --type cpp '\bmain\s*\(' .             # ✅ tested   whole-word-ish main(
rg -n -w m_total src/                         # ✅ tested   -w = whole word (won't match m_total2)
rg -n -C3 'applyDelta' src/                   # ✅ tested   3 lines of context around each hit
rg -l  'Bus::post'  src/                      # ✅ tested   file names only
rg -c  'm_total'    src/                      # ✅ tested   count per file
rg -n  'TODO|FIXME|HACK|XXX' src/             # ✅ tested   developer breadcrumbs [talk]
rg -n  -g '!build/*' -g '!third_party/*' 'foo'  #           exclude dirs
rg --files . | rg -i 'cmake'                  # ✅ tested   find files by name
rg -n --type-list | head                      #           what --type names exist
```

### Classify hits instead of reading them — writers vs readers **[added]**

For "100 instances of one variable" the useful split is **who writes it**:

```bash
# assignments / compound assignments / ++ -- (the WRITERS)               ✅ tested
rg -n 'm_total\s*([-+*/%|&^]|<<|>>)?=[^=]' src/
rg -n '(\+\+|--)\s*m_total|m_total\s*(\+\+|--)' src/
# everything else is a reader, a declaration, or a comment
rg -n -w m_total src/ | rg -v 'm_total\s*([-+*/]?=[^=])'
# who passes it by pointer/reference (could write through it)?
rg -n '&\s*m_total|\*\s*m_total' src/
```
Note: it also matches the *declaration* with a default initializer (`int m_total = 0;`) — ignore that hit.
Caveat: this finds *textual* writers only. Writes through a pointer, a memcpy, a setter, or a
message handler won't match → that is exactly why chapter 07 uses a **watchpoint** instead.

### Search for the *visible* thing first **[added]**
Users see strings, not identifiers. Grep what you can see: the exact error message, a log line,
a UI label, a CLI flag, a config key, a JSON field, an enum name.
```bash
rg -n -F 'Connection refused' src/        # -F = literal, no regex surprises
rg -n -F -- '--max-retries' src/ docs/
```
Then walk **outward** from that string to callers (clangd references or `bt` in the debugger).

> ⚠️ **`rg` with no path hangs in scripts/pipelines (found while testing).** When stdin is not a terminal, ripgrep waits to
> read from it. Always end the command with a path: `rg 'x' .` or `rg 'x' src/`. (Same for `rg --files .`.)

## 2 · Semantic navigation: clangd / ctags (find *references*, not text) **[added]**

`clangd` needs to know the real compile flags → export them from CMake:
```bash
cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON       # ✅ writes build/compile_commands.json
ln -sf build/compile_commands.json .                          # clangd looks in the project root / build/
```
In editors with LSP (VS Code, Neovim, CLion has its own): *Go to definition*, *Find all references*,
*Call hierarchy (incoming)*. "Incoming calls" is "who calls me?" without reading anything.
No LSP? `ctags` is crude but universal:
```bash
ctags -R --c++-kinds=+p --fields=+iaS --extras=+q src/   # needs universal-ctags
# vim: Ctrl-]  jump to definition      Ctrl-t  jump back      :tselect NAME  pick among matches
```

## 3 · History: `git` archaeology **[added]** — ✅ all tested in a scratch repo

```bash
git log --oneline -20 -- path/to/component          # recent history of just your area
git log -S'applyDelta' --oneline                    # "pickaxe": commits where the COUNT of that string changed
git log -G'm_total\s*\+=' --oneline -p              # commits whose diff matches a regex
git log -L :applyDelta:src/tracker.cpp              # full history of ONE function
git blame -L 10,30 src/tracker.cpp                  # who last touched each line
git blame -w -C -C src/tracker.cpp                  # ignore whitespace, follow code moved between files
git show <sha>                                      # then read the commit MESSAGE — it holds the "why"
git grep -n 'm_total' $(git rev-list -n1 HEAD~50)   # search the code as it was 50 commits ago
git shortlog -sn HEAD -- path/                      # who knows this area (give it HEAD or it waits on stdin)
```
The slides leave "show how to query small `git diff` messages" as a TODO **[talk]** — the commands
above are that exercise. The *commit message* is the closest thing to documentation of "why".

### Regression? Let git find the commit — `git bisect run`

```bash
cat > /tmp/check.sh <<'EOF'
#!/bin/sh
cmake --build build -j >/dev/null 2>&1 || exit 125   # 125 = "can't test this commit, skip it"
./build/sandbox                                       # exit 0 = good, 1-127 = bad
EOF
chmod +x /tmp/check.sh        # keep the script OUTSIDE the repo so checkouts don't remove it
git bisect start BAD_SHA GOOD_SHA        # e.g.  git bisect start HEAD v1.4
git bisect run /tmp/check.sh             # ✅ tested: prints "<sha> is the first bad commit"
git bisect reset                         # ALWAYS finish with this (returns you to your branch)
```
~100 commits ≈ 7 test runs (log₂). Works even if you can only say "this test fails now".
Docs: <https://git-scm.com/docs/git-bisect>

## 4 · When to stop searching and run the program

| Search result | Do this instead |
|---|---|
| >20 hits for the same name | Watchpoint on the live object (ch.07) |
| Many `main`s / entry points | `start` in the debugger lands on the real one (ch.03) |
| Virtual / callback / `std::function` dispatch | Break in the callee, read `bt` — grep can't see dynamic dispatch |
| Message passed through a bus/queue | Break at the **sender**, not the receiver (ch.07) |
| Macro-generated code | Preprocess it: `clang++ -E file.cpp \| less`, or step into it with the debugger |

## Links
- ripgrep user guide — <https://github.com/BurntSushi/ripgrep/blob/master/GUIDE.md>
- GNU grep manual — <https://www.gnu.org/software/grep/manual/grep.html>
- git-log (`-S`, `-G`, `-L`) — <https://git-scm.com/docs/git-log> · git-blame — <https://git-scm.com/docs/git-blame>
- clangd — <https://clangd.llvm.org/> · `compile_commands.json` — <https://cmake.org/cmake/help/latest/variable/CMAKE_EXPORT_COMPILE_COMMANDS.html>
- The Missing Semester (MIT; cited in the talk's slides) — <https://missing.csail.mit.edu/>
