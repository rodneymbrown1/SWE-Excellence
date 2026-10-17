#!/usr/bin/env python3
"""trace2gantt -- turn a lab's trace dump into a timeline you can read.

The labs print lines like
    N 2 bus_dist          (task number -> name)
    T 123456 1 2 0        (time_us type id arg)     type 1 = task switched in, 3 = ISR, 4 = marker
Usage:
    python3 tools/trace2gantt.py run.txt [--from MS] [--to MS] [--scale US_PER_CHAR]
    python3 run.py ... | python3 tools/trace2gantt.py - --from 0 --to 120

Output: one row per task ('#' running), a row for interrupts ('!'), markers ('^'), and per-task CPU share.
"""
import argparse, sys, collections

ap = argparse.ArgumentParser()
ap.add_argument("file")
ap.add_argument("--from", dest="t0", type=float, default=None, help="start (ms since first event)")
ap.add_argument("--to", dest="t1", type=float, default=None, help="end (ms since first event)")
ap.add_argument("--scale", type=int, default=1000, help="microseconds per character (default 1000)")
ap.add_argument("--width", type=int, default=120)
a = ap.parse_args()

names = {0: "idle/other"}
ev = []
for line in (sys.stdin if a.file == "-" else open(a.file)):
    f = line.split()
    if not f:
        continue
    if f[0] == "N" and len(f) >= 3:
        names[int(f[1])] = f[2]
    elif f[0] == "T" and len(f) >= 5:
        ev.append((int(f[1]), int(f[2]), int(f[3]), int(f[4])))
if not ev:
    sys.exit("no trace events found")
# unwrap the 32-bit microsecond clock
base, last, out = ev[0][0], ev[0][0], []
off = 0
for t, ty, i, arg in ev:
    if t < last - 2**31:
        off += 2**32
    last = t
    out.append((t + off - base, ty, i, arg))
ev = out
lo = int((a.t0 or 0) * 1000)
hi = int((a.t1 if a.t1 is not None else ev[-1][0] / 1000.0) * 1000)
sw = [(t, i) for t, ty, i, arg in ev if ty == 1]
cols = min(a.width, max(1, (hi - lo) // a.scale))
scale = max(a.scale, (hi - lo + cols - 1) // cols)
rows = collections.OrderedDict()
for k in sorted(names):
    rows[k] = [" "] * cols
irq = [" "] * cols
cpu = collections.Counter()
for n, (t, i) in enumerate(sw):
    end = sw[n + 1][0] if n + 1 < len(sw) else hi
    cpu[i] += max(0, min(end, hi) - max(t, lo))
    s, e = max(t, lo), min(end, hi)
    for c in range((s - lo) // scale, (e - lo + scale - 1) // scale):
        if 0 <= c < cols:
            rows.setdefault(i, [" "] * cols)[c] = "#"
for t, ty, i, arg in ev:
    if lo <= t < hi and 0 <= (t - lo) // scale < cols:
        if ty == 3:
            irq[(t - lo) // scale] = "!"
        elif ty == 4:
            irq[(t - lo) // scale] = "^"
lab = max(len(v) for v in names.values()) + 1
ruler = "".join("|" if ((lo + c * scale) // 1000) % 10 == 0 and (lo + c * scale) % 1000 < scale else " " for c in range(cols))
print("window %.1f..%.1f ms, 1 char = %d us" % (lo / 1000, hi / 1000, scale))
print(" " * lab + ruler)
for k, row in rows.items():
    if any(ch != " " for ch in row) or k in names:
        print(names.get(k, "task%d" % k).ljust(lab) + "".join(row))
if any(ch != " " for ch in irq):
    print("irq/mark".ljust(lab) + "".join(irq))
tot = sum(cpu.values()) or 1
print("\nCPU share in window: " + "  ".join("%s %.1f%%" % (names.get(k, k), 100.0 * v / tot) for k, v in sorted(cpu.items(), key=lambda kv: -kv[1])))
print("context switches in window: %d" % sum(1 for t, i in sw if lo <= t < hi))
