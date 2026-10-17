# Incident patterns {.chapter data-part="PART 6 · REFERENCE"}

<p class="lede">Real failures, reduced to the pattern and the check that would have caught them. Facts and caveats: <code>research/08-case-files.md</code>. Sources named so you can read the original.</p>

| Incident | Pattern | The check | Source |
|---|---|---|---|
| **Apollo 11** (1969) 1201/1202 alarms | unfinished jobs hold a fixed pool; overload accumulates; restart sheds load | pool and queue limits; margin of the lowest-priority job; restart protection | Eyles 2004 |
| **Patriot, Dhahran** (1991) | clock error grows with uptime (24-bit fixed point) | what is each time value multiplied by, and how long does it stay up? | GAO/IMTEC-92-26 |
| **Therac-25** (1985–87) | non-atomic test-and-set on shared variables | one atomic operation, or ownership | Leveson & Turner 1993 |
| **Ariane 501** (1996) | unprotected conversion; "on exception, halt"; identical redundant units | exception policy; reuse envelope; redundancy shares systematic bugs | Inquiry Board 1996 |
| **Mars Pathfinder** (1997) | priority inversion through a library lock; no inheritance | mutex with inheritance; B in analysis; a trace in the product | Reeves 1997 |
| **Northeast blackout** (2003) | alarm process stalled silently; events queued; server failed | consumer heartbeat; queue age; monitor of the monitor | Task Force 2004; The Register |
| **Spirit rover** (2004) | resource consumed at boot grows with time → reset loop | boot-time resources bounded; evidence persists; safe mode that avoids the culprit | Reeves & Neilson 2005 |
| **Toyota ETCS** (testimony, 2013) [SEC]{.sec} | watchdog fed from a timer interrupt; stack nearly full; high load | feeding condition; stack margin; bound vs load | Koopman 2014 (plaintiff's expert) |
| **Cloudflare** (2017) | wall clock difference negative at a leap second | monotonic clock for durations | Cloudflare post-mortem |
| **Boeing 787** (2015) | 248-day counter overflow, units powered together | wrap time; common-cause | FAA/EASA AD 2015-09-07 |
| **Ingenuity Flight 6** (2021) | one dropped frame + position-based timestamps corrupt later data; load caused the drop | stamp at source; check stamp gaps; budget optional load | NASA/JPL blogs |
| **CAN analysis** (1994→2007) | a widely used schedulability analysis was wrong | tools *and* measurement; know the model | Davis et al. 2007 |
| **Capstone R10** (lab) | silent drops, torn read, wrong priority, slow path in a fast task | counters; snapshot; rate/deadline priority; move slow work down | this project |

## Cross-reference to the six questions

| Question | Incidents |
|---|---|
| Timing | Patriot, 787, Cloudflare, Ingenuity |
| Scheduling | Apollo, Pathfinder, capstone |
| Messaging | Blackout, Ingenuity, capstone |
| Synchronization | Therac-25, Pathfinder, capstone |
| Reliability | Ariane, Spirit, Toyota (testimony), Pathfinder recovery |
| Observability | Pathfinder trace, capstone histograms |
