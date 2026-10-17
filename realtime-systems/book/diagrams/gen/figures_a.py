"""Conceptual figures, part A (Parts 1-2 of the book)."""
from svgkit import *


def six_questions():
    f = Fig(760, 410, "The six questions", "A component in the centre surrounded by six boxes, each a topic and the engineering question it asks: Timing, Scheduling, Messaging, Synchronization, Reliability, Observability.", "six")
    f.box(300, 160, 160, 90, "Your component", "period · deadline · budget", fill=ACC_L, stroke=ACC, sw=2.4)
    items = [
        (8, 14, "1  Timing", "Can it finish on time?", "period, deadline, WCET, jitter"),
        (273, 6, "2  Scheduling", "Which runs first?", "priority, preemption, RM / EDF"),
        (538, 14, "3  Messaging", "What if messages come too fast?", "queues, pub/sub, QoS, backpressure"),
        (8, 304, "4  Synchronization", "Can they share data safely?", "races, locks, inversion, deadlock"),
        (273, 312, "5  Reliability", "What if a component stops?", "watchdog, containment, recovery"),
        (538, 304, "6  Observability", "How do I prove it meets the need?", "trace, histogram, budget vs measured"),
    ]
    for (x, y, h, q, s_) in items:
        f.rect(x, y, 214, 92, "#fff", INK, 1.8, 4)
        f.text(x + 10, y + 24, h, 15, 800)
        f.text(x + 10, y + 48, q, 12, 700)
        f.text(x + 10, y + 70, s_, 11, 400, fill=SOFT)
    f.line(222, 90, 306, 170, ACC, 1.6, arrow="endA")
    f.line(380, 98, 380, 160, ACC, 1.6, arrow="endA")
    f.line(538, 90, 454, 170, ACC, 1.6, arrow="endA")
    f.line(222, 312, 306, 240, ACC, 1.6, arrow="endA")
    f.line(380, 312, 380, 250, ACC, 1.6, arrow="endA")
    f.line(538, 312, 454, 240, ACC, 1.6, arrow="endA")
    return f.render()


def history():
    f = Fig(760, 250, "Timeline: from the polling loop to today's frameworks", "A horizontal timeline with milestones: 1950s interrupts, 1960s Apollo executive and semaphores, 1973 Liu and Layland, 1990 priority inheritance, 1997 Pathfinder, 2008 WCET survey, 2024 PREEMPT_RT in Linux 6.12.", "hist")
    f.line(30, 120, 730, 120, INK, 2.5)
    ms = [
        (60, "1954–57", "interrupts appear", "DYSEAC, 1103A, TX-2", 0),
        (150, "mid-1960s", "Apollo Executive", "priority jobs + Waitlist", 1),
        (250, "1973", "Liu & Layland", "RM / EDF bounds", 0),
        (350, "1990", "Priority inheritance", "Sha, Rajkumar, Lehoczky", 1),
        (435, "1993", "Response-time analysis", "Audsley et al.", 0),
        (520, "1997", "Mars Pathfinder", "inversion found & fixed", 1),
        (600, "2008", "WCET survey", "Wilhelm et al.", 0),
        (690, "2024", "PREEMPT_RT", "mainline Linux 6.12", 1),
    ]
    for (x, yr, a, b, up) in ms:
        f.rect(x - 6, 114, 12, 12, ACC, INK, 1.6, 6)
        if up:
            f.line(x, 114, x, 78, "#888", 1)
            f.text(x, 66, yr, 12.5, 800, "middle", ACC)
            f.text(x, 52, a, 12, 700, "middle")
            f.text(x, 38, b, 10.5, 400, "middle", SOFT)
        else:
            f.line(x, 126, x, 160, "#888", 1)
            f.text(x, 178, yr, 12.5, 800, "middle", ACC)
            f.text(x, 194, a, 12, 700, "middle")
            f.text(x, 208, b, 10.5, 400, "middle", SOFT)
    f.text(30, 238, "Dates: interrupts per Smotherman; others per the papers and reports in research/01. Product release years are omitted (not verified).", 10.5, 400, fill=SOFT)
    return f.render()


def loop_time():
    f = Fig(760, 240, "A super-loop's period is the sum of whatever it did", "Three iterations of a loop. Each runs read, compute, write; the third also takes a rare branch and is almost twice as long, so the period varies.", "loop")
    f.text(20, 24, "One program, no scheduler: the period is whatever the code takes.", 13, 700)
    segs = [("read", 50, "#fff"), ("compute", 90, GRAY2), ("write", 40, "#fff")]
    x = 40
    y = 50
    for i, rare in enumerate([0, 0, 1]):
        start = x
        for (nm, w, fl) in segs:
            f.rect(x, y, w, 40, fl, INK, 1.6)
            f.text(x + w / 2, y + 25, nm, 12, 700, "middle")
            x += w
        if rare:
            f.rect(x, y, 170, 40, "url(#hatch)", INK, 1.6)
            f.rect(x + 22, y + 11, 126, 18, "#fff", INK, 1)
            f.text(x + 85, y + 24, "rare branch", 11.5, 700, "middle")
            x += 170
        f.line(start + 2, y + 56, x - 2, y + 56, ACC, 2, arrow="both")
        f.text((start + x) / 2, y + 76, "period %d = %d ms" % (i + 1, (x - start) // 4), 12, 700, "middle", ACC)
    f.text(40, 165, "A deadline of 'every 45 ms' is met twice and missed once. Nothing in the code says so.", 12.5, 400)
    f.text(40, 188, "Fixes seen later: a hardware timer sets the period (ch. 3), work is split into slots (ch. 5), or a scheduler preempts (ch. 6–7).", 12.5, 400, fill=SOFT)
    f.text(40, 224, "Scale: 4 px = 1 ms.", 10.5, 400, fill=SOFT)
    return f.render()


def clock_stack():
    f = Fig(760, 330, "From crystal to 'time' in your code", "Layers from the hardware oscillator through a hardware timer counter and tick interrupt up to the software tick count and application time calls, with notes on resolution and wrap-around at each layer.", "clock")
    layers = [
        ("Oscillator", "e.g. 25 MHz crystal / PLL", "accuracy in ppm; drifts with temperature"),
        ("Hardware timer / counter", "free-running, fixed width (e.g. 32-bit)", "resolution = 1 / clock;  WRAPS after 2^32 counts"),
        ("Tick interrupt (SysTick)", "fires every 1 ms (1000 Hz)", "tick = the kernel's unit of time; jitter from interrupt latency"),
        ("Kernel tick count", "TickType_t, 16 or 32 bits", "WRAPS: 65.5 s (16-bit @1 kHz) or 49.7 days (32-bit)"),
        ("Your code", "delay, timeout, timestamp, deadline", "compare with (now - start); never now >= deadline"),
    ]
    y = 20
    for i, (a, b, c) in enumerate(layers):
        f.rect(30, y, 240, 52, ACC_L if i in (1, 3) else "#fff", INK if i not in (1, 3) else ACC, 1.8, 4)
        f.text(40, y + 22, a, 14, 800)
        f.text(40, y + 41, b, 11.5, 400, fill=SOFT)
        f.text(300, y + 32, c, 12.5, 700 if i in (1, 3) else 400)
        if i < len(layers) - 1:
            f.line(150, y + 52, 150, y + 62, INK, 1.6, arrow="end")
        y += 62
    return f.render()


def interrupt_flow():
    f = Fig(760, 300, "Interrupts and deferred work", "A main program running, an interrupt arriving, the interrupt handler doing the minimum and posting an event to a queue, then a task doing the long work later.", "irq")
    f.text(20, 22, "Do the minimum in the interrupt; hand the rest to a task.", 13, 700)
    f.rect(30, 60, 700, 36, "#fff", INK, 1.6)
    f.text(40, 83, "Task (low priority)", 12, 700)
    f.rect(190, 60, 150, 36, GRAY2, INK, 1.6); f.text(265, 83, "running…", 12, 400, "middle")
    f.rect(430, 60, 120, 36, GRAY2, INK, 1.6); f.text(490, 83, "…resumes", 12, 400, "middle")
    f.rect(340, 60, 90, 36, "url(#hatch)", INK, 1.6)
    f.rect(30, 140, 700, 36, "#fff", INK, 1.6)
    f.text(40, 163, "Interrupt", 12, 700)
    f.rect(340, 140, 60, 36, ACC, INK, 1.6); f.text(370, 163, "ISR", 12, 800, "middle", "#fff")
    f.rect(30, 220, 700, 36, "#fff", INK, 1.6)
    f.text(40, 243, "Handler task (high prio)", 12, 700)
    f.rect(400, 220, 140, 36, ACC_L, ACC, 1.8); f.text(470, 243, "long work", 12, 700, "middle")
    f.line(340, 118, 340, 140, ACC, 1.8, arrow="endA")
    f.text(352, 132, "event arrives", 11, 700, fill=ACC)
    f.line(370, 176, 400, 220, ACC, 1.8, arrow="endA")
    f.text(396, 205, "post to queue", 11, 700, fill=ACC)
    f.text(30, 280, "ISR: microseconds, no blocking, only 'FromISR' calls.   Handler task: milliseconds, may block, may be preempted.", 12, 400, fill=SOFT)
    return f.render()


def cyclic():
    f = Fig(760, 330, "A cyclic executive and what an overrun does", "Top: a major cycle of four 10 ms minor frames; task A runs every frame, B every second frame, C every fourth. Bottom: task B overruns by 6 ms in frame 2, so the next frame starts late.", "cyc")
    px, ox = 16.0, 70
    fill = {"A": "#fff", "B": GRAY2, "C": "url(#dots)"}
    def frames(y, plan):
        for k in range(4):
            f.rect(ox + k * 10 * px, y, 10 * px, 38, "#fff", "#888", 1, 0, "3 3")
        x = ox
        t = 0.0
        for k, fr in enumerate(plan):
            x = ox + k * 10 * px
            for (nm, d) in fr:
                xs = max(x, ox + (t if False else 0))
                f.rect(x, y, d * px, 38, fill[nm], INK, 1.6)
                f.text(x + d * px / 2, y + 24, nm, 12.5, 800, "middle")
                x += d * px
    f.text(20, 20, "Nominal: every frame's work ends before the next frame begins", 13, 700)
    frames(34, [[("A", 2), ("B", 3), ("C", 4)], [("A", 2)], [("A", 2), ("B", 3)], [("A", 2)]])
    for k in range(5):
        f.text(ox + k * 10 * px, 88, "%d ms" % (k * 10), 10.5, 400, "middle", SOFT)
    f.text(ox, 106, "slack in frame:  1 ms          8 ms          5 ms          8 ms", 11, 400, fill=SOFT)
    f.text(20, 150, "Overrun: B takes 9 ms instead of 3 in frame 2", 13, 700)
    y = 164
    for k in range(4):
        f.rect(ox + k * 10 * px, y, 10 * px, 38, "#fff", "#888", 1, 0, "3 3")
    x = ox
    f.rect(x, y, 2 * px, 38, "#fff", INK, 1.6); f.text(x + px, y + 24, "A", 12.5, 800, "middle")
    f.rect(x + 2 * px, y, 9 * px, 38, GRAY2, INK, 1.6); f.text(x + 6.5 * px, y + 24, "B (9 ms: overrun)", 12, 800, "middle")
    f.rect(x + 10 * px, y, px, 38, "url(#hatch)", "#b00020", 1.6)
    f.text(x + 11 * px, y + 62, "frame 3 starts 1 ms late: A begins at 11 ms, not 10", 12, 700, "start", "#b00020")
    f.rect(x + 11 * px, y, 2 * px, 38, "#fff", INK, 1.6); f.text(x + 12 * px, y + 24, "A", 12.5, 800, "middle")
    f.text(20, 262, "Everything is decided in advance, so jitter is tiny — until one task is late. The lateness pushes later work late", 12.5, 400)
    f.text(20, 282, "(the 'domino effect'), and a new task or a rate change means re-cutting the table.", 12.5, 400)
    f.text(20, 312, "Behaviour per Buttazzo (2005); Eyles (2004) calls this a 'boxcar' executive. Lab H2 runs it.", 11, 400, fill=SOFT)
    return f.render()


def context_switch():
    f = Fig(760, 300, "A context switch", "Task A is running; the SysTick interrupt makes the kernel pick task B; PendSV saves A's registers on A's stack, loads B's, and B resumes. Each task owns a stack.", "ctx")
    f.text(20, 22, "One CPU, many stacks: the kernel swaps which stack the CPU is using.", 13, 700)
    f.rect(30, 50, 310, 30, "#fff", INK, 1.6); f.text(40, 70, "time →", 11, 400, fill=SOFT)
    f.rect(30, 90, 150, 40, GRAY2, INK, 1.6); f.text(105, 115, "Task A runs", 12.5, 700, "middle")
    f.rect(180, 90, 30, 40, ACC, INK, 1.6); f.text(195, 82, "SysTick", 10.5, 700, "middle", ACC)
    f.rect(210, 90, 50, 40, ACC_L, ACC, 1.6); f.text(235, 115, "PendSV", 11, 700, "middle", ACC)
    f.rect(260, 90, 140, 40, "url(#dots)", INK, 1.6); f.rect(275, 100, 110, 20, "#fff", INK, 1); f.text(330, 115, "Task B runs", 12.5, 700, "middle")
    f.text(30, 160, "1. SysTick: tick count++, a delayed task (B) becomes ready, B outranks A", 12, 400)
    f.text(30, 180, "2. PendSV (lowest-priority exception) runs the switch after other interrupts finish", 12, 400)
    f.text(30, 200, "3. Save A's registers on A's stack  →  store A's stack pointer in A's TCB", 12, 400)
    f.text(30, 220, "4. Load B's stack pointer from B's TCB  →  restore B's registers  →  return to B", 12, 400)
    f.rect(470, 60, 120, 150, "#fff", INK, 1.6); f.text(530, 78, "RAM", 12, 800, "middle")
    f.rect(480, 90, 100, 48, GRAY2, INK, 1.4); f.text(530, 108, "stack A", 11.5, 700, "middle"); f.text(530, 124, "saved regs", 10.5, 400, "middle", SOFT)
    f.rect(480, 146, 100, 48, "url(#dots)", INK, 1.4); f.rect(490, 158, 80, 24, "#fff", INK, 1); f.text(530, 175, "stack B", 11.5, 700, "middle")
    f.rect(610, 90, 120, 44, "#fff", INK, 1.4); f.text(670, 108, "TCB A", 12, 700, "middle"); f.text(670, 125, "saved SP, prio", 10.5, 400, "middle", SOFT)
    f.rect(610, 146, 120, 44, "#fff", INK, 1.4); f.text(670, 164, "TCB B", 12, 700, "middle"); f.text(670, 181, "saved SP, prio", 10.5, 400, "middle", SOFT)
    f.line(610, 112, 580, 112, ACC, 1.4, arrow="endA"); f.line(610, 168, 580, 168, ACC, 1.4, arrow="endA")
    f.text(30, 262, "Cost: tens of microseconds of CPU on an MCU, every switch. Frequent preemption is not free (R2 measured 4–24 µs per wake-up).", 11.5, 400, fill=SOFT)
    f.text(30, 282, "Model: FreeRTOS on Cortex-M (SysTick + PendSV); see Memfault 'RTOS context switching on Cortex-M'.", 10.5, 400, fill=SOFT)
    return f.render()


def task_states():
    f = Fig(760, 310, "Task states (FreeRTOS)", "State diagram. Ready to Running when scheduled; Running to Ready when preempted; Running to Blocked when it waits for time or an event; Blocked to Ready when the event occurs; Ready or Running to Suspended via suspend, and back via resume.", "states")
    f.box(300, 20, 160, 60, "Running", "exactly one at a time", fill=ACC_L, stroke=ACC, sw=2.4)
    f.box(30, 140, 170, 60, "Ready", "runnable, waiting for CPU")
    f.box(560, 140, 170, 60, "Blocked", "waiting for time / event")
    f.box(300, 230, 160, 56, "Suspended", "out until resumed")
    f.line(200, 150, 300, 66, INK, 1.8, arrow="end"); f.text(48, 96, "scheduler picks the", 11.5, 700); f.text(48, 111, "highest-priority Ready", 11.5, 700)
    f.line(300, 40, 200, 140, INK, 1.8, arrow="end", dash="6 3"); f.text(206, 62, "preempted / slice ends", 11.5, 700, "start")
    f.line(460, 50, 560, 140, INK, 1.8, arrow="end"); f.text(500, 82, "delay / take / receive", 11.5, 700)
    f.line(560, 185, 200, 185, INK, 1.8, arrow="end"); f.text(380, 177, "time passes / event arrives", 11.5, 700, "middle")
    f.line(115, 200, 300, 252, INK, 1.4, arrow="end"); f.text(120, 240, "suspend", 11.5, 400)
    f.line(380, 230, 380, 80, "#888", 1.2, arrow="end", dash="2 3"); f.text(388, 212, "resume → Ready", 11, 400, fill=SOFT)
    f.text(30, 304, "Only the highest-priority Ready task runs. A task that never blocks never lets lower-priority tasks run.", 11.5, 400, fill=SOFT)
    return f.render()


def util_bounds():
    # n vs bound
    import math
    W, H = 760, 330
    f = Fig(W, H, "Utilization bounds", "Chart of CPU utilization against number of tasks. A curve falls from 1.0 at one task to 0.693 for many tasks: the rate-monotonic guarantee. Above it, up to 1.0, is the region needing exact analysis. A line at 1.0 marks EDF and harmonic periods; a dashed line near 0.88 marks the typical breakdown for random sets.", "ub")
    ox, oy, w, h = 70, 20, 650, 240
    def X(n): return ox + (n - 1) / 19.0 * w
    def Y(u): return oy + (1.0 - (u - 0.5) / 0.5) * h
    f.rect(ox, oy, w, h, "#fff", INK, 1.4)
    f.path("M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f Z" % (ox, Y(0.5), ox + w, Y(0.5), ox + w, Y(math.log(2)), ox, Y(1.0)), "url(#dots)", "none", 0)
    pts = [(n, n * (2 ** (1.0 / n) - 1)) for n in range(1, 21)]
    f.path("M" + " L".join("%.1f %.1f" % (X(n), Y(u)) for n, u in pts), "none", ACC, 3)
    for n, u in pts:
        f.rect(X(n) - 3, Y(u) - 3, 6, 6, ACC, ACC, 1)
    f.line(ox, Y(1.0), ox + w, Y(1.0), INK, 2)
    f.text(ox + w - 4, Y(1.0) - 6, "1.00  EDF · harmonic periods", 12, 700, "end")
    f.line(ox, Y(0.88), ox + w, Y(0.88), INK, 1.4, dash="6 4")
    f.text(ox + w - 4, Y(0.88) - 6, "≈0.88 typical for random sets (Lehoczky–Sha–Ding)", 11.5, 400, "end")
    f.line(ox, Y(math.log(2)), ox + w, Y(math.log(2)), INK, 1.4, dash="2 3")
    f.text(ox + w - 4, Y(math.log(2)) + 16, "0.693 = ln 2 : the RM guarantee for any number of tasks", 11.5, 700, "end", ACC)
    f.text(ox + 120, Y(0.59), "below the curve: schedulable (guaranteed)", 12, 700, "start")
    f.text(ox + 150, Y(0.77), "between curve and 1.0: unknown — run exact analysis", 12, 400, "start", SOFT)
    for n in (1, 2, 3, 4, 5, 10, 20):
        f.text(X(n), oy + h + 18, str(n), 11.5, 400, "middle")
    f.text(ox + w / 2, oy + h + 38, "number of tasks n", 12, 700, "middle")
    for u in (0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
        f.text(ox - 8, Y(u) + 4, "%.1f" % u, 11.5, 400, "end")
    f.text(22, oy + h / 2, "CPU utilization", 12, 700, "middle", rotate=-90)
    f.text(ox, H - 8, "Curve = n(2^(1/n) − 1): 1.000, 0.828, 0.780, 0.757, 0.743 … 0.718 at n = 10, → 0.693. (Liu & Layland 1973, Theorem 5.)", 10.5, 400, fill=SOFT)
    return f.render()


def rta_stack():
    f = Fig(760, 300, "Response-time analysis as stacked interference", "Worst-case response time of task t3 built up as its own 3 ms of work plus interference from t1 (3 jobs of 1 ms) and t2 (2 jobs of 2 ms) before it can finish at 10 ms; its deadline is 12 ms.", "rta")
    px = 52
    ox = 40
    f.text(20, 22, "t3 (C = 3, T = 12) released together with t1 (C = 1, T = 4) and t2 (C = 2, T = 6)", 13, 700)
    f.text(20, 44, "R₃ = C₃ + ⌈R₃/T₁⌉·C₁ + ⌈R₃/T₂⌉·C₂      iterate:  R = 3 → 6 → 7 → 9 → 10 → 10  (converged)", 12.5, 400)
    y = 70
    f.text(ox - 30, y - 6, "ms", 11, 400, fill=SOFT)
    for t in range(0, 13):
        f.line(ox + t * px / 1.6, y, ox + t * px / 1.6, y + 130, "#ddd", 0.8)
        f.text(ox + t * px / 1.6, y - 6, str(t), 11, 400, "middle", SOFT)
    s = px / 1.6
    rows = [("t1", [(0, 1), (4, 1), (8, 1)], INK), ("t2", [(1, 2), (6, 2)], GRAY3), ("t3", [(3, 1), (5, 1), (9, 1)], ACC)]
    for r, (nm, segs, fl) in enumerate(rows):
        yy = y + 8 + r * 38
        f.text(ox - 8, yy + 20, nm, 13, 700, "end")
        for (a, d) in segs:
            f.rect(ox + a * s, yy, d * s, 28, fl, "#fff", 1)
    f.line(ox + 12 * s, y, ox + 12 * s, y + 130, "#b00020", 2, dash="5 3"); f.text(ox + 12 * s + 4, y + 142, "deadline 12", 11.5, 700, fill="#b00020")
    f.line(ox + 10 * s, y + 90, ox + 10 * s, y + 130, ACC, 2); f.text(ox + 10 * s + 4, y + 156, "R₃ = 10", 12, 800, fill=ACC)
    f.text(20, 262, "Dark: t1.  Mid-gray: t2.  Teal: t3 — it only runs in the gaps (ms 3, 5, 9).  Slack = 12 − 10 = 2 ms.", 12, 400)
    f.text(20, 282, "Utilization here is 0.833 — above the 0.780 bound — yet the exact test proves it schedulable. (Lab H3, demo 1.)", 11.5, 400, fill=SOFT)
    return f.render()


ALL = [("six-questions", six_questions), ("history", history), ("loop-time", loop_time), ("clock-stack", clock_stack),
       ("interrupt-flow", interrupt_flow), ("cyclic-executive", cyclic), ("context-switch", context_switch),
       ("task-states", task_states), ("util-bounds", util_bounds), ("rta-stack", rta_stack)]
