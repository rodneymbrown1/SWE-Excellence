# First hour on the device {.chapter data-part="PART 1 · START"}

<p class="lede">Five steps, each with a gate. By the end you can say what the scheduler does, what runs when, what is shared, and how to see inside, without having read the whole code base.</p>

{{fig:recon-flow | The first hour. Do not skip a gate; a "no" is the most useful thing you will learn today.}}

## Step 1 · Run it

☐ Build with debug symbols and **no optimisation** (`-O0 -g`, or `-Og`) so variables are visible. Note the exact command.
☐ Run it on the real target or the emulator. Save the first 200 lines of output.
☐ Run it twice. Do the two logs match? If not, note which lines differ (timing? ordering?).
☐ Write down: **one thing it did that surprised you.** It is your first lead.

## Step 2 · Read the configuration

Open the kernel configuration (`FreeRTOSConfig.h`, Zephyr `prj.conf`/Kconfig, the AUTOSAR OS config, the cFS platform config). Fill the **Framework Recon Sheet** on the next page. Anything that says "default" or "I think" is a `?`.

**Gate A.** *Can you state the scheduler policy, the tick rate, the number of priority levels, whether it preempts, and what detects a stack overflow?*

## Step 3 · Inventory

Fill the forms in §2: every task, every interrupt, every queue, every shared datum. Sources: the running system (a task list command or debugger), the framework's topology/launch/schedule files, a search for locks and queue creation.

**Gate B.** *Does every task have a trigger or period, a priority, a stack size and an owner? Does every queue have a depth, an overflow policy and a drop counter?*

## Step 4 · Budget

Fill the Timing Budget (§4) from the inventory: period, deadline, budget, load. Run `rtcalc.py` on it.

**Gate C.** *Does every periodic component have a deadline and a defended budget? What is the utilization and the worst response of the lowest-priority task?*

## Step 5 · Measure

Pick **one** question from the inventory you are least sure of and measure it with the recipes in §9 (a histogram, a counter, a trace).

**Gate D.** *Do you have one number per requirement (p99.9, max, drops, misses), not an average?*

## What a good first hour produces

| Artifact | Looks like | Why it matters |
|---|---|---|
| **Recon sheet** (next page) | every line filled or marked `?` | the configuration is the first document; a `?` is a question for the owner |
| **A log you can repeat** | command, build id, 200 lines of output, twice | a baseline to compare every later change against |
| **Task / interrupt / queue / shared-data tables** | one row per item, from the running system | the map of where preemption and loss can happen |
| **A timing budget with a verdict** | utilization, worst response of the lowest-priority task, slack | tells you whether to worry before you measure |
| **One measured number** | e.g. "p99.9 = 9.5 ms over 2,946 samples" | proves you can observe the system |
| **A `?` list with owners** | each unknown has a person and a date | turns ignorance into a schedule |

**Worked example (lab R10, first hour).** Run: 3,000 samples, "mean latency 715 µs". Config: fixed priority, 1 kHz tick, 8 priorities. Inventory: 5 tasks + 1 interrupt; `q_raw` depth 4, no drop counter shown. Budget: logger at priority 6 puts the filter's worst response at 3.6 ms (> 3 ms requirement). Measure: p99.9 = 9.5 ms. `?` list: why is the logger at 6? who reads drops? Result: four defects found in the first hour, none by reading the code.

## Then branch

**BUILD** → §3 Component Card and §5 checklist · **DEBUG** → §6 Triage · **UNDERSTAND** → §7 trace one message.

:::: {.cardpage}
## Framework Recon Sheet

<div class="form tall">
<div class="hd">Framework Recon Sheet</div>
<div class="f"><b>System / framework:</b> ____________________  <b>Version:</b> ________  <b>Date:</b> ________  <b>By:</b> ________</div>
<div class="f"><b>Target:</b> board / emulator ____________  <b>CPU:</b> ________  <b>Clock:</b> ______ MHz  <b>RAM:</b> ______  <b>Cores:</b> ____</div>
<div class="grid2">
<div class="f"><b>Scheduler policy</b> (fixed-prio / EDF / cooperative / table)<span class="ln"></span></div>
<div class="f"><b>Preemptive?</b> time slicing? <span class="ln"></span></div>
<div class="f"><b>Tick rate</b> and tick width (16/32/64-bit) → wraps in<span class="ln"></span></div>
<div class="f"><b>Priority levels</b> / idle / timer-task priority<span class="ln"></span></div>
<div class="f"><b>Memory</b>: static or heap? scheme? size<span class="ln"></span></div>
<div class="f"><b>Overflow checks</b> (stack, heap hook, assert)<span class="ln"></span></div>
<div class="f"><b>Mutexes with priority inheritance?</b><span class="ln"></span></div>
<div class="f"><b>ISR-safe API names</b> / interrupt priority limit<span class="ln"></span></div>
<div class="f"><b>Watchdog</b>: who feeds it, from where<span class="ln"></span></div>
<div class="f"><b>Reset reason / post-mortem</b> available?<span class="ln"></span></div>
<div class="f"><b>Lifecycle</b>: who starts what, in what order<span class="ln"></span></div>
<div class="f"><b>Message system</b> (queues / bus / topics) + QoS defaults<span class="ln"></span></div>
<div class="f"><b>Trace / stats hooks</b> enabled?<span class="ln"></span></div>
<div class="f"><b>Log output</b> (UART / RTT / SWO) and its cost<span class="ln"></span></div>
</div>
<div class="f"><b>Where the framework's own docs say the above</b> (file / page)<span class="ln"></span><span class="ln"></span></div>
<div class="f"><b>What surprised me in the first run</b><span class="ln"></span><span class="ln"></span></div>
<div class="f"><b>? items to resolve (owner · date)</b><span class="ln"></span><span class="ln"></span><span class="ln"></span></div>
</div>
::::
