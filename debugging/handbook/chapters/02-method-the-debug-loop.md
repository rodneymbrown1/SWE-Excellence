# 02 · The Debug Loop — a process, not a tool

> Your `context.txt` diagnosis was exactly right: *"it was not my understanding of C++ … it was my
> process for understanding large and unfamiliar codebases."* This chapter is that process.

## What makes a codebase hard (and which tool attacks which) **[talk]**

| Difficulty named in the talk | What it feels like | Attack with |
|---|---|---|
| Control flow unclear (entry points, threads, hot spots) | "What even runs?" | run it, `main`, debugger, profiler (ch.03, 06, 09) |
| Data flow / state changes unclear | "Who touches this variable?" | watchpoints, reverse debugging (ch.07, 08) |
| Pure scale (can't hold it in your head: 1M lines ≈ 18,000 pages ≈ 14× *War and Peace*) | Drowning | shrink the problem (ch.11) |
| Mixed variants (legacy + modern C++, different patterns) | Inconsistent code | doxygen, formatter, patterns (ch.10) |
| Human factors (Conway's law, no docs, only-the-senior-knows) | Fear of touching things | journal, ask well, shadow someone (ch.13) |

**Key reframe [talk]:** you do *not* need to understand the whole codebase. Mike's line: "most of
us don't get the luxury of four years to understand the codebase before we're given our first
bug." Follow the **data or flow for your task** and ignore the rest.

## The loop

```
┌─► 1 REPRODUCE ──► 2 LOCALIZE ──► 3 OBSERVE ──► 4 HYPOTHESIZE ──► 5 TEST ──┐
│                                                                            │
└──────────────── (hypothesis wrong? write it down, go back to 2/3) ◄────────┘
                                          (hypothesis survives) ──► 6 FIX ──► 7 PROVE ──► 8 RECORD
```

### 1 Reproduce **[talk: "Step 1: run your program"]**
- Build it with the project's build system, run it, *see* the behavior. "Sounds silly… but a high-level
  understanding of what your program actually does is key."
- Make the failure **deterministic and small**: fixed input, fixed seed, one thread if possible.
- Can't reproduce? Then the task is "make it reproduce" — loop it:
  ```bash
  n=0; while ./build/app --case 42 >/dev/null 2>&1; do n=$((n+1)); done; echo "failed after $n runs"   # [added]
  ```

### 2 Localize — **bisect everything** [added]
Pick the cheapest axis that halves the search space:

| Axis | Question | Tool |
|---|---|---|
| **Time (history)** | Which commit broke it? | `git bisect run` (ch.04) |
| **Space (code)** | Which module/class? | breakpoint + `bt`, `perf`, grep visible strings |
| **Data (pipeline)** | At which stage does the value go bad? | conditional break / `dprintf` at stage boundaries |
| **Execution (moment)** | When in the run does it first go wrong? | watchpoint, reverse debugging |
| **Config / build** | Debug vs release? flag? lib version? | rebuild with different settings |

### 3 Observe — look, don't guess
Use the tool that gives *facts*: debugger state, a sampling profile, a sanitizer report. Reading the
same function over and over (your "endless cycle" in `context.txt`) is the anti-pattern — **stop
reading, start measuring.**

### 4 Hypothesize — one falsifiable sentence
Good: *"`Tracker::m_total` becomes negative inside `applyDelta` because `Controller::rebalance` posts
a delta computed from a stale `believedTotal_`."*
Bad: *"something's wrong with the messaging."*

### 5 Test — cheapest experiment that could prove you wrong
A watchpoint, a conditional breakpoint, one `dprintf`, one unit test. **Change one thing at a time.**

### 6 Fix at the root
**Crash site ≠ bug site** [added]. Ask "why?" until the answer is a decision someone made
(5 Whys): assert fired → total negative → delta negative → stale belief → no resync after Reset.
Fix the resync, not the assert.

### 7 Prove it
- Add/adjust a test that fails before, passes after.
- **Revert your fix once and confirm the bug comes back** — proves you fixed *this* bug.
- Run the surrounding tests (`ctest`) [added].

### 8 Record
Write the journal entry (template in ch.13). **[talk]** "Keep a coding journal… a greppable text file
or Google Doc… Carmack's `.plan` files."

## Time-boxing & asking for help **[talk + added]**

- **[added] Heuristic:** if 25–30 minutes pass with no falsified hypothesis, you are not making
  progress — switch angle (data ↔ control flow ↔ history), shrink the repro, or ask. (The number is
  a suggestion, not from the talk; tune it.)
- **[talk]** Asking is expected: "bring something to the table — what you tried, where you're looking,
  what problem you're trying to solve."
- **[talk]** Best junior tip: ask a senior *"can I shadow you for 15 minutes?"* — you learn their
  tools, not just their answers.
- **[talk]** Ask "which tools are already in use here?" before installing your own.

### Ask-for-help template (paste into chat/email)
```
Goal:        <one line>
Repro:       <exact command, input, commit>
Expected vs actual: <…>
What I tried (and learned):  1) … 2) …
Current hypothesis:          <falsifiable sentence>
Where I'm stuck / the question: <one concrete question>
Evidence:    <bt, log excerpt, journal link>
```

## Anti-patterns to catch yourself in
- Re-reading code instead of running it.
- "Fixing" by adding a null check at the crash site.
- Changing 3 things between runs.
- Trusting a confident explanation (human or AI) without evidence (ch.14).
- Debugging a build you don't ship (debug-only) when the bug is in the optimized build (ch.05).
- Not writing anything down, then re-deriving it tomorrow.
