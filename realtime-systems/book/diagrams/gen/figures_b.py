"""Figures part B: drawn from real simulator output and real QEMU transcripts, plus Parts 3-6 concept diagrams."""
import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "labs", "host"))
from svgkit import *
import rtsim
from rtsim import Task, rate_monotonic, simulate, hyperperiod

TR = os.path.join(ROOT, "labs", "transcripts")


# ------------------------------------------------------------------ simulator Gantt charts
def g_rm_setA():
    ts = rate_monotonic([Task("t1", 1, 4), Task("t2", 2, 6), Task("t3", 3, 12)])
    r = simulate(ts, 24)
    return gantt(r, "gA", "Rate-monotonic schedule of three tasks", "Gantt chart over 24 ms of tasks t1 (1 ms every 4), t2 (2 ms every 6) and t3 (3 ms every 12). t3 is preempted repeatedly and finishes at 10 ms of each 12 ms period, before its deadline.", px=26, label_w=44)


def g_setB_pair():
    out = []
    ts = rate_monotonic([Task("t1", 2, 5), Task("t2", 4, 7)])
    r = simulate(ts, 35, "FP")
    out.append(gantt(r, "gB1", "Fixed priority (rate-monotonic) on a set with U = 0.97", "Gantt chart over 35 ms. With rate-monotonic priorities t2 misses its deadline once per hyperperiod (X).", px=20, label_w=44))
    r2 = simulate(ts, 35, "EDF")
    out.append(gantt(r2, "gB2", "EDF on the same set", "The same two tasks scheduled earliest-deadline-first. No deadline is missed.", px=20, label_w=44))
    return out


def g_overload():
    def mk(over):
        return rate_monotonic([Task("t1", 4, 10, overrun={0: 3, 1: 3} if over else {}), Task("t2", 6, 18), Task("t3", 2, 40), Task("t4", 2, 60)])
    o = mk(True)
    r = simulate(o, 60)
    return gantt(r, "gO", "Transient overload under rate-monotonic scheduling (Buttazzo 2005 counterexample)", "Gantt chart over 60 half-milliseconds. Task t1 overruns in its first two jobs. The task that misses its deadline is t2, not the longest-period task t4.", px=12, label_w=44, show_axis_every=10, extra_note="(time unit = 0.5 ms)")


def _pf():
    H = Task("H", segments=[("run", 1), ("lock", "R"), ("run", 2), ("unlock", "R"), ("run", 1)], T=50, offset=5)
    M = Task("M", 40, 100, offset=6)
    L = Task("L", segments=[("run", 2), ("lock", "R"), ("run", 10), ("unlock", "R"), ("run", 2)], T=200)
    return rate_monotonic([H, M, L])


def g_inversion():
    outs = {}
    desc = {"none": "Without any protocol: H blocks on the lock at 6 ms, M (medium priority) runs for 40 ms, and L cannot finish its critical section; H finishes at 56 ms, past its 55 ms deadline.",
            "inherit": "With priority inheritance: when H blocks, L runs at H's priority, finishes the critical section at 13 ms and H completes at 16 ms.",
            "ceiling": "With an immediate priority ceiling: L runs at the ceiling priority while it holds the lock; H waits for the CPU, not for the lock, and completes at 16 ms."}
    for proto in ("none", "inherit", "ceiling"):
        r = simulate(_pf(), 62, "FP", proto)
        outs[proto] = gantt(r, "gI" + proto, "Priority inversion, protocol: " + proto, desc[proto], t1=62, px=11.2, label_w=30, show_axis_every=10)
    return outs


# ------------------------------------------------------------------ real QEMU trace -> Gantt
def read_trace(path):
    names, ev = {0: "idle"}, []
    for line in open(path):
        f = line.split()
        if not f:
            continue
        if f[0] == "N":
            names[int(f[1])] = f[2]
        elif f[0] == "T" and len(f) >= 5:
            ev.append((int(f[1]), int(f[2]), int(f[3])))
    if not ev:
        return names, [], []
    base = ev[0][0]
    sw = [((t - base) / 1000.0, i) for t, ty, i in ev if ty == 1]
    irq = [((t - base) / 1000.0) for t, ty, i in ev if ty == 3]
    return names, sw, irq


def trace_gantt(path, uid, title, desc, t0, t1, px, order=None, label_w=80):
    names, sw, irq = read_trace(path)
    ids = order or sorted(i for i in names if i != 0) + [0]
    n = len(ids)
    W = int(label_w + (t1 - t0) * px + 20)
    top = 26
    row_h = 30
    f = Fig(W, top + n * row_h + 40, title, desc, uid)
    step = 5 if (t1 - t0) <= 130 else 10
    for t in range(int(t0), int(t1) + 1):
        if (t - t0) % step == 0:
            x = label_w + (t - t0) * px
            f.line(x, top - 6, x, top + n * row_h, "#ccc", 0.8)
            f.text(x, top - 10, str(t), 11, 400, "middle", SOFT)
    for r, i in enumerate(ids):
        y = top + r * row_h
        f.text(label_w - 8, y + 19, names.get(i, "task%d" % i), 12.5, 700, "end")
        f.line(label_w, y + row_h - 2, label_w + (t1 - t0) * px, y + row_h - 2, "#e5e5e5", 0.8)
    for k, (t, i) in enumerate(sw):
        end = sw[k + 1][0] if k + 1 < len(sw) else t1
        a, b = max(t, t0), min(end, t1)
        if b > a and i in ids:
            y = top + ids.index(i) * row_h
            f.rect(label_w + (a - t0) * px, y + 5, max(b - a, 0.2) * px, row_h - 10, GRAY3 if i == 0 else INK, "none", 0)
    for t in irq:
        if t0 <= t <= t1:
            x = label_w + (t - t0) * px
            f.line(x, top + n * row_h + 2, x, top + n * row_h + 12, ACC, 2)
    f.text(label_w, top + n * row_h + 30, "ms since trace start · bars = which task the CPU is running · teal ticks = interrupts" if irq else "ms since trace start · bars = which task the CPU is running", 10.5, 400, fill=SOFT)
    return f.render()


def g_trace_inversion():
    p1 = os.path.join(TR, "r3_trace_phase1.raw")
    p2 = os.path.join(TR, "r3_trace_phase2.raw")
    order = [1, 2, 3, 4, 0]
    a = trace_gantt(p1, "gT1", "Real trace, phase 1: binary semaphore", "Context-switch trace from the FreeRTOS lab on QEMU over the first 70 ms. met runs first, bus_dist runs briefly and blocks, comms runs for 40 ms, then met finishes and bus_dist runs at about 55 ms, too late.", 0, 70, 9.4, order)
    b = trace_gantt(p2, "gT2", "Real trace, phase 2: mutex with priority inheritance", "The same trace with a mutex. met finishes its critical section at about 13 ms because it inherited bus_dist's priority; bus_dist completes at about 16 ms and comms runs afterwards.", 0, 70, 9.4, order)
    return a, b


def g_trace_r8():
    return trace_gantt(os.path.join(TR, "r8_trace.raw"), "gT8", "Real trace: three periodic tasks and a 2 ms interrupt", "Context-switch trace of tasks t1, t2 and t3 with interrupts every 2 ms (teal ticks) over 36 ms; t1 runs every 4 ms, t2 every 6 ms and t3 fills the gaps.", 0, 36, 18, [1, 2, 3, 0], 60)


def g_trace_r10():
    return trace_gantt(os.path.join(TR, "r10_trace.raw"), "gT10", "Real trace of the capstone pipeline (baseline)", "Context-switch trace over 80 ms. The filter task runs steadily except for a 3 ms gap in which the logger, which has the highest priority, runs; samples queue up during that gap.", 0, 80, 8.6, [4, 3, 1, 2, 0], 74)


# ------------------------------------------------------------------ data figures
def g_queue_depth():
    sys.path.insert(0, os.path.join(ROOT, "labs", "host"))
    import h4_queue as h
    tr = []
    h.run(32, "drop_newest", tr)
    # take second 1 (t in [1.0, 1.4])
    pts = [(t, d) for t, d in tr if 0.99 <= t <= 1.34]
    W, H = 760, 300
    f = Fig(W, H, "Queue depth during a burst", "Line chart of items in the system over 350 milliseconds: steady at 0 to 2, then a burst of 20 messages in 20 ms raises it to 20, and it drains at 200 messages per second over about 100 ms. Horizontal lines mark queue capacities 4 and 19.", "qd")
    ox, oy, w, hh = 60, 20, 660, 220
    t0, t1 = 0.99, 1.34
    X = lambda t: ox + (t - t0) / (t1 - t0) * w
    Y = lambda d: oy + hh - d / 22.0 * hh
    f.rect(ox, oy, w, hh, "#fff", INK, 1.4)
    for d in (0, 5, 10, 15, 20):
        f.line(ox, Y(d), ox + w, Y(d), "#e0e0e0", 0.8)
        f.text(ox - 8, Y(d) + 4, str(d), 11.5, 400, "end")
    f.line(ox, Y(19), ox + w, Y(19), ACC, 2, dash="7 4"); f.text(ox + w - 4, Y(19) - 5, "capacity 19: nothing lost", 11.5, 700, "end", ACC)
    f.line(ox, Y(4), ox + w, Y(4), "#b00020", 2, dash="7 4"); f.text(ox + w - 4, Y(4) - 5, "capacity 4: everything above is dropped", 11.5, 700, "end", "#b00020")
    # step line
    d = "M%.1f %.1f" % (X(pts[0][0]), Y(pts[0][1]))
    for (t, v) in pts[1:]:
        d += " L%.1f %.1f" % (X(t), Y(v))
    f.path(d, "none", INK, 2.2)
    for k in range(0, 8):
        tt = t0 + k * 0.05
        f.text(X(tt), oy + hh + 18, "%d" % round((tt - t0) * 1000), 11.5, 400, "middle")
    f.text(ox + w / 2, oy + hh + 38, "milliseconds", 12, 700, "middle")
    f.text(24, oy + hh / 2, "items in system", 12, 700, "middle", rotate=-90)
    f.text(ox, H - 8, "Host simulation (lab H4): 100 msg/s steady + a 20-message burst at 1000 msg/s; consumer 5 ms per message (200 msg/s).", 10.5, 400, fill=SOFT)
    return f.render()


def g_apollo():
    sys.path.insert(0, os.path.join(ROOT, "labs", "host"))
    import h4_queue as h
    W, H = 760, 330
    f = Fig(W, H, "A fixed pool and a steady deficit (toy model)", "Three charts of outstanding jobs over 800 seconds against a limit of 8. With the job fitting there are no alarms; with a small deficit the count climbs to 8 once; with a larger deficit it climbs and resets repeatedly.", "ap")
    ox, w = 70, 650
    labels = [(0.40, "load 0.40: job fits — 0 alarms"), (0.52, "load 0.52: small deficit — 1 alarm"), (0.62, "load 0.62: larger deficit — 11 alarms")]
    for r, (hp, lab) in enumerate(labels):
        alarms, hist = h.apollo_run(hp)
        oy = 30 + r * 100
        hh = 66
        X = lambda k: ox + k / len(hist) * w
        Y = lambda j: oy + hh - j / 9.0 * hh
        f.rect(ox, oy, w, hh, "#fff", INK, 1.2)
        f.line(ox, Y(8), ox + w, Y(8), "#b00020", 1.4, dash="5 3")
        d = "M%.1f %.1f" % (X(0), Y(hist[0]))
        for k, j in enumerate(hist):
            d += " L%.1f %.1f" % (X(k), Y(j))
        f.path(d, "none", INK, 1.8)
        for a in alarms:
            f.text(ox + a / (2.0 * len(hist)) * w, oy + 11, "▼", 10, 800, "middle", "#b00020")
        f.text(ox, oy - 5, lab, 12, 700)
        f.text(ox - 8, Y(8) + 4, "8", 11, 400, "end", "#b00020")
        f.text(ox - 8, Y(1) + 4, "1", 11, 400, "end")
    f.text(ox + w / 2, 318, "time (seconds, 0–800)", 11.5, 700, "middle")
    f.text(24, 150, "outstanding jobs", 11.5, 700, "middle", rotate=-90)
    f.text(ox, 330, "", 1)
    return f.render()


def g_hist():
    """latency histograms from the R10 dumps (baseline vs fixed)."""
    def load(p):
        return sorted(float(l.split()[1]) for l in open(p) if l.startswith("L "))
    base = load(os.path.join(TR, "r10_dump.raw"))
    fix = load(os.path.join(TR, "r10_dump_fixed.raw"))
    edges = [0, 500, 1000, 1500, 2000, 3000, 4000, 5000, 7500, 10000]
    labs = ["<0.5", "0.5–1", "1–1.5", "1.5–2", "2–3", "3–4", "4–5", "5–7.5", "7.5–10"]
    def counts(xs):
        c = [0] * (len(edges) - 1)
        for x in xs:
            for i in range(len(edges) - 1):
                if edges[i] <= x < edges[i + 1]:
                    c[i] += 1
                    break
        return c
    cb, cf = counts(base), counts(fix)
    W, H = 760, 330
    f = Fig(W, H, "Latency histogram, before and after the fixes (log scale)", "Bar chart on a logarithmic count axis of estimate latency in milliseconds. The baseline has a long tail out to 10 ms; after four fixes everything is under 1 ms. A line marks the 3 ms requirement.", "hi")
    ox, oy, w, hh = 70, 20, 650, 220
    import math
    Y = lambda c: oy + hh - (math.log10(c) / 3.6) * hh if c > 0 else oy + hh
    f.rect(ox, oy, w, hh, "#fff", INK, 1.4)
    for c in (1, 10, 100, 1000):
        f.line(ox, Y(c), ox + w, Y(c), "#e0e0e0", 0.8); f.text(ox - 8, Y(c) + 4, str(c), 11.5, 400, "end")
    bw = w / len(cb)
    for i in range(len(cb)):
        x = ox + i * bw
        if cb[i]:
            f.rect(x + 6, Y(cb[i]), bw / 2 - 8, oy + hh - Y(cb[i]), "#fff", INK, 1.6)
            f.text(x + 6 + (bw / 2 - 8) / 2, Y(cb[i]) - 4, str(cb[i]), 10.5, 700, "middle")
        if cf[i]:
            f.rect(x + bw / 2, Y(cf[i]), bw / 2 - 8, oy + hh - Y(cf[i]), ACC, ACC, 1.6)
            f.text(x + bw / 2 + (bw / 2 - 8) / 2, Y(cf[i]) - 4, str(cf[i]), 10.5, 700, "middle", ACC)
        f.text(x + bw / 2, oy + hh + 18, labs[i], 11, 400, "middle")
    xr = ox + 4 * bw + 0
    f.line(ox + 5 * bw - 0.0, oy, ox + 5 * bw, oy + hh, "#b00020", 2, dash="6 4"); f.text(ox + 5 * bw + 5, oy + 14, "3 ms requirement", 11.5, 800, fill="#b00020")
    f.text(ox + w / 2, oy + hh + 38, "latency, IMU interrupt → estimate published (ms)", 12, 700, "middle")
    f.rect(ox + 395, oy + 36, 14, 12, "#fff", INK, 1.6); f.text(ox + 415, oy + 47, "baseline (p99.9 = 9.5 ms)", 11.5)
    f.rect(ox + 395, oy + 56, 14, 12, ACC, ACC, 1); f.text(ox + 415, oy + 67, "after fixes (p99.9 = 0.63 ms)", 11.5, fill=ACC)
    f.text(ox, H - 6, "Real data: labs/transcripts/r10_dump*.raw (3000 samples each, lab R10 on QEMU).", 10.5, 400, fill=SOFT)
    return f.render()


def g_co():
    """coordinated omission: closed vs open loop percentiles (values from lab H5 transcript)."""
    rows = []
    for line in open(os.path.join(TR, "h5_latency.txt")):
        m = re.match(r"^(closed-loop \(as reported\)|closed-loop \+ correction|open-loop \(ground truth\))\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(\d+)", line)
        if m:
            rows.append((m.group(1), float(m.group(4)), float(m.group(5)), float(m.group(7))))
    W, H = 760, 270
    f = Fig(W, H, "The same system, three reported tail latencies", "Grouped bars for p99 and max latency in milliseconds. The closed-loop tester reports p99 of 1.4 ms; the open-loop ground truth is 4,483 ms.", "co")
    ox, oy, w, hh = 250, 20, 470, 170
    import math
    X = lambda v: ox + (math.log10(max(v, 1)) / 3.9) * w
    f.rect(ox, oy, w, hh, "#fff", INK, 1.4)
    for v in (1, 10, 100, 1000):
        f.line(X(v), oy, X(v), oy + hh, "#e0e0e0", 0.8); f.text(X(v), oy + hh + 16, str(v), 11.5, 400, "middle")
    for i, (nm, p99, p999, mx) in enumerate(rows):
        y = oy + 14 + i * 52
        f.text(ox - 10, y + 22, nm, 12, 700, "end")
        f.rect(ox, y, X(p99) - ox, 18, ACC if "open" in nm else "#fff", INK, 1.6)
        if X(p99) - ox > 150:
            f.rect(ox + 6, y + 2, 132, 14, "#fff", "none", 0); f.text(ox + 10, y + 14, "p99 = %.1f ms" % p99, 11.5, 700, fill=INK)
        else:
            f.text(X(p99) + 6, y + 14, "p99 = %.1f ms" % p99, 11.5, 700)
        f.rect(ox, y + 22, X(mx) - ox, 14, GRAY3, INK, 1.2)
        f.text(X(mx) - 6, y + 33, "max %d ms" % mx, 10.5, 700, "end", INK)
    f.text(ox + w / 2, oy + hh + 36, "latency (ms, log scale)", 12, 700, "middle")
    f.text(20, H - 6, "Real run of lab H5: one 5-second stall in a 60-second test at 100 requests/s.", 10.5, 400, fill=SOFT)
    return f.render()


ALL_SINGLE = [("gantt-rm-seta", g_rm_setA), ("gantt-overload", g_overload), ("queue-depth", g_queue_depth),
              ("apollo-pool", g_apollo), ("latency-hist", g_hist), ("coordinated-omission", g_co), ("trace-r8", g_trace_r8)]
