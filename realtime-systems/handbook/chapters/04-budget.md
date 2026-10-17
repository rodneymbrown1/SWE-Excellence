# Timing budget sheet {.chapter data-part="PART 2 · BUILD"}

<p class="lede">The budget is where the card's numbers meet arithmetic. It answers "can my component finish on time, given everything above it?" with a number, a slack and a verdict. Do it before you build, and again after you measure.</p>

## Procedure

1. **List everything that takes CPU**: every task, **every interrupt (including the tick)**, the timer-service task, framework tasks.
2. **Assign priorities** (rate-monotonic unless the framework has fixed them). Record any that violate the rule and why.
3. **Write C, T, D** for each. Use the *measured maximum plus margin* for C, and call it "claimed".
4. **Utilization** U = Σ C/T. Compare with the Liu–Layland bound for *n* (book ch. 8). If above, continue.
5. **Response time** for each task: R = C + B + Σ ⌈(R + J)/T⌉·C of higher priority (ch. 9). Use `rtcalc.py`.
6. **Blocking B**: the longest critical section of any lower-priority task on a lock your task or a higher one uses (ch. 13).
7. **Overhead**: add ≈ a few tens of µs per wake-up and per tick (measure on your target).
8. **Slack** = D − R. **Require slack ≥ 10–20% of D** (a team choice; zero slack misses in practice: book ch. 9).
9. **Compare with a measurement** (§9). Disagreement of more than the overhead means an input is wrong.

## Calculator

```
python3 labs/host/rtcalc.py name:C:T[:D[:B]] name:C:T ...   [--edf] [--gantt 100]
python3 labs/host/rtcalc.py isr:250:2000 t1:1000:4000 t2:2000:6000 t3:3000:12000
```

Put the interrupts in as tasks. Same time unit throughout.

:::: {.cardpage}
## Timing budget sheet

<div class="form tall">
<div class="hd">Timing budget  ·  system ____________  ·  CPU ______ MHz  ·  tick ____ Hz  ·  date ______</div>
<table style="font-size:8.6pt">
<tr><th>Task / ISR</th><th>Prio</th><th>T</th><th>D</th><th>C (claimed)</th><th>U = C/T</th><th>B</th><th>J</th><th>R (worst)</th><th>Slack D−R</th><th>OK?</th><th>Measured max</th></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>&nbsp;<br>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
</table>
<div class="grid2">
<div class="f"><b>Total U</b> = ______   <b>n</b> = ____   <b>LL bound</b> = ______<span class="ln"></span></div>
<div class="f"><b>Harmonic periods?</b> ☐ yes ☐ no · hyperperiod ______<span class="ln"></span></div>
<div class="f"><b>Overhead assumed</b> (tick, switch): ______ µs per ______<span class="ln"></span></div>
<div class="f"><b>Tasks with slack &lt; 10% D:</b><span class="ln"></span></div>
</div>
<div class="f"><b>Critical section list</b> (lock · holder priority · longest hold · who it blocks)<span class="ln"></span><span class="ln"></span></div>
<div class="f"><b>Verdict & actions</b><span class="ln"></span><span class="ln"></span><span class="ln"></span></div>
</div>
::::

## Reading the result

| Finding | Likely cause | First action |
|---|---|---|
| R > D for one low-priority task | too much higher-priority load, or a large B | find the biggest contributor term; shorten critical sections; move work down |
| R > D for everyone | U too high; or an interrupt is missing from the list | list interrupts; measure; consider rates |
| R ≤ D on paper, miss on target | zero slack plus overhead; an unlisted task; C underestimated | add overhead; list framework tasks; re-measure C under load |
| measured ≪ predicted | not at the critical instant; C overestimated | do not rely on it; the test never aligned the tasks |
| U ≤ bound but a deadline is missed | blocking, jitter, or D < T | use RTA with B and J |
