"""rtsim — a small, deterministic uniprocessor scheduling workbench.

Time is an integer number of "ticks" (choose your own unit: 1 tick = 1 ms, 0.5 ms, ...).
Fixed-priority preemptive (FP) and Earliest-Deadline-First (EDF), optional shared
resources with three protocols (none / priority inheritance / immediate priority ceiling),
overrun injection, and the analyses used in the book:

    utilization(tasks)            sum C/T
    ll_bound(n)                   Liu & Layland n(2^(1/n) - 1)
    hyperbolic_ok(tasks)          prod(U_i + 1) <= 2           (Bini et al.; sufficient)
    is_harmonic(tasks)            every period divides the next larger one
    hyperperiod(tasks)            lcm of periods
    rta(tasks, blocking=...)      response-time analysis (Audsley et al. 1993)

Run `python3 rtsim.py` for a self-test.  Pure standard library.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from functools import reduce
from typing import Callable, Dict, List, Optional, Tuple

# --------------------------------------------------------------------------- model


@dataclass
class Task:
    name: str
    C: int = 0                      # worst-case execution time (ticks); ignored if `segments` is given
    T: int = 1                      # period / minimum inter-arrival time
    D: Optional[int] = None         # relative deadline, default = T
    offset: int = 0                 # first release
    prio: Optional[int] = None      # higher number = higher priority (assigned by rate_monotonic() if None)
    # Optional detailed behaviour: [("run", n), ("lock", "R"), ("run", n), ("unlock", "R"), ...]
    segments: Optional[List[Tuple[str, object]]] = None
    # Extra ticks added to the last "run" segment of job number k (0-based): {k: extra}
    overrun: Dict[int, int] = field(default_factory=dict)

    def __post_init__(self):
        if self.D is None:
            self.D = self.T
        if self.segments is None:
            self.segments = [("run", self.C)]
        else:
            self.C = sum(n for kind, n in self.segments if kind == "run")

    @property
    def wcet(self) -> int:
        return self.C


@dataclass
class Job:
    task: Task
    index: int
    release: int
    deadline: int
    segs: List[Tuple[str, object]]
    seg_i: int = 0
    remaining: int = 0
    held: List[str] = field(default_factory=list)
    blocked_on: Optional[str] = None
    start: Optional[int] = None
    finish: Optional[int] = None
    aborted: bool = False

    @property
    def response(self) -> Optional[int]:
        return None if self.finish is None else self.finish - self.release

    @property
    def missed(self) -> bool:
        if self.aborted:
            return True
        return self.finish is None or self.finish > self.deadline


@dataclass
class Result:
    horizon: int
    tasks: List[Task]
    timeline: List[Optional[str]]            # task name running at tick t, or None (idle)
    blocked: List[List[str]]                 # task names blocked on a resource at tick t
    holding: List[Optional[str]]             # resource held by the running task at tick t
    jobs: List[Job]
    skipped: Dict[str, int]                  # releases skipped (on_miss="skip_release")

    def jobs_of(self, name: str) -> List[Job]:
        return [j for j in self.jobs if j.task.name == name]

    def max_response(self, name: str) -> Optional[int]:
        rs = [j.response for j in self.jobs_of(name) if j.response is not None]
        return max(rs) if rs else None

    def misses(self, name: Optional[str] = None) -> List[Job]:
        js = self.jobs if name is None else self.jobs_of(name)
        # a job whose deadline lies beyond the horizon and is unfinished is not (yet) a miss
        return [j for j in js if (j.aborted or (j.finish is None and j.deadline <= self.horizon)
                                  or (j.finish is not None and j.finish > j.deadline))]

    def utilization_observed(self) -> float:
        busy = sum(1 for x in self.timeline if x is not None)
        return busy / self.horizon


# --------------------------------------------------------------------------- priorities and bounds


def rate_monotonic(tasks: List[Task]) -> List[Task]:
    """Assign priorities by period: shortest period = highest number. Ties keep list order."""
    order = sorted(range(len(tasks)), key=lambda i: (-tasks[i].T, -i))
    for rank, i in enumerate(order, start=1):
        tasks[i].prio = rank
    return tasks


def deadline_monotonic(tasks: List[Task]) -> List[Task]:
    order = sorted(range(len(tasks)), key=lambda i: (-tasks[i].D, -i))
    for rank, i in enumerate(order, start=1):
        tasks[i].prio = rank
    return tasks


def utilization(tasks: List[Task]) -> float:
    return sum(t.C / t.T for t in tasks)


def ll_bound(n: int) -> float:
    return n * (2 ** (1.0 / n) - 1)


def hyperbolic_ok(tasks: List[Task]) -> bool:
    p = 1.0
    for t in tasks:
        p *= (t.C / t.T + 1)
    return p <= 2.0


def hyperperiod(tasks: List[Task]) -> int:
    return reduce(lambda a, b: a * b // math.gcd(a, b), (t.T for t in tasks), 1)


def is_harmonic(tasks: List[Task]) -> bool:
    ts = sorted(t.T for t in tasks)
    return all(ts[i + 1] % ts[i] == 0 for i in range(len(ts) - 1))


# --------------------------------------------------------------------------- analysis


def rta(tasks: List[Task], blocking: Optional[Dict[str, int]] = None,
        jitter: Optional[Dict[str, int]] = None, limit: int = 100000) -> Dict[str, Tuple[Optional[int], bool]]:
    """Response-time analysis for fixed-priority preemptive scheduling.

        R_i = C_i + B_i + sum_{j in hp(i)} ceil((R_i + J_j) / T_j) * C_j

    Returns {name: (R_i or None if it diverges past the deadline, schedulable?)}.
    Priorities must be set (rate_monotonic() / deadline_monotonic() or by hand).
    Release jitter J_i of the task itself is added to R_i (response measured from arrival).
    """
    blocking = blocking or {}
    jitter = jitter or {}
    out: Dict[str, Tuple[Optional[int], bool]] = {}
    for ti in tasks:
        hp = [tj for tj in tasks if tj is not ti and tj.prio > ti.prio]
        B = blocking.get(ti.name, 0)
        w = ti.C + B
        while True:
            nxt = ti.C + B + sum(math.ceil((w + jitter.get(tj.name, 0)) / tj.T) * tj.C for tj in hp)
            if nxt == w:
                break
            w = nxt
            if w + jitter.get(ti.name, 0) > ti.D or w > limit:
                break
        R = w + jitter.get(ti.name, 0)
        ok = (nxt == w) and R <= ti.D
        out[ti.name] = (R if nxt == w or R <= limit else None, ok)
    return out


# --------------------------------------------------------------------------- simulator


def simulate(tasks: List[Task], horizon: int, policy: str = "FP", protocol: str = "none",
             on_miss: str = "continue") -> Result:
    """Simulate `tasks` for `horizon` ticks.

    policy   : "FP" (fixed priority, `Task.prio`, higher = more urgent) or "EDF"
    protocol : "none" | "inherit" | "ceiling"   (for tasks that use lock/unlock segments; FP only)
    on_miss  : "continue" (late job keeps running), "abort" (kill at its deadline),
               "skip_release" (do not release a new job while the previous one is unfinished)
    """
    assert policy in ("FP", "EDF") and protocol in ("none", "inherit", "ceiling")
    assert on_miss in ("continue", "abort", "skip_release")
    if policy == "FP":
        assert all(t.prio is not None for t in tasks), "set priorities (rate_monotonic) first"
    name2task = {t.name: t for t in tasks}
    # resource ceilings = highest base priority among users
    ceilings: Dict[str, int] = {}
    for t in tasks:
        for kind, arg in t.segments:
            if kind == "lock":
                ceilings[arg] = max(ceilings.get(arg, 0), t.prio or 0)
    owner: Dict[str, Optional[Job]] = {r: None for r in ceilings}

    timeline: List[Optional[str]] = []
    blocked_log: List[List[str]] = []
    holding_log: List[Optional[str]] = []
    jobs: List[Job] = []
    active: List[Job] = []
    counters = {t.name: 0 for t in tasks}
    skipped = {t.name: 0 for t in tasks}

    def eff_prio(job: Job) -> float:
        base = job.task.prio or 0
        if policy == "EDF":
            return -job.deadline          # earlier deadline = larger
        p = base
        if protocol == "ceiling":
            for r in job.held:
                p = max(p, ceilings[r])
        elif protocol == "inherit":
            # propagate priorities of jobs blocked (directly or transitively) on resources we hold
            changed = True
            guard = 0
            prios = {id(j): (j.task.prio or 0) for j in active}
            while changed and guard < 20:
                changed = False
                guard += 1
                for j in active:
                    if j.blocked_on is not None and owner.get(j.blocked_on) is not None:
                        h = owner[j.blocked_on]
                        if prios[id(h)] < prios[id(j)]:
                            prios[id(h)] = prios[id(j)]
                            changed = True
            p = prios[id(job)]
        return p

    for t in range(horizon):
        # releases
        for task in tasks:
            if t >= task.offset and (t - task.offset) % task.T == 0:
                k = (t - task.offset) // task.T
                if on_miss == "skip_release" and any(j.task is task and j.finish is None and not j.aborted for j in active):
                    skipped[task.name] += 1
                    counters[task.name] += 1
                    continue
                segs = list(task.segments)
                extra = task.overrun.get(k, 0)
                if extra:
                    for si in range(len(segs) - 1, -1, -1):
                        if segs[si][0] == "run":
                            segs[si] = ("run", segs[si][1] + extra)
                            break
                job = Job(task=task, index=k, release=t, deadline=t + task.D, segs=segs)
                job.remaining = segs[0][1] if segs[0][0] == "run" else 0
                jobs.append(job)
                active.append(job)
                counters[task.name] += 1
        # abort at deadline
        if on_miss == "abort":
            for j in list(active):
                if t >= j.deadline and j.finish is None:
                    j.aborted = True
                    for r in list(j.held):
                        owner[r] = None
                    j.held.clear()
                    active.remove(j)

        running: Optional[Job] = None
        guard = 0
        while running is None and guard < 1000:
            guard += 1
            cands = [j for j in active if j.blocked_on is None]
            if not cands:
                break
            cands.sort(key=lambda j: (-eff_prio(j), j.release, tasks.index(j.task)))
            j = cands[0]
            # zero-time segments at head of the chosen job
            progressed = False
            while True:
                if j.seg_i >= len(j.segs):
                    j.finish = t
                    active.remove(j)
                    progressed = True
                    break
                kind, arg = j.segs[j.seg_i]
                if kind == "run":
                    if j.remaining == 0:
                        j.remaining = arg
                    running = j
                    break
                if kind == "lock":
                    if owner[arg] is None:
                        owner[arg] = j
                        j.held.append(arg)
                        j.seg_i += 1
                        continue
                    j.blocked_on = arg
                    progressed = True
                    break
                if kind == "unlock":
                    owner[arg] = None
                    j.held.remove(arg)
                    for w in active:
                        if w.blocked_on == arg:
                            w.blocked_on = None
                    j.seg_i += 1
                    continue
                raise ValueError("unknown segment kind %r" % kind)
            if running is None and not progressed:
                break
            # loop again to pick if job blocked/finished
        timeline.append(running.task.name if running else None)
        blocked_log.append(sorted(j.task.name for j in active if j.blocked_on is not None))
        holding_log.append(running.held[-1] if running and running.held else None)
        if running is not None:
            if running.start is None:
                running.start = t
            running.remaining -= 1
            if running.remaining == 0:
                running.seg_i += 1
                # finish immediately if no more segments (zero-time tail ops handled at next pick)
                while running.seg_i < len(running.segs) and running.segs[running.seg_i][0] == "unlock":
                    r = running.segs[running.seg_i][1]
                    owner[r] = None
                    running.held.remove(r)
                    for w in active:
                        if w.blocked_on == r:
                            w.blocked_on = None
                    running.seg_i += 1
                if running.seg_i >= len(running.segs):
                    running.finish = t + 1
                    active.remove(running)
                else:
                    kind, arg = running.segs[running.seg_i]
                    running.remaining = arg if kind == "run" else 0
    return Result(horizon, tasks, timeline, blocked_log, holding_log, jobs, skipped)


# --------------------------------------------------------------------------- text rendering


def ascii_gantt(res: Result, width: Optional[int] = None, start: int = 0) -> str:
    """One row per task. '#' running, '.' released and waiting (ready), 'b' blocked on a resource,
    ' ' not active.  A '|' ruler marks every 10 ticks."""
    end = res.horizon if width is None else min(res.horizon, start + width)
    names = [t.name for t in sorted(res.tasks, key=lambda t: -(t.prio or 0))]
    # reconstruct per-tick state from jobs
    rows = {n: [" "] * (end - start) for n in names}
    for j in res.jobs:
        fin = j.finish if j.finish is not None else res.horizon
        last = fin if not j.aborted else min(fin, res.horizon)
        for t in range(max(j.release, start), min(last if j.finish is not None else res.horizon, end)):
            rows[j.task.name][t - start] = "."
    for t in range(start, end):
        if res.timeline[t]:
            rows[res.timeline[t]][t - start] = "#"
        for n in res.blocked[t]:
            rows[n][t - start] = "b"
    ruler = "".join("|" if (t % 10 == 0) else " " for t in range(start, end))
    nums = ""
    t = start
    while t < end:
        if t % 10 == 0:
            s = str(t)
            nums += s
            t += len(s)
        else:
            nums += " "
            t += 1
    label_w = max(len(n) for n in names) + 1
    out = [" " * label_w + nums[: end - start], " " * label_w + ruler]
    for n in names:
        out.append(n.ljust(label_w) + "".join(rows[n]))
    return "\n".join(out)


def summary(res: Result, tasks: Optional[List[Task]] = None) -> str:
    rows = ["task   prio    C     T     D   jobs  max-R  misses"]
    for t in sorted(res.tasks, key=lambda t: -(t.prio or 0)):
        js = res.jobs_of(t.name)
        mr = res.max_response(t.name)
        rows.append("%-6s %4s %4d %5d %5d %5d %6s %7d" % (
            t.name, t.prio if t.prio is not None else "-", t.C, t.T, t.D, len(js),
            "-" if mr is None else mr, len(res.misses(t.name))))
    return "\n".join(rows)


# --------------------------------------------------------------------------- self-test

if __name__ == "__main__":
    # 1. Liu-Layland table
    print("n  bound")
    for n in (1, 2, 3, 4, 5, 10, 100):
        print("%-3d %.4f" % (n, ll_bound(n)))
    print("ln 2 = %.4f" % math.log(2))

    # 2. U above the bound yet RM-schedulable (RTA proves it)
    a = rate_monotonic([Task("t1", 1, 4), Task("t2", 2, 6), Task("t3", 3, 12)])
    print("\nSet A: U = %.3f > LL bound(3) = %.3f" % (utilization(a), ll_bound(3)))
    print("  RTA:", rta(a))
    r = simulate(a, hyperperiod(a))
    assert not r.misses(), "sim disagrees with RTA"
    assert r.max_response("t3") == rta(a)["t3"][0]
    print(ascii_gantt(r))

    # 3. EDF schedules what RM cannot
    b = rate_monotonic([Task("t1", 2, 5), Task("t2", 4, 7)])
    rm = simulate(b, hyperperiod(b), "FP")
    edf = simulate(b, hyperperiod(b), "EDF")
    print("\nSet B: U = %.3f   RM misses=%d   EDF misses=%d" % (utilization(b), len(rm.misses()), len(edf.misses())))
    assert rm.misses() and not edf.misses()

    # 4. Pathfinder-style inversion
    def pf():
        H = Task("H", segments=[("run", 1), ("lock", "R"), ("run", 2), ("unlock", "R"), ("run", 1)], T=50, offset=5)
        M = Task("M", 40, 100, offset=6)
        L = Task("L", segments=[("run", 2), ("lock", "R"), ("run", 10), ("unlock", "R"), ("run", 2)], T=200)
        return rate_monotonic([H, M, L])
    for proto in ("none", "inherit", "ceiling"):
        res = simulate(pf(), 100, "FP", proto)
        print("\nprotocol=%-8s H max response=%s  H misses=%d" % (proto, res.max_response("H"), len(res.misses("H"))))
    print("self-test OK")
