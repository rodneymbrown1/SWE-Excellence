#!/usr/bin/env python3
"""lathist -- percentile table and histogram from lines "L <microseconds>".

    python3 labs/rtos/run.py labs/rtos/r10_pipeline/build/r10_pipeline.elf | python3 labs/tools/lathist.py - [--limit US]

--limit US : count and report samples above this (the requirement), e.g. --limit 5000
"""
import sys, math

path = sys.argv[1]
limit = None
if "--limit" in sys.argv:
    limit = float(sys.argv[sys.argv.index("--limit") + 1])
xs = []
for line in (sys.stdin if path == "-" else open(path)):
    f = line.split()
    if len(f) == 2 and f[0] == "L":
        xs.append(float(f[1]))
if not xs:
    sys.exit("no 'L <us>' lines found")
xs.sort()
def pct(p): return xs[min(len(xs) - 1, int(p / 100.0 * len(xs)))]
print("samples: %d" % len(xs))
print("min %.0f  p50 %.0f  p90 %.0f  p99 %.0f  p99.9 %.0f  max %.0f   (microseconds)" % (xs[0], pct(50), pct(90), pct(99), pct(99.9), xs[-1]))
if limit is not None:
    over = sum(1 for x in xs if x > limit)
    print("above %.0f us: %d samples (%.2f%%)  ->  requirement %s" % (limit, over, 100.0 * over / len(xs), "MET" if pct(99.9) <= limit else "NOT MET (p99.9 above the limit)"))
edges = [0, 500, 1000, 1500, 2000, 3000, 4000, 5000, 7500, 10000, 1e9]
cnt = [0] * (len(edges) - 1)
for x in xs:
    for i in range(len(edges) - 1):
        if edges[i] <= x < edges[i + 1]:
            cnt[i] += 1
            break
top = max(cnt)
print("\nlatency (us)        count")
for i, c in enumerate(cnt):
    hi = "inf" if edges[i + 1] >= 1e9 else "%d" % edges[i + 1]
    print("%6d - %-6s %8d  %s" % (edges[i], hi, c, "#" * int(50 * c / top) if c else ""))
