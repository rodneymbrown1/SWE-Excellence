#!/usr/bin/env python3
"""rtcalc -- schedulability calculator.  Give it your tasks, get the answers the handbook asks for.

    python3 rtcalc.py NAME:C:T[:D[:B]] ...   [--edf] [--gantt N]

      C = worst-case execution time (budget)      T = period or minimum inter-arrival
      D = deadline (default T)                    B = blocking time from lower-priority tasks (default 0)
      All in the same unit (e.g. ms).  Priorities are assigned rate-monotonically (shortest period highest);
      list a task first to break ties in its favour.

Examples
    python3 rtcalc.py sense:1:10 filter:3:20 control:4:40 log:10:100
    python3 rtcalc.py a:2:5 b:4:7 --edf
"""
import sys

from rtsim import (Task, ascii_gantt, hyperbolic_ok, hyperperiod, is_harmonic, ll_bound, rate_monotonic, rta,
                   simulate, summary, utilization)


def parse(args):
    tasks, blocking = [], {}
    for a in args:
        f = a.split(":")
        name, C, T = f[0], int(f[1]), int(f[2])
        D = int(f[3]) if len(f) > 3 and f[3] else None
        tasks.append(Task(name, C, T, D))
        if len(f) > 4:
            blocking[name] = int(f[4])
    return tasks, blocking


def main(argv):
    flags = [a for a in argv if a.startswith("--")]
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    gantt_w = None
    if "--gantt" in argv:
        i = argv.index("--gantt")
        gantt_w = int(argv[i + 1])
        args = [a for a in args if a != argv[i + 1]]
    tasks, blocking = parse(args)
    rate_monotonic(tasks)
    n = len(tasks)
    U = utilization(tasks)
    print("tasks: %d   utilization U = %.3f   hyperperiod = %d" % (n, U, hyperperiod(tasks)))
    print("Liu-Layland bound for n=%d: %.3f   -> %s" % (n, ll_bound(n), "U <= bound: schedulable under RM (sufficient test)" if U <= ll_bound(n) else "U > bound: inconclusive, run exact analysis"))
    print("hyperbolic bound (prod(U_i+1) <= 2): %s     harmonic periods: %s" % ("passes" if hyperbolic_ok(tasks) else "fails", "yes (RM bound is 1.0)" if is_harmonic(tasks) else "no"))
    if U > 1:
        print("U > 1: overloaded; no scheduler can meet every deadline.")
    print("\nResponse-time analysis (fixed priority, rate-monotonic):")
    res = rta(tasks, blocking=blocking)
    print("task   prio     C     T     D     B   R(worst)  slack  ok?")
    for t in sorted(tasks, key=lambda t: -t.prio):
        R, ok = res[t.name]
        print("%-6s %4d %5d %5d %5d %5d %9s %6s  %s" % (t.name, t.prio, t.C, t.T, t.D, blocking.get(t.name, 0),
              "-" if R is None else R, "-" if R is None else t.D - R, "yes" if ok else "NO"))
    pol = "EDF" if "--edf" in flags else "FP"
    horizon = hyperperiod(tasks) if hyperperiod(tasks) <= 400 else 400
    sim = simulate(tasks, horizon, pol)
    print("\nSimulation (%s, critical instant at t=0, %d ticks): deadline misses = %d" % (pol, horizon, len(sim.misses())))
    print(summary(sim))
    w = gantt_w or min(horizon, 100)
    print("\n" + ascii_gantt(sim, width=w))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
