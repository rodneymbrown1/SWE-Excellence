# Inventory forms {.chapter data-part="PART 1 · START"}

<p class="lede">Four tables describe almost any RTOS application: tasks, interrupts, queues and shared data. Fill them from the running system and the framework's files, not from memory. Photocopy as needed.</p>

## How to get each table

| Table | Fastest source |
|---|---|
| Tasks | task-list command; gdb helper (`fr-tasks`); framework topology / launch / schedule files |
| Interrupts | vector table; peripheral init code; interrupt priority settings |
| Queues & messages | queue/pipe/topic creation sites; QoS or depth settings; framework port wiring |
| Shared data | search for mutexes, critical sections, `volatile`, global state; guarded ports |
| Stack/heap margins | high-water marks after a worst-case run |

## A filled example (lab R10)

| Table | Row |
|---|---|
| **Task** | `filter` · message (≈997 µs sensor) · T ≈ 997 µs · D 3 ms · C 400 µs (measured; **+6 ms every 250th**) · prio 4 · stack 256 words, min-free ? · blocks on `q_raw` · owner: pipeline team |
| **Interrupt** | IMU timer · prio 0xC0 (below the kernel line) · ≈1 kHz · handler ≈ 10 µs · stamps `now_us()`, posts to `q_raw` · uses `xQueueSendFromISR` |
| **Queue** | `q_raw`: ISR → filter · 12 B · 1,003/s avg, peak = avg · depth **4** · full → **drop newest** · **no counter shown** · age limit 3 ms · stamped at the interrupt |
| **Shared data** | `att` (angle, ~angle, seq, t_us): writer filter, reader control · protection **none** · hold: 2 reads 150 µs apart · invariant `angle_inv == ~angle` |

The two bold items in each row are the defects the lab plants. You find them by *filling the table*, not by reading the code.

:::: {.cardpage}
## Task table

<div class="form half">
<div class="hd">Task table  ·  system ____________  ·  date ________</div>
<table style="font-size:8.4pt">
<tr><th>Task / component</th><th>Trigger<br>(period / event)</th><th>T or<br>min gap</th><th>D</th><th>C budget<br>(how known?)</th><th>Prio</th><th>Stack<br>(free min)</th><th>Blocks on</th><th>Owner</th></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
</table>
<div class="f"><b>Also list:</b> idle task · timer service task (priority!) · any task the framework created for you.</div>
<div class="f"><b>Notes / ?</b><span class="ln"></span><span class="ln"></span></div>
</div>

<div class="form half">
<div class="hd">Interrupt table</div>
<table style="font-size:8.4pt">
<tr><th>Interrupt</th><th>Source</th><th>Priority<br>(above the kernel line?)</th><th>Rate / min gap</th><th>Handler time (worst)</th><th>Does</th><th>Uses</th></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
</table>
<div class="f"><b>Tick interrupt:</b> rate ____ Hz   cost ____ µs   <b>Longest interrupts-off section:</b> ____ µs (where: ________)</div>
</div>
::::

:::: {.cardpage}
## Queue and message table

<div class="form half">
<div class="hd">Queue / message table  ·  one row per connection</div>
<table style="font-size:8.4pt">
<tr><th>From → to</th><th>Message<br>(size)</th><th>Rate<br>avg / peak</th><th>Depth<br>(from burst?)</th><th>Full →<br>(policy)</th><th>Drop<br>counter?</th><th>Age limit<br>(stamped where?)</th><th>QoS /<br>ownership</th></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
</table>
<div class="f"><b>Depth rule:</b> ⌈(peak rate − service rate) × burst length⌉ + 1.   <b>Latency if full:</b> depth × service time = ______</div>
</div>

<div class="form half">
<div class="hd">Shared data table</div>
<table style="font-size:8.4pt">
<tr><th>Datum</th><th>Owner<br>(writer)</th><th>Readers</th><th>Protection<br>(copy / crit.sect / mutex / atomic word)</th><th>Longest<br>hold</th><th>Blocks whom</th><th>Invariant<br>that detects tearing</th></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
</table>
<div class="f"><b>Lock order</b> (if more than one lock): ______ → ______ → ______      <b>Locks held across a blocking call?</b> ☐ none ☐ list: ________</div>
</div>
::::
