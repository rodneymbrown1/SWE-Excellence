# Evidence and sources {.appendix}

<p class="lede">What each claim in the book rests on, how strong it is, and what could not be verified. The full notes, with quotes, are in <code>resource/research/</code>.</p>

## How to read the strength column

* **Primary**: I read the source's own text.
* **Secondary**: I read a reputable page that quotes or summarizes it. [SEC]{.sec}
* **Manual**: tool behavior from the official manual, not executed. [MANUAL]{.manual}
* **Ran**: executed here. [RAN]{.ran}

## Empirical studies

| Claim in the book | Source | Strength | Caveat |
|---|---|---|---|
| Developers did not use the debugger in 91% of IDE sessions; advanced features under-used | Beller, Spruit, Spinellis, Zaidman, "On the Dichotomy of Debugging Behavior Among Programmers", ICSE 2018 | Primary | Java, Eclipse and IntelliJ. 176 survey respondents, 458 instrumented developers |
| "once one knows the condition, one almost automatically understands the problem" | Same paper, expert interview | Primary | Two interviewees; a quote, not a measurement |
| Correct early hypothesis predicts success; offered hypotheses helped, offered locations did not | Alaboudi and LaToza, "Using Hypotheses as a Debugging Aid", VL/HCC 2020 | Primary (abstract read; arXiv) | 20 developers; lab tasks |
| About 58% of time on program comprehension | Xia et al., "Measuring Program Comprehension…", IEEE TSE 2018 | Secondary (publisher abstract) | 78 developers, 3,148 hours, 7 projects; an average |
| Methodical, structured investigation is most effective | Robillard, Coelho, Murphy, IEEE TSE 2004 | Primary (abstract read) | 5 developers, one system |
| Why-did / why-didn't questions; Whyline cut debugging time "nearly a factor of 8" | Ko and Myers, "Designing the Whyline", CHI 2004 | Primary | Alice teaching environment; six scenarios; an upper bound |
| Systematic readers did better on small programs; experts on large ones read as-needed | Littman et al. 1986; Koenemann and Robertson 1991, as described in a 2023 survey (arXiv 2310.11301) | Secondary | Original papers not read |

## Authorities and books

| Claim in the book | Source | Strength |
|---|---|---|
| A programmer's theory: explain, justify, respond to change; decay without it | Naur, "Programming as Theory Building", 1985 | Primary (mirror text) |
| Scientific method for debugging; defect → infection → failure | Zeller, *Why Programs Fail*, ch. 6 | Primary (excerpt) |
| TRAFFIC: Track, Reproduce, Automate, Find origins, Focus, Isolate, Correct | Zeller | Secondary [SEC]{.sec} |
| Nine rules; "quit thinking and look"; keep an audit trail | Agans, *Debugging* (2002) | Secondary (a review quoting the book) [SEC]{.sec} |
| Four phases; unknown, data, condition | Pólya, *How to Solve It* | Secondary (Wikipedia; course page) [SEC]{.sec} |
| "Data dominates"; measure first | Pike, "Notes on Programming in C", 1989 | Primary |
| Show the tables / data structures first | Brooks (*Mythical Man-Month* ch. 9); Torvalds (git list, 2006, via LWN) | Secondary; Brooks paraphrased, wording varies by edition |
| Behaviors as sequences of states; specs above the code | Lamport (TLA+; "Thinking for Programmers") | Secondary (abstract and interview coverage) [SEC]{.sec} |
| `{P} C {Q}`; class invariants; Design by Contract | Hoare; Meyer | Secondary (lecture notes) [SEC]{.sec} |
| Characterization tests; seams | Feathers, *Working Effectively with Legacy Code* | Secondary [SEC]{.sec} |
| Hypothetico-deductive troubleshooting; bisection; "what touched it last" | Google, *Site Reliability Engineering*, ch. 12 | Primary |
| Follow the data; run it first; conditional watchpoints | Shah and Croft-White, C++ on Sea 2025 | Primary (your transcript) |

## Tools

| Claim in the book | Source | Strength |
|---|---|---|
| Break conditions, ignore counts, command lists, `dprintf`, watchpoint rules, convenience functions, Python breakpoints, reverse execution, startup and batch options | GDB manual (sourceware.org, current docs) | Manual [MANUAL]{.manual} |
| Cortex-M hardware watchpoints; late halt; same-value writes suppressed | Memfault Interrupt, "Faster Debugging with Watchpoints" | Primary (first ~39k characters) |
| gdb-dashboard | github.com/cyrus-and/gdb-dashboard README | Primary |
| rr record, replay, reverse commands, limits | rr-project.org and its wiki | Primary |
| VS Code launch.json, Remote-SSH, breakpoint types, `-exec` | VS Code documentation | Primary |
| lldb behavior | lldb-1700.0.9.502, this Mac | Ran [RAN]{.ran} |

## What I could not verify, and what I did about it

| Item | What happened | Handling |
|---|---|---|
| Whether any gdb command *runs* | No gdb on the machine used | Manual-checked; smoke test (Appendix C) |
| `$_caller_matches` anchoring | The manual does not say | Pattern written to work either way |
| Local `./.gdbinit` auto-loading | Not confirmed for local files | The book teaches `-x` |
| VS Code data-breakpoint support for gdb | Docs do not say which debuggers | Book says to test it |
| Your VS Code symptom | I cannot see your setup | Ranked hypotheses (Appendix A) |
| Brooks and Kernighan exact wording; Beck's "make the change easy" | Wording varies or the origin is unconfirmed | Paraphrased or not used |
| Victor's "Inventing on Principle" | Video not readable | Secondary only; innovation claim marked an argument |
| Time budgets (chapter 20) | Not from research | Marked as a proposal |
| Gillian Minnehan's talk | Behind a login; I read only the session page | Your notes are the source for its contents |

## Credits

The thesis is yours: that the tool works only as well as the developer understands the problem. The sources above supply the evidence. The practice program, probes, and transcripts are in `lab/`.
