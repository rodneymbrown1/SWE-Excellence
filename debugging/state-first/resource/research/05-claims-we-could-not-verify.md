# 05 · What we could not verify (and how the book handles it)

Honesty ledger. If you check one file in this folder, check this one.

| Item | Problem | How the book handles it |
|---|---|---|
| **gdb was never executed** | This Mac has only lldb; Docker was not used. | gdb commands are checked against the official manual (`03-gdb-mechanics.md`) and labeled **[MANUAL]**. lldb versions are **[RAN]**. `lab/gdb/smoke-test.sh` lets you verify every gdb script on your Linux box in about two minutes. |
| `$_caller_matches` regex anchoring | Manual doesn't say whether the match is anchored. | Book uses patterns like `".*flush_burst"` and tells you to confirm on first use. |
| Local `./.gdbinit` auto-load | Manual text read covers safe-path generally; exact local-file behaviour unconfirmed. | Book teaches explicit `gdb -x script` (always works). |
| VS Code data breakpoints with `cppdbg`+gdb | Docs say availability depends on the debugger; no list. | Book tells you to use the Debug Console `-exec watch …` or the gdb terminal for watchpoints and says "try it, then note whether the UI offers it". |
| Why your Remote-SSH debug session "ran in the terminal with no UI" | We can't see your setup. | Appendix A gives a **ranked checklist of hypotheses** to test, not a diagnosis. |
| Zeller's TRAFFIC definitions | Primary slides unreachable; seven step names confirmed by several secondary pages. | Book uses the seven names and our own one-line meaning; flagged as secondary. |
| Agans's book | Not read directly; rules and three quotes taken from a detailed review that quotes the book. | Cited as secondary. |
| Brooks "show me your tables" wording | Differs by edition; no primary scan. | Paraphrased, no direct quote. |
| Torvalds quote | Wording stable across sources; original list post not retrieved (LWN reprint dated 3 Aug 2006 confirmed). | Short quote attributed to LWN's reprint. |
| Kent Beck "make the change easy" | 2012-tweet origin not confirmed (he has used it in later writing). | **Not used.** |
| Kernighan "debugging is twice as hard…" | Exact wording and edition (1974 vs 1978) vary between sources. | Paraphrased with "attributed to". Beller et al. also cite it as a general point. |
| Lamport "Thinking Above the Code" content | Talk abstract and interview coverage only; his book PDF unreadable to our fetcher. | Used only for the idea that a spec above the code helps and that behaviours are sequences of states (from TLA+ secondary notes). |
| Victor "Inventing on Principle" | Video 403; only secondary write-ups. | Paraphrase only, labeled secondary; the innovation claim is labelled an argument, not a finding. |
| Littman 1986 original | Read a 2023 survey's description, not the paper. | Attributed "as described by …". |
| Minelli 2015 (70%) | Seen only inside a search summary of Xia et al. | Mentioned as "an earlier estimate near 70%" with Sn status; headline number is Xia's 58%. |
| Robillard "half the time" claim | Appeared only in a secondary report. | **Not used.** |
| Time budgets in chapter 18 | Not from research. | Labeled "starting defaults — our proposal"; calibrate with journal. |
| Whyline "8×" | Alice-based prototype, six scenarios, small user tests. | Reported with that context; called an upper bound. |
| Cortex-M comparator count | Chip-specific. | Book says "typically a small number (4 on the nRF52840 example)" and tells you to read `DWT_CTRL.NUMCOMP`. |
