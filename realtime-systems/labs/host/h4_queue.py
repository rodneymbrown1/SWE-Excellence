#!/usr/bin/env python3
"""Lab H4: bounded queues, bursts, and what 'full' means.

A producer sends 100 msg/s steadily, plus a burst of 20 messages at 1000 msg/s once per second.
A consumer needs 5 ms per message (capacity 200 msg/s).  Average load is ~120/200 = 60%, yet the
burst arrives faster than the consumer can drain it.

    python3 h4_queue.py            queue-depth sweep for three overflow policies
    python3 h4_queue.py apollo     a toy model of the Apollo 11 executive running out of core sets

Everything is a discrete-event simulation with a fixed seed: identical output on every run.
"""
import math
import sys
from collections import deque

SERVICE = 0.005          # s per message
STEADY = 0.010           # s between steady messages
BURST_N, BURST_GAP = 20, 0.001
DURATION = 10.0


def arrivals():
    ev = []
    t = 0.0
    while t < DURATION:
        ev.append(t)
        t += STEADY
    for s in range(1, int(DURATION)):
        for i in range(BURST_N):
            ev.append(s + 0.0005 + i * BURST_GAP)
    ev.sort()
    return ev


def run(depth, policy, trace=None):
    """policy: drop_newest | drop_oldest | block.  Returns stats dict.  If `trace` is a list, (time, items in system) is appended."""
    arr = arrivals()
    q = deque()                      # holds arrival times
    busy_until = 0.0
    lat, drops, maxdepth = [], 0, 0
    area, last_t = 0.0, 0.0          # for time-average depth (Little's law)
    in_service = None
    events = [(t, "arr") for t in arr]
    # simple event loop: process in time order, service completions generated on the fly
    import heapq
    heap = [(t, 0, "arr") for t in arr]
    heapq.heapify(heap)
    serving = False
    blocked_producer_delay = 0.0
    pending_block = deque()          # for 'block': arrivals waiting for space
    n_in = 0
    sojourn_sum = 0.0

    def start_service(now):
        nonlocal serving, in_service
        if q and not serving:
            t_arr = q.popleft()
            in_service = t_arr
            serving = True
            heapq.heappush(heap, (now + SERVICE, 1, "done"))

    while heap:
        t, _, kind = heapq.heappop(heap)
        area += (len(q) + (1 if serving else 0)) * (t - last_t)
        last_t = t
        if kind == "arr":
            if len(q) < depth:
                q.append(t)
                n_in += 1
            elif policy == "drop_newest":
                drops += 1
            elif policy == "drop_oldest":
                q.popleft()
                drops += 1
                q.append(t)
                n_in += 1
            else:                                     # block: producer waits for space (arrival time is delayed)
                pending_block.append(t)
            start_service(t)
        else:                                          # service completion
            lat.append(t - in_service)
            sojourn_sum += t - in_service
            serving = False
            if pending_block and len(q) < depth:
                orig = pending_block.popleft()
                blocked_producer_delay = max(blocked_producer_delay, t - orig)
                q.append(orig)                         # keeps ORIGINAL arrival time: latency includes the wait
                n_in += 1
            start_service(t)
        maxdepth = max(maxdepth, len(q) + (1 if serving else 0))
        if trace is not None:
            trace.append((t, len(q) + (1 if serving else 0)))
    lat.sort()
    p = lambda f: lat[min(len(lat) - 1, int(f * len(lat)))] * 1000
    L = area / last_t
    lam = len(lat) / last_t
    W = sum(lat) / len(lat)
    return dict(depth=depth, policy=policy, delivered=len(lat), dropped=drops, maxdepth=maxdepth,
                p50=p(0.50), p99=p(0.99), maxlat=lat[-1] * 1000, producer_wait=blocked_producer_delay * 1000,
                L=L, lamW=lam * W)


def sweep():
    print("burst: %d msgs at %d/s once per second, on top of %d/s steady; service %d ms/msg (capacity %d/s)\n" %
          (BURST_N, round(1 / BURST_GAP), round(1 / STEADY), SERVICE * 1000, round(1 / SERVICE)))
    peak = 1 / BURST_GAP + 1 / STEADY                    # arrival rate while the burst lasts (burst + steady)
    t_burst = BURST_N * BURST_GAP
    need = math.ceil((peak - 1 / SERVICE) * t_burst) + 1
    print("sizing rule:  depth >= ceil((peak_rate - service_rate) * burst_duration) + 1")
    print("            = ceil((%.0f - %.0f) * %.3f) + 1 = %d slots\n" % (peak, 1 / SERVICE, t_burst, need))
    hdr = "%-12s %5s %9s %8s %8s %9s %9s %12s" % ("policy", "depth", "delivered", "dropped", "maxdepth", "p50 ms", "p99 ms", "max lat ms")
    print(hdr)
    for pol in ("drop_newest", "drop_oldest", "block"):
        for d in (4, 8, 18, need, 32):
            r = run(d, pol)
            print("%-12s %5d %9d %8d %8d %9.1f %9.1f %12.1f" % (pol, r["depth"], r["delivered"], r["dropped"], r["maxdepth"], r["p50"], r["p99"], r["maxlat"]))
        print()
    r = run(32, "drop_newest")
    print("Little's law check (depth 32, nothing dropped): time-average items in system L = %.3f;  lambda * W = %.3f" % (r["L"], r["lamW"]))


APOLLO_T, APOLLO_WORK, APOLLO_POOL = 2.0, 1.0, 8


def apollo_run(hp, steps=400):
    """Toy model, NOT Apollo data.  Returns (alarm_times, outstanding_jobs_per_period)."""
    backlog, alarms, hist = 0.0, [], []
    for k in range(1, steps):
        backlog += APOLLO_WORK - (1 - hp) * APOLLO_T          # work that did not fit this period
        backlog = max(backlog, 0.0)
        jobs = 1 + int(backlog // APOLLO_WORK)               # outstanding jobs, each holding a core set
        if jobs > APOLLO_POOL:
            alarms.append(k * APOLLO_T)
            backlog, jobs = 0.0, 1                            # BAILOUT: restart flushes the queue
        hist.append(jobs)
    return alarms, hist


def apollo():
    """A 2 s job (SERVICER) needs `work` seconds of CPU per period. Higher-priority load takes `hp` of the CPU.
    A job that has not finished when the next one is released keeps its core set.  With 8 core sets the 9th request
    fails -> BAILOUT (1202): the restart keeps only the newest job and flushes the rest."""
    print("period %.1fs, job needs %.1fs CPU, pool = %d core sets\n" % (APOLLO_T, APOLLO_WORK, APOLLO_POOL))
    for label, hp in (("hp load 0.40 (job fits)", 0.40), ("hp load 0.52 (small deficit)", 0.52), ("hp load 0.62 (larger deficit)", 0.62)):
        alarms, hist = apollo_run(hp)
        print("%-34s alarms in %4.0f s: %2d   first alarm at %s   peak outstanding jobs %d" %
              (label, 400 * APOLLO_T, len(alarms), "-" if not alarms else "%.0f s" % alarms[0], max(hist)))
    print("\nWhat to notice: a small steady deficit does not fail at once -- it fills a fixed pool, then the system restarts,")
    print("recovers, and fails again.  The alarm spacing is set by (pool size) / (deficit per period).")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "apollo":
        apollo()
    else:
        sweep()
