# 09 · What we could not verify (and how the documents handle it)

Honesty ledger. If you read one file in this folder, read this one.

| Item | Problem | How the documents treat it |
|---|---|---|
| Stankovic (1988) full text | Only citation/award pages and secondary summaries retrieved | Definition used without quotation, attributed "see Stankovic (1988)" |
| Locke (1992) cyclic vs fixed-priority | Abstract only (the downloaded PDF was a different paper) | Conclusion stated as the abstract states it; flagged "abstract-level" |
| Lehoczky–Sha–Ding 88% | Abstract via search; later arXiv paper disputes generality | "High 80s for random sets; do not plan on it" |
| Feiertag et al. 2008 | Abstract via Chalmers page only | Data-age vs reaction-time distinction attributed; the formula in the book is **ours** and labeled so |
| Cervin et al. 2003 (*IEEE CSM*) | Not opened; the thesis was | Only the thesis quotes are used |
| Therac-25 "within about 8 seconds" | Search-result wording only; precise window not verified in the text we read | Book says "within seconds" |
| 787 counter unit/width | AD gives only "software counter … overflow after 248 days" | Presented as "consistent with a signed 32-bit count of 10 ms ticks (2³¹ × 10 ms = 248.55 days)"; labeled inference |
| Starliner numbers | News reports, not NASA's review | Marked tier C; numbers (≈11 h; second error) attributed to the reports |
| Toyota ETCS | Expert slides for the plaintiff; Toyota disputed; NASA found no electronic cause for the events it studied (news) | Used as a *checklist of questions*, never as a finding about the car |
| Northeast blackout "race condition" | Press coverage of GE's analysis; the Task Force report says "stalled" and queueing | Task Force wording for the stall, press attribution for race |
| Ingenuity Flight 6 mechanism layer | Posts say image lost + wrong timestamps; do not name the software layer or framework | Book says exactly that, does not assert F´ involvement |
| Pathfinder `bc_sched` priority "highest except tExec" | From Reeves's email, verified | Used with attribution; Jones's earlier version differs and is not used |
| Apollo "85% CPU", "attributed to X" blog numbers | Blog sources disagree | Not used; only Eyles |
| RTOS product dates (µC/OS 1991, FreeRTOS 2003, Zephyr 2016) | Not verified from primary sources | Timeline in the book uses only verified dates; product years omitted or marked "approx." |
| JetBrains / AspenCore RTOS-share figures | Landing page only; a search summary quoted figures we could not confirm in the downloaded text | **Not used** as numbers; the book says "FreeRTOS is the most commonly named RTOS in public developer surveys" only where a survey was read — it was not, so the sentence is omitted |
| cFS pipe depth / scheduler frame defaults | Not verified | Book says "look at the scheduler table and pipe depths in your build" |
| F´ RateGroupDriver divider semantics | SDD read at overview level only | Described generally ("divides a base tick into rate-group cycles") and flagged |
| AUTOSAR WdgM / OSEK details | TLS error on download; secondary lecture material | Three supervision types credited to AUTOSAR; no table-level claims |
| Zephyr zbus, cFS OS_MutSem, HS app, EcuM entries in the framework table | General knowledge | Marked "verify in your framework" in the Handbook |
| ISR categories in OSEK | Not verified | Not discussed |
| MPU/ARINC 653 | Not researched | Named only |
| gdb on target through VS Code | GUI path not executable in this environment | CLI path **[RAN]**; VS Code `launch.json` provided as **[MANUAL]** |
| Real hardware timing | All labs ran under QEMU or on a host | Labs teach method; numbers are not claims about any board |
| Little's law | Used as math, not looked up in the 1961 paper | Stated as a theorem; checked by simulation (Lab H4) |
| FreeRTOS book is v10.6.2-era | Labs use a newer kernel tag | Where an API differs, the lab README notes it |
