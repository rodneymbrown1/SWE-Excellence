"""Figures part C: messaging, rates, lifecycle, reliability, memory, distributed, cover, handbook flowcharts."""
from svgkit import *


def pubsub():
    f = Fig(760, 330, "Publish/subscribe with per-subscriber queues and QoS", "Two publishers send to a topic. Three subscribers each have their own bounded queue and QoS: one reliable with depth 10, one best-effort with depth 1, one late-joining that receives the last value (transient local).", "ps")
    f.box(20, 40, 150, 56, "Publisher A", "100 Hz · IMU", fill="#fff")
    f.box(20, 140, 150, 56, "Publisher B", "10 Hz · GPS")
    f.rect(250, 70, 140, 110, ACC_L, ACC, 2.2, 6)
    f.text(320, 100, "TOPIC", 12, 800, "middle", ACC)
    f.text(320, 122, "/state", 15, 800, "middle")
    f.text(320, 146, "type + QoS contract", 11, 400, "middle", SOFT)
    f.line(170, 68, 250, 100, INK, 1.8, arrow="end"); f.line(170, 168, 250, 150, INK, 1.8, arrow="end")
    subs = [("Control", "reliable · keep-last 10", "must not lose; bounded latency"), ("Display", "best-effort · keep-last 1", "latest only; loss is fine"), ("Logger (late join)", "reliable · transient-local", "gets last value on start")]
    for i, (a, b, c) in enumerate(subs):
        y = 20 + i * 100
        f.line(390, 125, 470, y + 36, INK, 1.8, arrow="end")
        f.rect(470, y, 270, 82, "#fff", INK, 1.8, 4)
        f.text(480, y + 20, a, 13.5, 800)
        f.text(480, y + 38, b, 12, 700, fill=ACC)
        f.text(480, y + 55, c, 11.5, 400, fill=SOFT)
        for k in range(5):
            f.rect(480 + k * 22, y + 62, 18, 14, GRAY2 if k < (4 if i == 0 else 1) else "#fff", INK, 1)
        f.text(600, y + 74, "← its own queue", 10.5, 400, fill=SOFT)
    f.text(20, 318, "Each arrow has a rate, a queue depth, a loss policy and an age limit — requirements, even when nobody wrote them down.", 11.5, 400, fill=SOFT)
    return f.render()


def e2e_chain():
    f = Fig(760, 300, "End-to-end latency is not the sum of response times", "A sensor stage at 10 ms, a filter stage at 20 ms and a controller at 40 ms. Worst-case waits for each stage's next period (hatched) dominate the execution times (solid): 80 ms in total against 10 ms of execution.", "e2e")
    px = 7.6
    ox = 40
    stages = [("Sample  T=10", 10, 2), ("Filter  T=20", 20, 3), ("Control  T=40", 40, 5)]
    f.text(20, 22, "Worst case for a signal that appears just after a stage has read its input:", 13, 700)
    x = ox
    y = 60
    for (nm, T, R) in stages:
        f.rect(x, y, T * px, 36, "url(#hatch)", INK, 1.6)
        f.rect(x + T * px, y, R * px, 36, INK, INK, 1.6)
        f.text(x + T * px / 2, y + 60, nm, 12, 700, "middle")
        f.text(x + T * px / 2, y + 76, "wait %d" % T, 11, 400, "middle", SOFT)
        f.text(x + T * px + R * px / 2, y - 6, "run %d" % R, 11, 700, "middle")
        x += (T + R) * px
    f.line(ox, y + 100, x, y + 100, ACC, 2.4, arrow="both")
    f.text((ox + x) / 2, y + 122, "worst-case data age ≈ Σ (T + R) = 12 + 23 + 45 = 80 ms", 13.5, 800, "middle", ACC)
    f.text(ox, 215, "Hatched = waiting for the next period boundary (sampling delay).   Solid = executing (response time R).", 12, 400)
    f.text(ox, 238, "Sum of response times alone: 2 + 3 + 5 = 10 ms. A design reviewed only on that number is off by 8×.", 12, 400, fill=SOFT)
    f.text(ox, 262, "Faster stages shrink the wait; harmonic periods make the pattern repeat; time-stamping at the source lets consumers measure age.", 12, 400, fill=SOFT)
    f.text(ox, 286, "Loose bound used in this book, in the spirit of Feiertag et al. (2008); the exact value depends on phase and path semantics.", 10.5, 400, fill=SOFT)
    return f.render()


def lifecycle():
    f = Fig(760, 330, "Component lifecycle", "State machine: Unconfigured to Inactive via configure, Inactive to Active via activate, Active to Inactive via deactivate, Inactive to Unconfigured via cleanup, any to Finalized via shutdown. Allocation happens during configure; the run loop only happens in Active.", "lc")
    f.box(30, 120, 150, 70, "Unconfigured", "constructed, no resources")
    f.box(250, 120, 150, 70, "Inactive", "configured, not running", fill=ACC_L, stroke=ACC)
    f.box(470, 120, 150, 70, "Active", "processing, publishing", fill=ACC_L, stroke=ACC, sw=2.6)
    f.box(250, 250, 150, 56, "Finalized", "terminal")
    f.line(180, 145, 250, 145, INK, 1.8, arrow="end"); f.text(215, 138, "configure", 11.5, 700, "middle")
    f.line(400, 145, 470, 145, INK, 1.8, arrow="end"); f.text(435, 138, "activate", 11.5, 700, "middle")
    f.line(470, 172, 400, 172, INK, 1.8, arrow="end"); f.text(435, 190, "deactivate", 11.5, 700, "middle")
    f.line(250, 172, 180, 172, INK, 1.8, arrow="end"); f.text(215, 190, "cleanup", 11.5, 700, "middle")
    f.line(325, 190, 325, 250, INK, 1.4, arrow="end", dash="5 3"); f.text(332, 224, "shutdown", 11.5, 700)
    f.path("M545 120 C545 70 600 70 600 120", "none", "#b00020", 1.6, arrow="end"); f.text(600, 66, "error → ErrorProcessing", 11.5, 700, "middle", "#b00020")
    f.text(30, 40, "Allocate, open, subscribe  →  during configure   |   Start timers and processing  →  activate", 12.5, 700)
    f.text(30, 60, "Stop processing, drain  →  deactivate   |   Release  →  cleanup   |   Nothing allocates in Active", 12.5, 400, fill=SOFT)
    f.text(30, 328, "Shape follows the ROS 2 managed-node design (4 primary states, 7 transitions); other frameworks use other names for the same ideas.", 10.5, 400, fill=SOFT)
    return f.render()


def msg_lifecycle():
    f = Fig(760, 270, "A message's life and where it can go wrong", "Pipeline: create, stamp, publish, route, enqueue, dequeue, process, release. Under each stage the failure modes: loss, delay, reorder, duplicate, stale.", "ml")
    st = [("create", "owner?"), ("stamp", "time, seq"), ("publish", "rate"), ("route", "who hears?"), ("enqueue", "depth, policy"), ("dequeue", "who is late?"), ("process", "budget"), ("release", "free / ack")]
    x = 20
    w = 82
    for i, (a, b) in enumerate(st):
        f.box(x, 40, w, 52, a, b, fill=ACC_L if a in ("enqueue", "stamp") else "#fff", stroke=ACC if a in ("enqueue", "stamp") else INK, size=12.5)
        if i < len(st) - 1:
            f.line(x + w, 66, x + w + 8, 66, INK, 1.6, arrow="end")
        x += w + 8
    marks = [(4, "LOSS", "queue full → dropped (is it counted?)"), (1, "STALE", "timestamp assigned late / by position, not at the source"), (5, "DELAY", "consumer starved by higher priority"), (3, "REORDER / DUP", "multiple paths, retries (reliable QoS)")]
    y = 125
    for (i, k, t) in marks:
        cx = 20 + i * (w + 8) + w / 2
        f.line(cx, 92, cx, y + 8, "#888", 1, dash="2 3")
        f.text(cx, y + 20, k, 11.5, 800, "middle", "#b00020")
        y += 0
    f.text(20, 170, "LOSS at enqueue: queue full → dropped. Is the drop counted and visible?", 12, 400)
    f.text(20, 190, "STALE at stamp: a timestamp assigned late (or by stream position) corrupts every later consumer — Ingenuity Flight 6.", 12, 400)
    f.text(20, 210, "DELAY at dequeue: the consumer is starved by higher-priority work, or blocked on a lock.", 12, 400)
    f.text(20, 230, "REORDER / DUPLICATE at route: several paths or retries (reliable delivery) can deliver twice or out of order.", 12, 400)
    f.text(20, 256, "Rule: every arrow needs an owner, an age limit and a named behaviour when it cannot keep up.", 12.5, 800, fill=ACC)
    return f.render()


def watchdog():
    f = Fig(760, 330, "Three ways to feed a watchdog", "Three panels. Left: the timer interrupt feeds the watchdog, so it is fed even if every task is dead. Middle: a low-priority task feeds it, so it detects only total starvation. Right: a supervisor feeds only if every task checked in, so any stuck task causes a reset.", "wd")
    cols = [(10, "1  Feed from the timer ISR", "never detects task death", "Toyota ETCS (as testified)", "#b00020"),
            (260, "2  Feed from a low-priority task", "detects only total starvation", "Memfault: the naive design", "#b00020"),
            (510, "3  Feed only if ALL tasks checked in", "detects any stuck task", "task watchdog; AUTOSAR alive supervision", ACC)]
    for (x, h, s, src, col) in cols:
        f.rect(x, 10, 240, 310, "#fff", INK, 1.6, 6)
        f.text(x + 10, 32, h, 12.5, 800)
        f.text(x + 10, 50, s, 12, 700, fill=col)
        f.text(x + 10, 304, src, 10.5, 400, fill=SOFT)
    # panel1
    f.box(30, 120, 90, 36, "Timer ISR", None, fill=ACC_L, stroke=ACC, size=12)
    f.box(150, 120, 80, 36, "WDT", None, size=12)
    f.line(120, 138, 150, 138, ACC, 2, arrow="endA")
    for i, nm in enumerate(["sensor", "control", "logger"]):
        f.box(30, 190 + i * 34, 90, 28, nm, None, fill="url(#hatch)" if nm == "control" else "#fff", size=11, weight=400)
    f.text(135, 232, "control is dead.", 11, 700, fill="#b00020"); f.text(135, 248, "Nobody asks.", 11, 700, fill="#b00020")
    # panel2
    f.box(290, 120, 90, 36, "low-prio task", None, fill=ACC_L, stroke=ACC, size=11)
    f.box(410, 120, 80, 36, "WDT", None, size=12)
    f.line(380, 138, 410, 138, ACC, 2, arrow="endA")
    for i, nm in enumerate(["sensor", "control", "logger"]):
        f.box(290, 190 + i * 34, 90, 28, nm, None, fill="url(#hatch)" if nm == "control" else "#fff", size=11, weight=400)
    f.text(395, 232, "It still gets CPU", 11, 700, fill="#b00020"); f.text(395, 248, "→ keeps feeding.", 11, 700, fill="#b00020")
    # panel3
    for i, nm in enumerate(["sensor", "control", "logger"]):
        f.box(530, 70 + i * 34, 80, 28, nm, None, fill="url(#hatch)" if nm == "control" else "#fff", size=11, weight=400)
        f.line(610, 84 + i * 34, 640, 120 if i == 0 else (130 if i == 1 else 140), ACC if nm != "control" else "#b00020", 1.6, arrow="endA" if nm != "control" else None, dash=None if nm != "control" else "3 3")
    f.box(640, 110, 90, 40, "Supervisor", "all 3 in?", fill=ACC_L, stroke=ACC, size=11)
    f.line(685, 150, 685, 190, "#b00020", 2, arrow="end", dash="5 3")
    f.box(640, 190, 90, 36, "WDT", None, size=12)
    f.text(520, 270, "control missing → no feed", 11.5, 800, fill=ACC)
    f.text(520, 288, "→ reset; saved note says who.", 11.5, 800, fill=ACC)
    return f.render()


def memory_map():
    f = Fig(760, 320, "Where memory goes (RAM of a small system)", "A vertical bar of RAM from low to high addresses: static data, heap with task stacks and queues allocated at startup, free space reserved, and the main stack. Task stacks sit inside the heap in FreeRTOS.", "mm")
    parts = [("main stack (before the scheduler starts)", 36, "#fff"), ("heap: tasks' stacks + TCBs + queues + buffers", 140, "url(#dots)"), ("   ↑ must be sized so it never runs out; all allocated at start-up", 0, None), ("static: .data (initialised) + .bss (zeroed)", 60, GRAY2), (".noinit (survives a reset: post-mortem notes)", 28, ACC_L)]
    x, y, w = 40, 20, 330
    for (a, h, fl) in parts:
        if h:
            f.rect(x, y, w, h, fl, INK, 1.6)
            f.rect(x + 8, y + h / 2 - 11, w - 16, 22, "#fff", INK, 1) if fl.startswith("url") else None
            f.text(x + w / 2, y + h / 2 + 5, a, 12, 700, "middle")
            y += h
    f.text(x, y + 18, "high address ↑ (top)  …  low address ↓ (bottom)", 11, 400, fill=SOFT)
    notes = ["Stack: per task, fixed size at creation.", "  Overflow corrupts the neighbour first (R6).", "Heap: fragmentation can fail an allocation", "  with plenty of total free space (R6).", "Static: sizes known at link time — preferred.", "Rule (Holzmann): no allocation after initialization.", "Measure: high-water marks, min-ever-free heap."]
    for i, t in enumerate(notes):
        f.text(400, 50 + i * 24, t, 12, 700 if not t.startswith(" ") else 400)
    return f.render()


def distributed():
    f = Fig(760, 300, "Beyond one CPU", "Three nodes connected by a shared bus. Each has its own clock and its own scheduler. Messages cross the bus with arbitration delay and may be lost or delayed. A timeline shows two clocks drifting apart.", "dist")
    for i, nm in enumerate(["Node A (sensor)", "Node B (control)", "Node C (actuator)"]):
        x = 30 + i * 240
        f.box(x, 30, 200, 70, nm, "own clock · own scheduler", fill="#fff")
        f.line(x + 100, 100, x + 100, 140, INK, 1.8)
    f.rect(30, 140, 680, 24, GRAY2, INK, 1.6, 4)
    f.text(370, 157, "shared bus (e.g. CAN: lowest ID wins arbitration; a frame in flight cannot be preempted)", 12, 700, "middle")
    f.text(30, 200, "New questions that a single CPU never asked:", 13, 800)
    qs = ["Whose clock is 'now'?   Drift, offset, sync protocol (PTP / gPTP), leap seconds.",
          "What is the worst-case delay on the bus?   Priority + blocking by the frame in flight (CAN).",
          "What if a node is silent?   Heartbeats / liveliness with a lease; who decides it is dead?",
          "What order did things happen in?   Timestamps from different clocks are not comparable without sync (Lamport 1978)."]
    for i, q in enumerate(qs):
        f.text(44, 224 + i * 20, "•  " + q, 12, 400)
    return f.render()


def cover():
    f = Fig(612, 300, "Cover graphic", "Periodic task pulses on three rows with deadline markers, one pulse late and highlighted.", "cover")
    import random
    random.seed(3)
    rows = [(4, 1.0, 0), (6, 1.6, 1), (12, 3.0, 2)]
    px = 22
    for (T, C, r) in rows:
        y = 40 + r * 70
        f.line(30, y + 44, 590, y + 44, "#999", 1.2)
        t = 0
        while t * px + 30 < 585:
            x = 30 + t * px
            f.rect(x, y + 4, C * px, 40, ACC if r == 2 else INK, "none", 0)
            f.line(x, y - 8, x, y + 4, INK, 1.6)
            t += T
    f.rect(30 + 8 * px, 40 + 140 + 4, 3 * px, 40, "#b00020", "none", 0)
    return f.render()


def recon_flow():
    f = Fig(760, 330, "First hour in a new RTOS system", "Flowchart: build and run; read the configuration; inventory tasks, interrupts, queues and shared data; compute a timing budget; measure; then choose build, debug or understand.", "rf")
    steps = [("1  Run it", ["build, flash or", "emulate; read", "the log"]), ("2  Read config", ["tick, priorities,", "heap, hooks,", "asserts"]), ("3  Inventory", ["tasks, ISRs,", "queues, shared", "data"]),
             ("4  Budget", ["period, deadline,", "budget, CPU", "load per task"]), ("5  Measure", ["trace, counters,", "high-water", "marks"])]
    x = 12
    for i, (a_, lines) in enumerate(steps):
        f.rect(x, 30, 138, 100, ACC_L if i in (2, 3) else "#fff", ACC if i in (2, 3) else INK, 1.8, 4)
        f.text(x + 69, 55, a_, 13, 800, "middle")
        f.lines(x + 69, 77, lines, 11.5, 1.3, 400, "middle", SOFT)
        if i < 4:
            f.line(x + 138, 80, x + 148, 80, INK, 1.8, arrow="end")
        x += 148
    f.text(12, 170, "Gates between steps:", 13, 800)
    gates = ["After 2: can you state the scheduler policy, tick rate and number of priority levels?",
             "After 3: does every task have a trigger or period, a priority, a stack size and an owner?",
             "After 4: does every periodic component have a deadline and an estimated or measured budget?",
             "After 5: do you have one number per requirement (p99.9, max, drops, misses) — not an average?"]
    for i, g in enumerate(gates):
        f.text(26, 194 + i * 22, "▪  " + g, 12, 400)
    f.line(12, 288, 748, 288, "#ccc", 1)
    f.text(12, 310, "Then branch:   BUILD → component card   ·   DEBUG → symptom triage   ·   UNDERSTAND → trace one message end to end", 12, 700, fill=ACC)
    return f.render()


def triage():
    f = Fig(760, 360, "Symptom to first probe", "A table-like decision chart: for each symptom, the first suspicion and the first probe. Missed deadline: check budget and priorities with trace. Hang: check blocked tasks and watchdog. Reset loop: read reset reason. Wrong data: check shared state. Data loss: check queue drop counters.", "tri")
    rows = [("Missed deadline / jitter", "overrun, preemption, ISR load, inversion", "trace the window; compare R to budget"),
            ("System alive, one function dead", "task blocked forever (lock, queue)", "list tasks + what each waits on"),
            ("Resets / reboot loop", "watchdog, fault, boot-time resource", "read reset reason + saved post-mortem"),
            ("Wrong or inconsistent values", "race on shared state, stale data", "invariant check; watch the variable"),
            ("Messages missing / late", "queue full, consumer starved, QoS", "drop counters, queue depth, age stamps"),
            ("Slowly gets worse over hours", "leak, fragmentation, counter wrap, drift", "min-ever-free heap, high-water marks, uptime math"),
            ("Works in debug, fails in release", "timing/optimisation, uninitialised data", "trace instead of breakpoints; build flags diff")]
    f.rect(10, 10, 740, 30, INK, INK, 1, 4)
    f.text(20, 30, "Symptom", 12.5, 800, fill="#fff"); f.text(260, 30, "First suspicion", 12.5, 800, fill="#fff"); f.text(500, 30, "First probe", 12.5, 800, fill="#fff")
    for i, (a, b, c) in enumerate(rows):
        y = 40 + i * 44
        f.rect(10, y, 740, 44, "#fff" if i % 2 == 0 else GRAY1, "#999", 1)
        f.text(20, y + 27, a, 12.5, 800)
        f.text(260, y + 27, b, 12, 400)
        f.text(500, y + 27, c, 12, 700, fill=ACC)
    return f.render()


ALL = [("pubsub", pubsub), ("e2e-chain", e2e_chain), ("lifecycle", lifecycle), ("msg-lifecycle", msg_lifecycle), ("watchdog-designs", watchdog),
       ("memory-map", memory_map), ("distributed", distributed), ("cover-art", cover), ("recon-flow", recon_flow), ("triage", triage)]
