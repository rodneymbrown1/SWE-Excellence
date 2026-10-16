"""lldb probes for the State First lab (gateway.cpp).

Load inside lldb:   command script import lldb/probes.py
Each function is a callback.  Return False = "do not stop, keep running" (a log line).
Return True = "stop here so I can look".  This is the lldb twin of gdb's
`commands / silent / printf / continue` and of a Python gdb.Breakpoint.stop().
"""
import lldb


def _chain(frame, depth=3):
    thread = frame.GetThread()
    n = min(depth, thread.GetNumFrames())
    return " <- ".join(thread.GetFrameAtIndex(i).GetFunctionName() or "?" for i in range(n))


def log_state_write(frame, bp_loc, internal_dict):
    """Watchpoint callback: log every write to state_ (value, line, call chain); keep running."""
    this = frame.FindVariable("this")
    state = this.GetChildMemberWithName("state_").GetValue()
    line = frame.GetLineEntry().GetLine()
    print("  state_ written -> %-8s after line %d   via %s" % (state, line, _chain(frame)))
    return False


def stop_if_called_from_flush_burst(frame, bp_loc, internal_dict):
    """Breakpoint callback on LinkMonitor::on_event: stop only for the rare caller."""
    caller = frame.GetThread().GetFrameAtIndex(1).GetFunctionName() or ""
    return "flush_burst" in caller


def stop_on_stale_missed(frame, bp_loc, internal_dict):
    """Breakpoint callback at the end of on_event: invariant 'after a Heartbeat, missed_ == 0'."""
    e = frame.FindVariable("e")
    if e.GetChildMemberWithName("type").GetValue() != "Heartbeat":
        return False
    missed = frame.FindVariable("this").GetChildMemberWithName("missed_").GetValueAsSigned()
    return missed != 0


# ---- COUNT: tally events without stopping (the lldb twin of a gdb convenience-variable counter) ----
_counts = {"heartbeat": 0}


def count_heartbeat(frame, bp_loc, internal_dict):
    _counts["heartbeat"] += 1
    return False


def show_counts(frame, bp_loc, internal_dict):
    print("heartbeats handled: %d" % _counts["heartbeat"])
    return False


# ---- A1 / A2: who calls on_event, and what (state x event) combinations really occur --------------
_callers = {}
_grid = {}


def tally_caller_and_cell(frame, bp_loc, internal_dict):
    """Breakpoint callback at the entry of LinkMonitor::on_event. Records the caller and the (state, event) cell."""
    thread = frame.GetThread()
    parent = thread.GetFrameAtIndex(1)
    key = "%s:%d" % (parent.GetFunctionName(), parent.GetLineEntry().GetLine())
    _callers[key] = _callers.get(key, 0) + 1
    this = frame.FindVariable("this")
    state = this.GetChildMemberWithName("state_").GetValue()
    etype = frame.FindVariable("e").GetChildMemberWithName("type").GetValue()
    _grid[(state, etype)] = _grid.get((state, etype), 0) + 1
    return False


def show_tallies(frame, bp_loc, internal_dict):
    print("callers of LinkMonitor::on_event (function:line  count)")
    for k in sorted(_callers):
        print("  %-28s %d" % (k, _callers[k]))
    print("observed state x event (count of events seen in that state)")
    print("  %-10s %8s %10s %8s" % ("", "Tick", "Heartbeat", "Data"))
    for s in ("Down", "Up", "Degraded"):
        print("  %-10s %8d %10d %8d" % (s, _grid.get((s, "Tick"), 0), _grid.get((s, "Heartbeat"), 0), _grid.get((s, "Data"), 0)))
    return False
