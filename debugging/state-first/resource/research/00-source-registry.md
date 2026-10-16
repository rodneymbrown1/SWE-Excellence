# Source registry

Status key: **P** = read the source's own text · **S** = read a reputable secondary page that quotes/summarizes it ·
**Sn** = only a search-result summary (not opened) · **U** = unverified.
Tier: **A** peer-reviewed / official manual / primary author · **B** reputable practitioner or course material · **C** blog/aggregator.

## People, method and cognition

| ID | Source | Tier | Status | URL / where |
|---|---|---|---|---|
| S01 | Naur, P. (1985) "Programming as Theory Building", *Microprocessing and Microprogramming* 15(5) | A | P (mirror) | https://neonvagabond.xyz/mirrors/naur1985programming.html |
| S02 | Zeller, A. *Why Programs Fail* (2nd ed., 2009), ch. 6 "Scientific Debugging" | A | P (course reading excerpt) | https://courses.cs.duke.edu/compsci308/spring26/readings/Zeller_Scientific_Debugging.pdf (local: `_raw/zeller-scientific-debugging-duke.*`) |
| S02b | Zeller — TRAFFIC mnemonic (Track, Reproduce, Automate, Find origins, Focus, Isolate, Correct) | B | S/Sn (several secondary pages name all seven; primary slides not retrievable) | https://symflower.com/en/company/blog/2023/debugging-with-the-traffic-principle/ ; https://www.embedded.com/?p=4415917 |
| S03 | Agans, D. (2002) *Debugging: The 9 Indispensable Rules* | A (book) | S (review quoting the book) | https://embeddedartistry.com/blog/2017/9/6/debugging-9-indispensable-rules (local copy `_raw/agans-embeddedartistry.html`) |
| S04 | Pólya, G. (1945) *How to Solve It* | A (book) | S | https://en.wikipedia.org/wiki/How_to_Solve_It ; https://www.ms.uky.edu/~carl/ma310/spring03/polya/Polya.htm |
| S05 | Pike, R. (1989) "Notes on Programming in C" — rules 1, 2, 5 | A | P | https://www.lysator.liu.se/c/pikestyle.html |
| S06 | Brooks, F. *The Mythical Man-Month*, ch. 9 — flowcharts vs tables | A (book) | Sn (wording varies by edition; used as paraphrase only) | https://en.wikiquote.org/wiki/Fred_Brooks |
| S07 | Torvalds, L. (2006) git list — "worry about data structures" | B | S (LWN "Quote of the week", 3 Aug 2006) | https://lwn.net/Articles/193244/ |
| S08 | Lamport, L. — "Thinking for Programmers: Rising Above the Code" (talk); TLA+ behavior = sequence of states | A | Sn (abstract + secondary) | https://www.microsoft.com/en-us/research/video/thinking-for-programmers/ ; https://www.infoq.com/news/2014/10/ser-lamport-interview |
| S09 | Hoare (1969) triple {P}C{Q}; Meyer — Design by Contract | A | S (lecture notes; no primary text read) | https://scg.unibe.ch/download/lectures/p2/P2-03-DesignByContract.pdf |
| S10 | Feathers, M. (2004) *Working Effectively with Legacy Code* — characterization tests, seams | A (book) | S | https://understandlegacycode.com/blog/key-points-of-working-effectively-with-legacy-code/ |
| S11 | Beyer et al. *Site Reliability Engineering* (Google), ch. 12 "Effective Troubleshooting" | A | P | https://sre.google/sre-book/effective-troubleshooting/ |
| S12 | Ko & Myers (2004) "Designing the Whyline", CHI '04 | A | P (local PDF text) | https://hci.rwth-aachen.de/materials/conferences/CHI2004/1p151.pdf |
| S13 | Alaboudi & LaToza (2020) "Using Hypotheses as a Debugging Aid", VL/HCC | A | P | https://arxiv.org/abs/2005.13652 |
| S14 | Beller, Spruit, Spinellis, Zaidman (2018) "On the Dichotomy of Debugging Behavior Among Programmers", ICSE '18 | A | P | https://www.spinellis.gr/pubs/conf/2018-ICSE-debugging-analysis/html/BSSZ18.pdf |
| S15 | Xia et al. (2018) "Measuring Program Comprehension: A Large-Scale Field Study with Professionals", IEEE TSE 44(10) | A | S (publisher abstract copy at Monash) | https://research.monash.edu/en/publications/measuring-program-comprehension-a-large-scale-field-study-with-pr/ |
| S16 | Robillard, Coelho, Murphy (2004) "How Effective Developers Investigate Source Code", IEEE TSE 30(12) | A | P | https://www.cs.mcgill.ca/~martin/papers/tse2004.pdf |
| S17 | Littman et al. (1986); Koenemann & Robertson (1991) — systematic vs as-needed comprehension | A | S (read a 2023 survey that describes both) | https://arxiv.org/pdf/2310.11301 |
| S18 | Brooks, R. (1983) "Towards a theory of the comprehension of computer programs" — hypothesis-driven, beacons | A | Sn/S (secondary descriptions) | via S17 and https://www.st.cs.uni-saarland.de/edu/empirical-se/2006/PDFs/brien03.pdf |
| S19 | Shah & Croft-White (2025) "Understanding Large and Unfamiliar Codebases", C++ on Sea | B | P (your local transcript + slides) | `../../understanding-large-and-unfamiliar-codebases-…/` |
| S20 | Victor, B. (2012) "Inventing on Principle" | B | S (secondary write-ups; video not readable) | https://hacks.mozilla.org/2012/04/bret-victors-inventing-on-principle-and-a-few-things-it-inspired/ |

## Tools

| ID | Source | Tier | Status | URL |
|---|---|---|---|---|
| T01 | GDB manual — Set Watchpoints, Conditions, Break Commands, Dynamic Printf, Set Breaks, Disabling, Save Breakpoints | A | P | https://sourceware.org/gdb/current/onlinedocs/gdb.html/ (pages named in `03-gdb-mechanics.md`) |
| T02 | GDB manual — Convenience Functions/Variables, Python Breakpoints, Reverse Execution, Catchpoints, Frame Info, Variables, Print Settings, Command Files, Mode Options, File Options, Selection, Initialization Files, Auto-loading safe path | A | P | same host |
| T03 | Memfault Interrupt — "Faster Debugging with Watchpoints" | B | P (first ~39k chars) | https://interrupt.memfault.com/blog/cortex-m-watchpoints |
| T04 | Embedded Online Conference — "GDB Deep Dive" (G. Minnehan, 2024) | B | P (session page only; video behind free login) | https://embeddedonlineconference.com/session/GDB_Deep_Dive_EOC |
| T05 | cyrus-and/gdb-dashboard README | B | P | https://github.com/cyrus-and/gdb-dashboard |
| T06 | VS Code docs — C/C++ launch.json reference, Linux config, Remote-SSH, Debugging, C++ debug | A | P | https://code.visualstudio.com/docs/cpp/launch-json-reference ; …/cpp/config-linux ; …/remote/ssh ; …/debugtest/debugging ; …/cpp/cpp-debug |
| T07 | rr project + wiki | A | P | https://rr-project.org/ ; https://github.com/rr-debugger/rr/wiki/Usage |
| T08 | LLDB (lldb-1700.0.9.502, this Mac) | — | **RAN** | local transcripts in `lab/` and the worked-example chapter |
