# Evidence ledger and sources {.appendix data-part="APPENDICES"}

The full registry, with URLs, is `research/00-source-registry.md`. Everything in this book that sounds like a fact about a paper, incident or tool is traceable to a row below. **Status:** **P** = source text read; **S** = reputable secondary read; **Sn** = search summary only; **RAN** = executed in this project.

## Papers and standards

| Source | Used for | Status |
|---|---|---|
| Liu & Layland (1973), *JACM* | assumptions A1–A5, bound, EDF optimality | P |
| Stankovic (1988), *IEEE Computer* | definition of real-time | Sn |
| Buttazzo (2005), *Real-Time Systems* | cyclic executive pros/cons; RM vs EDF; overload | P |
| Audsley et al. (1993), *Software Eng. J.* | response-time analysis | P |
| Sha, Rajkumar, Lehoczky (1990), *IEEE Trans. Computers* | inheritance and ceiling protocols | P |
| Lehoczky, Sha, Ding (1989) | 88% average breakdown | Sn |
| Locke (1992) | cyclic executive vs fixed priority | Sn |
| Wilhelm et al. (2008), *ACM TECS* | WCET: safe/tight, measurement vs analysis | P (key passages) |
| Cervin (2003), PhD thesis | control timing rules of thumb | P (passages) |
| Lu, Park, Seo, Zhou (2008), ASPLOS | 105 real concurrency bugs | P |
| Lee (2006), *IEEE Computer* | threads and nondeterminism | P |
| Eide & Regehr (2008), EMSOFT | `volatile` miscompilation | S |
| Davis, Burns, Bril, Lukkien (2007), *Real-Time Systems* | CAN analysis flaw | P (abstract) |
| Casini et al. (2019), ECRTS | ROS 2 executor response-time analysis | P (abstract-level) |
| Feiertag et al. (2008) | data age vs reaction time | Sn |
| Dunkels et al. (2006), SenSys | protothreads | P |
| Holzmann (2006), *IEEE Computer* | Power of Ten | P |
| Lamport (1978), *CACM* | ordering, logical clocks | P (downloaded; used for the idea) |
| Tene (2012–15) talk & post | coordinated omission | P |
| Smotherman, "History of Interrupts" | interrupt history | P |
| OSTEP (Arpaci-Dusseau) | deadlock conditions, scheduling basics | P |
| ROS 2 docs (QoS; lifecycle design) | QoS policies; lifecycle states | P |
| F´ docs (ActiveRateGroup SDD; component/port selection; cheatsheet) | component kinds, rate groups | P |
| FreeRTOS kernel book; Zephyr scheduling docs; Linux `SCHED_DEADLINE` docs | kernel behaviour | P |
| AUTOSAR WdgM; OSEK OS | watchdog supervision types; ceiling resources | Sn |

## Incident reports and accounts

| Case | Source | Status |
|---|---|---|
| Apollo 11 alarms | Eyles (2004), AAS | P |
| Mars Pathfinder | Reeves (1997) email; Jones (1997) summary | P |
| Patriot, Dhahran | GAO/IMTEC-92-26 | P |
| Boeing 787 counter | FAA/EASA AD 2015-09-07 | P |
| Therac-25 | Leveson & Turner (1993) | P |
| Ariane 501 | Inquiry Board report (1996) | P |
| Spirit FLASH anomaly | Reeves & Neilson (2005) | P |
| Northeast blackout 2003 | Task Force final report; The Register | P (alarm sections) / P (tier C) |
| Ingenuity Flights 6 & 8 | NASA/JPL blog posts | P |
| Starliner OFT-1 | news reports (SpacePolicyOnline) | P (tier C) — used only in `research/` |
| Cloudflare leap second | Cloudflare post-mortem | P |
| Toyota ETCS | Koopman (2014) slides, **plaintiff's expert** | P — **[SEC]**, disputed |

## Things we could not confirm (and how this book treats them)

See `research/09-claims-we-could-not-verify.md`. The important ones: the 787 counter's width and unit (inference only); Toyota material is expert testimony; product release years for RTOSes (omitted); cFS pipe/scheduler defaults (not stated); which software layer assigned Ingenuity's timestamps (not stated by NASA); real-board timing (all labs ran on an emulator with a deterministic clock).

## What was executed

[RAN]{.ran} Host labs H1–H5 (macOS, Apple clang 17, Python 3.12); RTOS labs R0–R10 on FreeRTOS-Kernel V11.3.2, QEMU 11.1.2 (`mps2-an385`), `arm-none-eabi-gcc` 16.2.0, gdb 18.1. Transcripts: `labs/transcripts/`. **[MANUAL]**: the VS Code `launch.json` example.
