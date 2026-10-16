# 11 · Shrink the Problem — tests, examples, and "first tasks"

> **[talk]** *"If you've got a complex task, break it down into smaller steps. It's impossible to
> tackle these big things as a whole."* Your task (implement something on a huge class) is not
> "understand the codebase" — it's "understand **this path through** the codebase". Everything here
> is a way to make the thing you must understand smaller.

## 1 · Is there already a test for my component? — look FIRST **[your notes + talk slide 62]**

Your own note: *"look for a tests folder… is there already a test for this component?"* A passing test is a free, tiny,
deterministic program that exercises exactly your component — the perfect thing to run under the debugger.

```bash
# find tests (✅ tested patterns)
find . -type d \( -name test -o -name tests -o -name unittests -o -name testing \) -not -path './build/*'
rg -l 'TEST(_F|_P)?\(|TEST_CASE\(|BOOST_AUTO_TEST_CASE|SCENARIO\(' --glob '!build*' .   # always give rg a path
rg -n 'add_test|gtest_discover_tests|catch_discover_tests|enable_testing' --glob 'CMakeLists.txt' .
rg -n -i 'tracker' tests/                    # tests mentioning MY component (swap in your class name)

# list and run via CTest (✅ tested on practice-sandbox)
ctest --test-dir build -N                    # list tests, run nothing
ctest --test-dir build -R tracker -V         # run matching names, verbose
ctest --test-dir build --output-on-failure   # show output only for failures
ctest --test-dir build -j4                   # parallel
ctest --test-dir build --rerun-failed --output-on-failure

# run one test case directly (framework flags) 📖
./build/tests/unit_tests --gtest_list_tests
./build/tests/unit_tests --gtest_filter='TrackerTest.*'
./build/tests/unit_tests --gtest_filter='TrackerTest.ResetClearsTotal' --gtest_repeat=100   # flaky? repeat it
./build/tests/unit_tests --list-tests                 # Catch2
./build/tests/unit_tests "[tracker]"                  # Catch2 by tag

# debug a single test case
gdb --args ./build/tests/unit_tests --gtest_filter='TrackerTest.ResetClearsTotal'   # 📖
lldb -- ./build/tests/unit_tests --gtest_filter='TrackerTest.ResetClearsTotal'
```
**No test for your component?** The talk: *"if you don't have tests, maybe that's a great first thing to do as a task to start learning the codebase."*
Write one that reproduces the bug (it fails) → that's both your repro and your regression test (ch.02 steps 1 and 7).

### Characterization tests — safe way to touch scary code **[added]**
Before changing legacy code you don't understand, write tests that capture what it **currently does** (even if "wrong"), then change it knowing
what you broke. This is Michael Feathers' technique from *Working Effectively with Legacy Code*.

## 2 · Run examples & samples **[talk, slide 62]**
Frameworks ship tutorials/samples (a graphics library has them). Run the smallest one, put a breakpoint in the part you care about, use `bt`.
```bash
ls examples samples demo tools 2>/dev/null ; rg -l 'int main' examples samples 2>/dev/null
```

## 3 · Pick a good first task — and make it small **[talk, slides 67–72]**

The talk's list of "byte-sized" first tasks:
- A **labeled** "good first issue / minor / small" item in the tracker (managers: create those labels!).
- **Fix a compiler warning** (`-Wall -Wextra` output) — "not glorious, but gives you practice."
- **Change some text / a config value** — teaches how config is loaded.
- **Add an item to a list box / widget** — teaches whether data is hard-coded, from config, or downloaded.
- **Exercise:** "use a debugger to track what function is called when you click on something." (ch.03 + ch.09)
- Answer a tiny question about behavior: *"What does a train do when it arrives at a station?"* → record it (ch.08), read the stack.

Find them yourself:
```bash
rg -n -i 'TODO|FIXME|XXX|HACK|later|workaround|magic|hard-?coded' --type cpp src/   # ✅ tested pattern
rg -n '\?\?\?' src/                                  # question marks / confusion markers
git log --since=3.months --oneline -- path/ | head -30   # what's actively changing = where reviewers' attention is
git log --grep='fix' --oneline -- path/ | head
```
The talk's examples of what you'll find: *"This is hard-coded and should be fixed later"* · *"FIXME, this is a magic constant that should be loaded from a config file"* ·
*"Perhaps we should do this for all the name generators"*. Reading the commit that last touched a TODO tells you who to ask and why it exists (ch.04).

## 4 · The "thin slice" method for your own feature **[added]**
When asked to "implement X in class C":
1. **Find the smallest existing thing that behaves like X** (a sibling feature). Copy its path end to end.
2. Trace *that* sibling with the debugger once (ch.03 → ch.06): entry → class → message → output. Write the 6-line path in the journal.
3. Make the **smallest possible change** that makes your test (ch.11 §1) go from red to green. Commit.
4. Only then widen.
5. Review your own diff before anyone else does: `git diff --stat; git diff` — does every changed line trace to the requirement?

## 5 · Reduce, don't read — minimizing a repro **[added]**
```bash
# delta-debug by hand: halve the input / config / commit range until nothing can be removed
git bisect start BAD GOOD && git bisect run ./check.sh      # history axis
head -n 500 input.log > half.log && ./app half.log           # input axis: halve until it stops failing, then back off
```
Goal: a repro the size of the practice sandbox — ~60 lines, one class, one queue. Smaller repros are debuggable AND shareable (ch.02 ask-for-help template).

## Links
- CTest — <https://cmake.org/cmake/help/latest/manual/ctest.1.html> · `enable_testing` / `add_test` — <https://cmake.org/cmake/help/latest/command/add_test.html>
- GoogleTest — <https://google.github.io/googletest/> (advanced: `--gtest_filter`) · Catch2 — <https://github.com/catchorg/Catch2>
- Michael Feathers, *Working Effectively with Legacy Code* (characterization tests)
- OpenTTD's issue labels used in the talk — <https://github.com/OpenTTD/OpenTTD/issues> · project dev page — <https://www.openttd.org/development>
