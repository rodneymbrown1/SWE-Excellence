#!/usr/bin/env python3
"""Lab H3: the scheduler workbench -- four guided demonstrations.  Run one with its number, or all.

    python3 h3_demos.py 1      U above the Liu-Layland bound, still schedulable (RTA proves it)
    python3 h3_demos.py 2      RM misses, EDF does not  (U = 0.97)
    python3 h3_demos.py 3      transient overload: who misses? (Buttazzo 2005 counterexample)  + permanent overload
    python3 h3_demos.py 4      priority inversion (Pathfinder-shaped) with no protocol / inheritance / ceiling
"""
import sys

from rtsim import (Task, ascii_gantt, hyperperiod, ll_bound, rate_monotonic, rta, simulate, summary, utilization)


def demo1():
    print("== 1. U above the bound, still schedulable ==")
    ts = rate_monotonic([Task("t1", 1, 4), Task("t2", 2, 6), Task("t3", 3, 12)])
    print("U = %.3f   LL bound(3) = %.3f  -> the bound test is inconclusive" % (utilization(ts), ll_bound(3)))
    print("RTA:", {k: v for k, v in rta(ts).items()})
    r = simulate(ts, hyperperiod(ts))
    print("simulation over one hyperperiod: misses =", len(r.misses()))
    print(ascii_gantt(r))


def demo2():
    print("== 2. Rate-monotonic misses, EDF does not ==")
    ts = rate_monotonic([Task("t1", 2, 5), Task("t2", 4, 7)])
    print("U = %.3f  (< 1, so EDF can schedule it; > LL bound(2) = %.3f)" % (utilization(ts), ll_bound(2)))
    print("RTA:", rta(ts))
    for pol in ("FP", "EDF"):
        r = simulate(ts, hyperperiod(ts), pol)
        print("\n%s: misses = %s" % (pol, [(j.task.name, "job %d" % j.index, "deadline %d" % j.deadline, "finished %s" % j.finish) for j in r.misses()]))
        print(ascii_gantt(r, width=36))


def demo3():
    print("== 3a. Transient overload (Buttazzo 2005, Fig. 9; times doubled so 1.5 becomes 3) ==")

    def mk(over):
        return rate_monotonic([Task("t1", 4, 10, overrun={0: 3, 1: 3} if over else {}), Task("t2", 6, 18), Task("t3", 2, 40), Task("t4", 2, 60)])
    n = mk(False)
    print("normal: U = %.3f  RTA ok = %s" % (utilization(n), all(ok for _, ok in rta(n).values())))
    o = mk(True)
    r = simulate(o, hyperperiod(o))
    print("with the overrun in t1 jobs 0 and 1, the tasks that miss are:", sorted({j.task.name for j in r.misses()}),
          "  <- NOT the longest-period task t4")
    print(ascii_gantt(r, width=70))
    print("\n== 3b. Permanent overload, U = 1.25 (Buttazzo: C=(4,6,5), T=(8,12,20)); jobs COMPLETED in 120 ticks ==")
    p = rate_monotonic([Task("a", 4, 8), Task("b", 6, 12), Task("c", 5, 20)])
    for pol in ("FP", "EDF"):
        rr = simulate(p, 120, pol)
        done = {t.name: sum(1 for j in rr.jobs_of(t.name) if j.finish is not None) for t in p}
        print("%-3s %s" % (pol, done))
    print("Under fixed priority the lowest-priority task starves; EDF slows every task by the same factor U.")


def demo4():
    print("== 4. Priority inversion: H needs a lock that L holds, M is CPU-bound in between ==")

    def mk():
        H = Task("H", segments=[("run", 1), ("lock", "R"), ("run", 2), ("unlock", "R"), ("run", 1)], T=50, offset=5)
        M = Task("M", 40, 100, offset=6)
        L = Task("L", segments=[("run", 2), ("lock", "R"), ("run", 10), ("unlock", "R"), ("run", 2)], T=200)
        return rate_monotonic([H, M, L])
    for proto in ("none", "inherit", "ceiling"):
        r = simulate(mk(), 100, "FP", proto)
        h = r.jobs_of("H")[0]
        print("\nprotocol = %-8s  H released at %d, finished at %s, response = %s (deadline %d) -> %s" % (
            proto, h.release, h.finish, h.response, h.D if hasattr(h, 'D') else h.deadline - h.release,
            "MISS" if h.missed else "ok"))
        print(ascii_gantt(r, width=70))
    print("\nlegend: '#' running   '.' ready (preempted or waiting for CPU)   'b' blocked on the lock")


DEMOS = {"1": demo1, "2": demo2, "3": demo3, "4": demo4}

if __name__ == "__main__":
    which = sys.argv[1:] or sorted(DEMOS)
    for w in which:
        DEMOS[w]()
        print()
