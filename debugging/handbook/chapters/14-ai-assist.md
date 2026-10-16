# 14 · AI Assistance — "trust, but verify"

> **[talk, bonus round]** *"Does AI solve this problem? … Yes, it really can help — but it's still a pattern-matching
> tool. If it sees something it thinks it understands, it will be very convinced … It sounds authoritative. It's not.
> It's just good at being convincing. So do double check."* → **Trust but verify.**

## What the talk says AI is good and bad at

| Good at | Bad at |
|---|---|
| Summarizing what a file/function does | Knowing it's wrong — "hyperconfident" **[talk]** |
| Searching a codebase far faster than you | Staying on track — "AIs get distracted if something looks like something they've seen before" |
| Explaining unfamiliar code / basic tasks | Challenging you or defending claims with evidence — "rarely challenge you or defend positions with evidence" |
| Driving tools (prototype: UDB + Claude Code: "tell me why this happened") | Real root cause in a 3M-line codebase on its own |

**The MySQL story [talk, slides 77–78]:** the speaker's first attempt — the AI (Claude and ChatGPT) ran off after any plausible root cause "with intense
conviction", proposed "the definitive patch", and was completely wrong. What worked: **time-travel debugging "constrained the AI by making it confirm
with evidence every hypothesis."** The bug had been open ~16 months; when he posted his findings, the maintainers replied it was already fixed by another change that nobody had linked to it. Article: <https://undo.io/resources/time-travel-debugging-tames-complex-codebases-and-overconfident-ai/>

## ⚠️ First: is it allowed? **[talk + added — critical for Raytheon]**
The talk: use **enterprise** AI tools; the AI must be *licensed to your organization* and *your organization must approve you sharing code and insights.*
For a defense contractor add: code, designs, and data may be **export-controlled (ITAR/EAR) or CUI**. Pasting any of it into a consumer chatbot can be a
reportable security incident. **Rule: no code, logs, error text containing program details, hostnames, or screenshots go into any AI tool unless your
security/program office has approved that exact tool for that data.** If unsure, ask — and practise on this handbook's sandbox or open-source repos instead (the talk's advice: learn on OpenTTD/SQLite/MySQL).

## The workflow: AI proposes → debugger judges

```
AI says: "the bug is in X because Y"
        │
        ▼
Turn the claim into a FALSIFIABLE test — one watchpoint / breakpoint / dprintf / unit test
        │
        ▼
Run it.  Evidence agrees?  ──yes──►  Keep it, write it in the journal (ch.13)
        │no
        ▼
Tell the AI the evidence ("the watchpoint never fired in X; the write came from frame Z — here's the bt") and ask for a NEW hypothesis
```
Examples of turning claims into experiments:
| AI claim | Experiment |
|---|---|
| "`m_total` goes negative in `applyDelta`" | `watch -l tracker.m_total if … < 0` — does it stop there? with what `v`? (ch.07) |
| "This function is called once per frame" | `break Foo::tick` + `ignore 1 999` + `info breakpoints` for the hit count; or `perf` call counts (ch.09) |
| "The pointer is freed before use" | ASan (ch.12) — does it report use-after-free, with what stacks? |
| "This commit introduced it" | `git bisect run` (ch.04) |
| "These two classes aren't coupled" | `rg` + clangd *incoming calls* + Doxygen caller graph (ch.10) |

## Prompts that work (use on **approved** tools, with **non-sensitive** or open-source code)

```text
# Orient (read-only):
"Explain the control flow from main() to <feature>. List files/classes in order. For each claim cite file:line.
 Mark anything you inferred rather than read as INFERRED."

# Make it show evidence:
"For your hypothesis, give me ONE gdb/lldb command sequence that would prove it wrong. Don't propose a fix yet."

# Constrain it:
"Here is the backtrace and the watchpoint output. Which hypotheses from your last answer does this falsify? What's left?"

# Review my reasoning:
"Here is my hypothesis and my evidence. What's the strongest alternative explanation I haven't excluded?"

# Learn, not just solve:
"Explain what <class>'s observer/subscribe pattern is doing here and what to grep for to find every publisher."
```
Anti-prompts: *"fix this"* with no repro; pasting a stack trace and accepting the first explanation; letting it edit code before you can reproduce the failure.

## Tools the talk named (to watch, not to rely on) **[talk]**
- **Sourcegraph** (code search/summarize) — <https://sourcegraph.com/>
- **ChatDBG** (open-source: an LLM inside GDB/LLDB/pdb) — <https://github.com/plasma-umass/ChatDBG>
- **Claude Code** (terminal coding agent) — and Undo's **UDB + Claude Code** prototype (lightning talk; "releasing to customers later this year")
Treat all of them as *hypothesis generators*, never as judges.

## Links
- Undo article (MySQL + overconfident AI) — <https://undo.io/resources/time-travel-debugging-tames-complex-codebases-and-overconfident-ai/>
- ChatDBG — <https://github.com/plasma-umass/ChatDBG> · Sourcegraph — <https://sourcegraph.com/>
- Debugging heuristics beyond tools (book): David J. Agans, *Debugging: The 9 Indispensable Rules* — "Make it fail", "Quit thinking and look", "Change one thing at a time", "Keep an audit trail", "If you didn't fix it, it ain't fixed" — i.e. ch.02's loop. **[added]**
