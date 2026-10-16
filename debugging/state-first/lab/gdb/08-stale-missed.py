"""A Python probe for gdb:  stop only when a Heartbeat leaves missed_ non-zero.   [MANUAL]

Use:   gdb -q -batch -x gdb/08-python-probe.gdb ./gateway
A gdb.Breakpoint subclass overrides stop(): return True to stop, False to keep running.
Rules from the manual: do not step, change frames, or add/delete breakpoints inside stop().
"""
import gdb


class StaleMissed(gdb.Breakpoint):
    def stop(self):
        etype = str(gdb.parse_and_eval("e.type"))
        missed = int(gdb.parse_and_eval("missed_"))
        return etype.endswith("Heartbeat") and missed != 0


StaleMissed("gateway.cpp:81")
