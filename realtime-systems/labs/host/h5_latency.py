#!/usr/bin/env python3
"""Lab H5: percentiles lie when the measurement waits for the system (coordinated omission).

A service handles a request in ~1 ms, except for ONE 5-second stall in a 60-second test.
The intended load is 100 requests per second.

  closed-loop tester : sends the next request only after the previous one returned
  open-loop tester   : sends on a fixed schedule and measures from the INTENDED send time

Both talk to the same system.  Compare what each reports.

    python3 h5_latency.py
"""
import random

random.seed(7)
RATE = 100                  # intended requests / second
DURATION = 60.0
STALL_AT, STALL_LEN = 30.0, 5.0
INTERVAL = 1.0 / RATE


def service_time(start):
    """Time to serve a request that starts executing at `start` (a stall freezes the server)."""
    base = 0.001 + random.random() * 0.0004
    if STALL_AT <= start < STALL_AT + STALL_LEN:
        return (STALL_AT + STALL_LEN - start) + base
    return base


def closed_loop():
    t, out = 0.0, []
    while t < DURATION:
        d = service_time(t)
        out.append(d)
        t += max(d, INTERVAL)           # wait for the response, then wait out the rest of the interval
    return out


def open_loop():
    out, server_free = [], 0.0
    for i in range(int(DURATION * RATE)):
        sched = i * INTERVAL
        start = max(sched, server_free)
        d = service_time(start)
        server_free = start + d
        out.append(server_free - sched)  # latency from the intended send time
    return out


def pct(xs, p):
    s = sorted(xs)
    return s[min(len(s) - 1, int(p / 100.0 * len(s)))]


def fill_in(samples, expected):
    """Tene's correction: for every sample longer than the expected interval, add the samples the
    tester *would* have taken during the stall (decreasing by `expected` each)."""
    out = list(samples)
    for v in samples:
        x = v - expected
        while x >= expected:
            out.append(x)
            x -= expected
    return out


def row(name, xs):
    print("%-30s %7d  %8.2f %8.2f %9.2f %10.2f %9.0f" % (name, len(xs), pct(xs, 50) * 1000, pct(xs, 99) * 1000,
                                                       pct(xs, 99.9) * 1000, pct(xs, 99.99) * 1000, max(xs) * 1000))


if __name__ == "__main__":
    c, o = closed_loop(), open_loop()
    print("%-30s %7s  %8s %8s %9s %10s %9s" % ("method", "samples", "p50 ms", "p99 ms", "p99.9 ms", "p99.99 ms", "max ms"))
    row("closed-loop (as reported)", c)
    row("closed-loop + correction", fill_in(c, INTERVAL))
    row("open-loop (ground truth)", o)
    print("\nThe system stalled for %.0f s of a %.0f s test: ~%.0f%% of the requests that WOULD have arrived were delayed."
          % (STALL_LEN, DURATION, 100 * STALL_LEN / DURATION))
    slow = sum(1 for x in o if x > 0.1)
    print("Open-loop sees %d of %d requests slower than 100 ms; the closed-loop tester recorded %d." %
          (slow, len(o), sum(1 for x in c if x > 0.1)))
    # a periodic real-time task has the same bias if the logger only records jobs that RAN:
    print("\nRTOS translation: if a task overruns and you log only the response times of the jobs that ran, the")
    print("releases it SKIPPED during the overrun never appear in your histogram.  Count releases, not completions.")
