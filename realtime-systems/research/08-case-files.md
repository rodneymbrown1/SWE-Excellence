# 08 · Case files — what each real incident teaches, and how solid the facts are

Each row: what we say in the book, the source, the status, and the caveat. "Class" maps to the six questions (T timing · S scheduling · M messaging · Y synchronization · R reliability · O observability).

| # | Incident | Class | What the book says (short) | Source / status | Caveat |
|---|---|---|---|---|---|
| 1 | **Apollo 11, 1969** — 1201/1202 alarms | S, M, R | A priority-driven executive with job and memory pools; unexpected ~13% load on a ≤15% margin; unfinished jobs piled up until pools ran out → BAILOUT; restart protection restarted only critical jobs and shed the rest. | C01 Eyles 2004 — **P** | Eyles was on the LM software team; narrative is his. Numbers (13%, 15%, 10%, 8 core sets, 5 VAC) from his paper. Blogs' other numbers not used. |
| 2 | **Patriot, Dhahran 1991** — clock drift | T | 24-bit conversion of a tenths-of-seconds counter; error grows with uptime: 0.0034 s at 1 h → 0.3433 s at 100 h → 687 m range-gate shift. | C04 GAO — **P** | GAO table values used verbatim; OCR errors in the text layer were checked against the table's pattern. |
| 3 | **Therac-25, 1985–87** — race on shared variables | Y | Concurrent access to shared variables with non-indivisible test-and-set; operator edits within seconds could be missed; earlier hardware interlocks masked the defect. | C06 Leveson & Turner — **P** | Many causes (process, interlocks, reporting); the software race is one. |
| 4 | **Ariane 501, 1996** — unhandled conversion exception | R | A 64→16-bit conversion overflow in reused code; policy "on exception, stop the processor"; both identical units stopped. | C07 Inquiry Board — **P** | Web copy of the report; section numbering not cited. |
| 5 | **Mars Pathfinder, 1997** — priority inversion | Y, S, O | Low-priority task held an OS-internal mutex (in `select()`); medium tasks preempted it; high-priority `bc_dist` blocked; `bc_sched` detected the missed cycle and reset; fixed by enabling inheritance on that semaphore; found in <18 h in lab using a trace left in flight. | C02 Reeves — **P** | Reeves is the JPL software lead; corrects the earlier Jones/Wilner account (C03). |
| 6 | **Northeast blackout, 2003** — silent alarm stall | M, R, O | Alarm process "stalled"; events queued; the server hosting it failed; operators unaware; GE traced a race condition. | C09 Task Force — **P**; C10 Register — **P** (tier C) | Race-condition detail is from press coverage of GE's findings. Blackout had many other causes. |
| 7 | **Spirit rover, 2004** — flash filesystem boot loop | R, memory | A resource growing with mission time was consumed at boot; reset loop; recovery by avoiding the file system, deleting files, reformat. | C08 Reeves & Neilson — **P** | Day numbers per paper; mechanism summarized. |
| 8 | **Toyota ETCS (litigated 2013)** — watchdog and tasks | R, S, memory | As testified: watchdog kicked by a timer ISR; didn't detect death of main task; stack 94% full; ~80% CPU load > RM bound. | C- / S22 Koopman slides — **P** | **Plaintiff expert; disputed.** NASA's review found no electronic cause for the events it studied (news summary, Sn). Presented as a *checklist of things to ask*, not a verdict. |
| 9 | **Cloudflare, 2017** — leap-second negative duration | T | Wall-clock difference assumed non-negative; leap second made it negative; panic in weighted selection. | C12 — **P** | Not embedded; chosen for the clock-type lesson. |
| 10 | **Boeing 787, 2015** — 248-day counter | T, R | Software counter in GCUs overflows after 248 days of continuous power; four units powered at once fail together → AD requires periodic power cycle. | C05 EASA/FAA AD — **P** | Unit/width of the counter not in the AD; 10 ms / signed 32-bit is arithmetic inference. |
| 11 | **Starliner OFT-1, 2019** — mission timer | T, O | Mission elapsed timer started at wrong point (~11 h off); independent review also found a second software error and gaps in end-to-end testing. | C13 news reports — **P** (tier C) | NASA/Boeing primary review not retrieved; numbers (11 h, "60 recommendations") are from news summaries. |
| 12 | **Ingenuity Flight 6, 2021** — dropped frame, wrong timestamps | M, T | One lost camera frame; all later images carried wrong timestamps; navigation estimates fought phantom errors; large oscillations; landed safely. | C11 NASA blogs — **P** | The posts do not say which software layer assigned the timestamps. |
| 13 | **CAN schedulability analysis, 1994 → 2007** | S | Widely used analysis was found flawed; revised. | S13 Davis et al. — **P** | Abstract-level read. |
| 14 | **Executor timing in ROS 2, 2019** | S, M | Default executor timing behaviour had to be reverse-engineered before analysis. | S14 Casini et al. — **P** (abstract-level) | Paper concerns the 2018-era release. |

## Selection rule

Cases were chosen because (a) a primary or near-primary report exists, (b) the mechanism is a *timing/ordering/queue/clock/supervision* mechanism rather than a pure hardware fault, and (c) each maps to a concrete check the reader can add to a review.

## Cases considered and **not** used

- Mars Climate Orbiter (units) — not a real-time failure.
- Knight Capital / CrowdStrike — not embedded/real-time.
- Boeing 737 MAX MCAS — systems-level design/certification; would need a safety-engineering chapter beyond software fundamentals. Not researched.
- GPS week rollover; Y2K38 — counter wrap family already covered by the 787 and Patriot cases.
