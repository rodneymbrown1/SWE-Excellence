# Source registry

Status: **P** read source text · **S** read reputable secondary · **Sn** search snippet only · **U** unverified.
Tier: **A** paper/report/standard/manual · **B** practitioner/course · **C** blog/aggregator.
Local copy = `_raw/<dir>/` (text in `text.txt`).

## Theory and analysis

| ID | Source | Tier | Status | Local dir / URL |
|---|---|---|---|---|
| S01 | Liu & Layland (1973) "Scheduling Algorithms for Multiprogramming in a Hard-Real-Time Environment", *JACM* 20(1):46–61 | A | P | `liu-layland-1973` · https://www.cis.upenn.edu/~lee/07cis505/Lec/liu73scheduling.pdf |
| S02 | Stankovic (1988) "Misconceptions About Real-Time Computing", *IEEE Computer* 21(10):10–19 | A | Sn (citation + award pages; full text not retrieved) | https://ethw.org/John_A._Stankovic |
| S03 | Buttazzo (2005) "Rate Monotonic vs. EDF: Judgment Day", *Real-Time Systems* 29:5–26 | A | P (post-print via Wayback copy of IRIS) | `buttazzo-judgment-day` · https://iris.sssup.it/handle/11382/302823 |
| S04 | Audsley, Burns, Richardson, Tindell, Wellings (1993) "Applying new scheduling theory to static priority pre-emptive scheduling", *Software Engineering Journal* 8(5):284–292 | A | P | `audsley-rta-1993` |
| S05 | Sha, Rajkumar, Lehoczky (1990) "Priority Inheritance Protocols", *IEEE Trans. Computers* 39(9):1175–1185 | A | P | `srl-priority-inheritance` · https://www.math.unipd.it/~tullio/RTS/2009/SRL-1990.pdf |
| S06 | Lehoczky, Sha, Ding (1989) "The Rate Monotonic Scheduling Algorithm: Exact Characterization and Average Case Behavior", RTSS | A | Sn (abstract: 88% breakdown utilization for uniformly distributed tasks) | via search; counter-view arXiv 0912.3852 (Sn) |
| S07 | Locke (1992) "Software architecture for hard real-time applications: cyclic executives vs. fixed priority executives", *Real-Time Systems* 4:37–53 | A | Sn (abstract). The copy downloaded as `locke-umbc-read15` is a **different paper** and is not used | DOI 10.1007/BF00365463 |
| S08 | Wilhelm et al. (2008) "The worst-case execution-time problem — overview of methods and survey of tools", *ACM TECS* 7(3) | A | P (skimmed key passages) | `wilhelm-wcet` |
| S09 | Cervin (2003) PhD thesis "Integrated Control and Real-Time Scheduling", Lund (file was named `Cer03.pdf`; it is the thesis, not the *IEEE CSM* article) | A | P (targeted passages) | `cervin-control-timing` |
| S10 | Lu, Park, Seo, Zhou (2008) "Learning from Mistakes", ASPLOS | A | P | `lu-concurrency-bugs` |
| S11 | Lee (2006) "The Problem with Threads", *IEEE Computer* 39(5) (UCB/EECS-2006-1 version) | A | P | `lee-problem-with-threads` |
| S12 | Eide & Regehr (2008) "Volatiles Are Miscompiled, and What to Do about It", EMSOFT | A | S (LLVM pubs abstract + Regehr's retrospective blog) | `eide-regehr-volatile`, `feiertag-regehr-blog` (the latter is Regehr's blog post, misnamed on disk) |
| S13 | Davis, Burns, Bril, Lukkien (2007) "CAN schedulability analysis: Refuted, revisited and revised", *Real-Time Systems* 35:239–272 | A | P (abstract + skim) | `davis-can-2007` |
| S14 | Casini, Blaß, Lütkebohle, Brandenburg (2019) "Response-Time Analysis of ROS 2 Processing Chains under Reservation-Based Scheduling", ECRTS | A | P (downloaded; abstract-level use) | `casini-ros2-rta` |
| S15 | Feiertag, Richter, Nordlander, Jonsson (2008) "A Compositional Framework for End-to-End Path Delay Calculation of Automotive Systems under Different Path Semantics" | A | Sn (abstract via Chalmers page); related arXiv 1804.07647 downloaded | `arxiv-latencies-multicore-ecu` |
| S16 | Dunkels, Schmidt, Voigt, Ali (2006) "Protothreads", SenSys | A | P | `dunkels-protothreads` |
| S17 | Holzmann (2006) "The Power of 10", *IEEE Computer* | A | P | `holzmann-power-of-10` |
| S18 | Lamport (1978) "Time, Clocks, and the Ordering of Events in a Distributed System", *CACM* | A | P (downloaded) | `lamport-time-clocks` |
| S19 | Tene — "How NOT to Measure Latency" (QCon SF 2012 slides) and mechanical-sympathy post on Coordinated Omission | B | P | `tene-latency-qcon`, `tene-coordinated-omission` |
| S20 | Smotherman — "History of Interrupts" (Clemson) | B | P | `smotherman-interrupts` |
| S21 | Arpaci-Dusseau — *Operating Systems: Three Easy Pieces* (cpu-mechanisms, cpu-sched, threads-bugs, threads-sema) | A (textbook, free) | P | `ostep-*` |
| S22 | Koopman (2014) "A Case Study of Toyota Unintended Acceleration and Software Safety" (slides, CC BY 4.0) | B | P — **plaintiff's expert witness**; disputed by Toyota | `koopman-toyota-slides` |
| S23 | Cervin et al. (2003) "How does control timing affect performance?", *IEEE Control Systems Magazine* 23(3) | A | Sn (abstract only) | https://lup.lub.lu.se/record/161677 |
| S24 | Åström & Wittenmark (1997) *Computer-Controlled Systems* — sampling rule of thumb | A (book) | S (quoted in S09) | via `cervin-control-timing` |
| S25 | Little (1961) "A Proof for the Queuing Formula L = λW", *Operations Research* | A | U (classical theorem; used as math, not as an empirical claim) | DOI 10.1287/opre.9.3.383 |

## Case files

| ID | Source | Tier | Status | Local dir |
|---|---|---|---|---|
| C01 | Eyles (2004) "Tales from the Lunar Module Guidance Computer", AAS 04-064 (hosted at klabs.org) | A | P | `eyles-lm-guidance` |
| C02 | Reeves (1997) email "What really happened on Mars?" — JPL's Pathfinder flight software lead | A (primary account) | P | `reeves-pathfinder` |
| C03 | Jones (1997) message summarising Wilner's RTSS keynote | B | P | `jones-pathfinder` |
| C04 | GAO/IMTEC-92-26 (1992) "Patriot Missile Defense: Software Problem Led to System Failure at Dhahran" | A | P | `gao-patriot` |
| C05 | EASA/FAA AD 2015-09-07 (Boeing 787 GCU 248-day counter) | A | P | `easa-787-ad` |
| C06 | Leveson & Turner (1993) "An Investigation of the Therac-25 Accidents", *IEEE Computer* 26(7) | A | P | `therac25-leveson` |
| C07 | ESA/CNES Inquiry Board (1996) Ariane 501 Failure Report | A | P (web copy) | `ariane5-inquiry` |
| C08 | Reeves & Neilson (2005) "The Mars Rover Spirit FLASH Anomaly", IEEE Aerospace | A | P | `spirit-flash-anomaly` |
| C09 | U.S.–Canada Power System Outage Task Force (2004) Final Report on the August 14, 2003 Blackout | A | P (alarm sections) | `nerc-blackout-final` |
| C10 | The Register (2004) "Software bug blamed for blackout alarm failure" (GE XA/21 race) | C | P | `register-blackout-bug` |
| C11 | NASA/JPL Ingenuity blogs: "Flight 8 Success, Software Updates, and Next Steps" (2021) and "Surviving an In-Flight Anomaly" (Flight 6) | A | P | `ingenuity-flight8-blog`, `ingenuity-flight6-blog` |
| C12 | Cloudflare (2017) "How and why the leap second affected Cloudflare DNS" | B | P | `cloudflare-leap-second` |
| C13 | SpacePolicyOnline reports on Starliner OFT-1 timer + Independent Review Team | C | P (news reports; NASA primary report not retrieved) | `spacepolicy-starliner-software`, `spacenews-starliner-irt` |

## Tools, frameworks, standards

| ID | Source | Tier | Status | Local dir |
|---|---|---|---|---|
| T01 | *Mastering the FreeRTOS Real Time Kernel* (GitHub edition, v10.6.2-era) ch. 1–13 | A | P | `fr-book-ch01` … `fr-book-ch13` |
| T02 | FreeRTOS-Kernel source, pinned tag | A | **RAN** (lab builds) | `../labs/third_party/` |
| T03 | Zephyr kernel scheduling docs; `CONFIG_SCHED_DEADLINE` Kconfig page | A | P | `zephyr-scheduling`, `zephyr-kconfig-sched-deadline` |
| T04 | Linux kernel docs: SCHED_DEADLINE; real-time theory | A | P | `linux-sched-deadline`, `linux-rt-docs` |
| T05 | ROS 2 QoS (ROS 2 docs source, rolling) | A | P | `ros2-qos-raw` |
| T06 | ROS 2 design: managed (lifecycle) nodes | A | P | `ros2-node-lifecycle` |
| T07 | F´ docs: ActiveRateGroup & RateGroupDriver SDD, component/port selection, cheatsheet | A | P | `fprime-*` |
| T08 | NASA cFS README and NTRS overview paper | A | P (overview level) | `cfs-readme`, `cfs-ntrs-2019` |
| T09 | Memfault Interrupt — "Firmware Watchdog Best Practices"; "RTOS context switching on Cortex-M" | B | P | `memfault-watchdog`, `memfault-context-switch` |
| T10 | Ganssle — "A Guide to Watchdog Timers for Embedded Systems" | B | P | `ganssle-watchdogs` |
| T11 | AUTOSAR Watchdog Manager SWS (alive / deadline / logical supervision) | A | Sn (document found; TLS error prevented download) | https://www.autosar.org/ |
| T12 | OSEK/VDX OS 2.2.3 — tasks, alarms, priority-ceiling resources | A | Sn (secondary lecture material) | — |
| T13 | OSADL QA Farm real-time latency plots | B | P (index page) | `osadl-latency` |
| T14 | HdrHistogram README | B | P | `hdrhistogram-readme` |
| T15 | Valvano — UT Austin course syllabus + RTOS book outline | B | P | `valvano-syllabus`, `valvano-outline3` |
| T16 | Samek — "Beyond the RTOS" (Arm community blog) | C (vendor view) | P | `samek-beyond-rtos` |
| T17 | JetBrains "State of Embedded Development 2025" | C | P (landing page only; **no usable RTOS-share figure read**) | `jetbrains-embedded-2025` |
| T18 | QEMU 11.1.2, arm-none-eabi-gcc 16.2.0, arm-none-eabi-gdb 18.1 (Homebrew) | — | **RAN** | `10-lab-environment-notes.md` |
