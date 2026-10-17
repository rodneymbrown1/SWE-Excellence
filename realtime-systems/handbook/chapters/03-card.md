# The Component Card {.chapter data-part="PART 2 · BUILD"}

<p class="lede">One page per component. It is the timing contract, the data contract and the failure contract in one place. Fill it before you write code; update it when the code changes. A reviewer should be able to approve or reject a change from the card alone.</p>

## How to fill each field

| Field | What to write | Typical mistake |
|---|---|---|
| **Purpose** | one sentence, a verb and an object | listing implementation |
| **Trigger / rate** | what starts a job and how often, *minimum* gap for events | "as fast as possible" |
| **Deadline** | latest completion, and **who requires it** | copying the period without checking |
| **Budget** | an upper bound and *how you know* (analysis, measured max, guess) | typical time instead of worst case |
| **Priority** | the number and the rule that produced it | "importance" |
| **Miss policy** | what happens to the next release | not stated |
| **Inputs / outputs** | each with rate, queue depth, overflow policy, age limit, timestamp source | no overflow policy |
| **Shared data** | owner, protection, longest hold | "protected by `volatile`" |
| **Blocks on** | every wait, with its timeout | an untimed wait |
| **Memory** | allocations after init, pools, growth | "malloc as needed" |
| **Lifecycle** | what must exist first; state after restart | sleeps to "let it start" |
| **Failure** | detector, reaction, blast radius, recovery, evidence | blank |
| **Evidence** | requirement → metric → method → margin → result | an average |

**Rule of thumb:** if a field takes more than a minute, you have found something the team has not decided.

:::: {.cardpage}
## Component Card (blank)

<div class="form tall">
<div class="hd">Component Card  ·  component ______________  ·  owner ________  ·  version/date ________</div>
<div class="f"><b>PURPOSE</b> (one sentence)<span class="ln"></span></div>
<div class="grid2">
<div class="f"><b>TRIGGER</b> ☐ periodic ☐ sporadic ☐ message ☐ interrupt<span class="ln"></span></div>
<div class="f"><b>RATE</b> period T / min gap ________  jitter limit ________<span class="ln"></span></div>
<div class="f"><b>DEADLINE</b> D = ________ (source: ________)<span class="ln"></span></div>
<div class="f"><b>BUDGET</b> C = ________ (☐ analysed ☐ measured max ☐ guessed)<span class="ln"></span></div>
<div class="f"><b>PRIORITY</b> ________ (rule: ________)  <b>stack</b> ____ words, min-free ____<span class="ln"></span></div>
<div class="f"><b>MISS POLICY</b> ☐ continue ☐ skip ☐ abort ☐ degrade ☐ reset<span class="ln"></span></div>
</div>
<div class="f"><b>INPUTS</b> (name · from · rate · queue depth · overflow policy · max age · QoS)<span class="ln"></span><span class="ln"></span><span class="ln"></span></div>
<div class="f"><b>OUTPUTS</b> (name · to · rate · stamped where, by what clock)<span class="ln"></span><span class="ln"></span></div>
<div class="f"><b>SHARED DATA touched</b> (datum · read/write · protection · longest hold)<span class="ln"></span><span class="ln"></span></div>
<div class="f"><b>BLOCKS ON</b> (locks, queues, I/O, delays; timeouts)<span class="ln"></span></div>
<div class="f"><b>MEMORY</b> static / heap allocations after init? (should be none) · pools · growth with time<span class="ln"></span></div>
<div class="f"><b>LIFECYCLE</b> start-up needs (who must exist first) · stop/drain · state after restart<span class="ln"></span><span class="ln"></span></div>
<div class="f"><b>FAILURE</b> detector · reaction · blast radius · recovery · evidence kept<span class="ln"></span><span class="ln"></span></div>
<div class="f"><b>EVIDENCE</b> requirement → metric → method → margin → result<span class="ln"></span><span class="ln"></span><span class="ln"></span></div>
<div class="f"><b>? OPEN QUESTIONS</b> (each with who can answer)<span class="ln"></span><span class="ln"></span></div>
</div>
::::

:::: {.cardpage}
## Component Card (worked example: the filter in lab R10)

<div class="form" style="font-size:9.4pt">
<div class="hd">Component Card  ·  filter  ·  owner: pipeline team  ·  baseline of lab R10</div>
<div class="f"><b>PURPOSE</b> Turn each raw IMU sample into an attitude estimate and publish it.</div>
<div class="f"><b>TRIGGER</b> message (one raw sample per ≈997 µs, from the IMU interrupt through `q_raw`).  <b>RATE</b> ≈1,003 Hz; sensor has its own clock (not harmonic with the 10 ms control).</div>
<div class="f"><b>DEADLINE</b> estimate published ≤ 3 ms after the IMU interrupt for 99.9% of samples (R-2).  <b>BUDGET</b> 400 µs per sample (measured); **plus a 6 ms recalibration every 250th sample** ← does not fit the rate: a defect.</div>
<div class="f"><b>PRIORITY</b> 4 (above control, below actuator).  The logger runs at **6**: wrong (it can delay the filter by its whole 3 ms).</div>
<div class="f"><b>MISS POLICY</b> not defined (the queue silently drops).  ← a defect.</div>
<div class="f"><b>INPUTS</b> `q_raw`: depth **4**, overflow = drop newest, **no counter visible**, age limit 3 ms, stamp at the interrupt (hardware timer).  ← depth needs ≥ 8 and a visible counter.</div>
<div class="f"><b>OUTPUTS</b> `att` (shared struct: angle, ~angle, seq, t_us), stamped with the sample's interrupt time.</div>
<div class="f"><b>SHARED DATA</b> `att`: writer = filter; reader = control; protection = **none**; two reads at different times → torn reads (47 of 309 cycles).  ← needs a snapshot.</div>
<div class="f"><b>FAILURE</b> detector: none · reaction: none · blast radius: control gets stale or mixed data · evidence: none.</div>
<div class="f"><b>EVIDENCE</b> R-1 (no loss): `dropped_raw` = 54 → fail · R-2: p99.9 = 9.5 ms → fail · R-3: `torn` = 47 → fail · R-4: `ctrl_late` = 61 → fail.</div>
<div class="f"><b>AFTER FIXES</b> logger priority 1 · depth 8 + counter · snapshot under a critical section · recalibration moved to a priority-2 task → all four met (p99.9 = 631 µs).</div>
</div>
::::
