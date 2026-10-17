# 01 · What "real-time" means, and how the loop became an RTOS

## 1. Definition

- **Stankovic (1988)**, "Misconceptions About Real-Time Computing: A Serious Problem for Next-Generation Systems", *IEEE Computer* 21(10):10–19. [S02, **Sn**]
  Only citation/award pages and a UVA summary were read. The widely repeated working definition — *correctness depends not only on the logical result but also on when the result is produced* — is attributed to this paper by a Chalmers lecture slide and the UVA summary. We use the definition, attribute it with "see Stankovic (1988)", and do not quote the paper.
- **Hard / firm / soft** — a deadline whose miss is catastrophic / makes the result worthless / only degrades value. Standard textbook taxonomy (Liu, Buttazzo, Burns & Wellings). Used as vocabulary; no single primary quote needed.
- **Key consequence used in the book:** "real-time" is *not* "fast". Speed is a property of the average case; real-time is a property of the **worst case against a stated deadline**. (Consistent with every analysis paper below, all of which are about bounds, not averages.)

## 2. Liu & Layland (1973) — the paper everything else cites [S01, **P**]

Read in full (`_raw/liu-layland-1973/`). Verified:

- Five assumptions, quoted in the book in paraphrase:
  - (A1) requests for hard-deadline tasks are **periodic**, with constant interval;
  - (A2) deadline = **the next request** of the same task (run-ability constraint only);
  - (A3) tasks are **independent**;
  - (A4) run-time per task is **constant** ("can be interpreted as the maximum" run-time);
  - (A5) non-periodic tasks are special (initialization/failure-recovery) and do not have hard deadlines.
- **Theorem 1:** the **critical instant** for a task is when it is requested simultaneously with all higher-priority tasks.
- **Theorem 5:** for *m* tasks with fixed priorities (rate-monotonic order) the least upper bound on utilization is **U = m(2^{1/m} − 1)**; "for large m, U ≈ ln 2" (≈ 0.693). Two tasks: 0.828.
- **Deadline-driven (EDF) scheduling:** "the least upper bound on the processor utilization factor is uniformly 100 percent" (Section 6 / Theorem 7).
- Note for readers: the bound is **sufficient, not necessary**. A task set above 69.3% may still be schedulable (exact analysis is in §3 of `03-scheduling-and-analysis.md`).
- Important caveat for practitioners: assumptions A3 and A4 exclude **blocking on shared resources** and **varying execution times**; later work (SRL 1990, Audsley 1993) relaxes them.

## 3. Interrupts and the road to the executive

Source: Mark Smotherman, "History of Interrupts" (Clemson) [S20, **P**] — a scholarly timeline compiled by a computer-architecture historian, with explicit uncertainty notes.

- Dates the page lists as firsts: **DYSEAC (1954)** I/O interrupt; **UNIVAC 1103 / 1103A** (1953 / 1956) "typically cited as first"; **TX-2 (1957)** multiple-sequence / vectored; **IBM Stretch (1957)**; **Manchester Atlas (1961)** page fault.
- Smotherman's own caveat that is worth keeping: *the 1953 ERA 1103 manual does not describe interrupts; others credit the 1103A (1956)*. So the book says "by the mid-1950s" rather than naming one first.
- The book's story: polling loop → interrupt (event announces itself) → multiple sequences of work → an **executive** to share the machine.

## 4. Apollo's Executive — priority scheduling designed from nothing [C01, **P**]

Eyles (2004), read in full (`_raw/eyles-lm-guidance/`). Verified quotes/facts:

- Designed by **Hal Laning** in the mid-1960s "from whole cloth with no examples to guide him" — the Executive (priority jobs) + Waitlist (timed tasks) + hardware interrupts.
- **Boxcar executive** (Eyles's term): computations divided explicitly between time slices; "painful to implement"; "a brittle system during operation. It breaks down completely as soon as any function takes longer than the time it is allocated." — this is a **cyclic executive** failure mode, in 1960s words.
- **Jobs:** each assigned a priority; "the operating system always executed the job with the highest priority". "This system gave the illusion that jobs ran simultaneously, although of course they merely took turns."
- **Resources:** an array of **eight core sets** (12 registers × 15 bits) and **five Vector Accumulator areas**; at most **eight jobs** could be in the queue.
- **Overload mechanism (exactly):** `READACCS` ran every **2 seconds** and scheduled the big `SERVICER` job. If `SERVICER` had not finished, "the earlier SERVICER had not released its core set" → each new request took another core set → resources exhausted → `BAILOUT` with **1202** (no core sets) or **1201** (no VAC areas).
- **Margin numbers:** duty-cycle margin "over 15%" before landing radar lock; ≈13% after; ≤10% with a monitor display (Verb 16 Noun 68) added. The rendezvous-radar interface problem "stole approximately 13% of the computer's duty cycle, resulting in five program alarms and software restarts".
- **Restart protection:** waypoints; after restart only the most recent incarnation of each job restarted; non-critical, non-protected functions (e.g. the Verb 16 Noun 68 monitor) were terminated. "Here a system of restart protection that was primarily motivated by the possibility of hardware glitches synergistically provided a means to shed computational load" — and "the problem fixed itself" in P63; in P64 "the software restart flushed the Executive queue but could not shed load" because essential software alone left <10% margin.
- **Used in book:** overload (ch. 11), cyclic-executive vs priority (ch. 5, 7), job/queue exhaustion as backpressure (ch. 15), restart/lifecycle (ch. 18, 19).
- **Not used:** contested numbers from blogs ("85% CPU", attribution of the design to specific individuals other than Laning) — see `09-…`.

## 5. Cyclic executives vs priority-driven scheduling

- **Buttazzo (2005)** [S03, **P**], introduction (verified): describes *timeline scheduling* — "the time line is divided into slots of fixed length (minor cycle) and tasks are statically allocated in each slot … The schedule is then constructed up to the least common multiple of all the periods (called the hyperperiod or the major cycle) and stored in a table." Pros: "straightforward to implement", "very small" jitter. Cons: "fragile during overload situations, since a task exceeding its predicted execution time could generate (if not aborted) a domino effect on the subsequent tasks, causing their execution to exceed the minor cycle boundary (timeline break)"; "a creation of a new task, or a little change in a task rate, might modify the values of the minor and major cycles, thus requiring a complete redesign of the scheduling table."
- **Locke (1992)** [S07, **Sn**]: abstract only — compares the same application built both ways; concludes that with rate-monotonic priorities the fixed-priority approach "generally dominates" the cyclic executive for hard real-time systems. Cited by Buttazzo as Locke (1997) in the chapter above (different edition/reprint); we cite the 1992 paper by DOI and flag that we read only the abstract.

## 6. Why threads are hard — one framing

- **Lee (2006)** [S11, **P**]: "Threads, as a model of computation, are wildly nondeterministic, and the job of the programmer becomes one of pruning that nondeterminism." The paper's advice: "Nondeterminism should be explicitly and judiciously introduced where needed." Used in ch. 6/12 as motivation for *run-to-completion* and *message-passing* styles, not as a reason to avoid RTOSes.

## 7. RTOS products (dates)

Search-snippet level only (Wikipedia/aggregator pages): VxWorks first released 1987 (Wind River developed its own kernel to replace VRTX), QNX 1982. We could **not** verify µC/OS (1991), FreeRTOS (2003), Zephyr (2016) from primary sources in this pass. The book's history timeline uses only the dates verified in §3 (interrupts), §2 (1973), §4 (1960s Executive), and states that product-release years are "approximate, from vendor/encyclopedia pages". See `09-…`.
