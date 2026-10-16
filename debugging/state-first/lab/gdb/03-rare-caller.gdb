# Probe 3 (FILTER by caller): stop on LinkMonitor::on_event only when flush_burst called it.   [MANUAL]
# Needs a gdb built with Python.  If $_caller_matches is missing, use the fallback below instead.
set pagination off
break LinkMonitor::on_event if $_caller_matches(".*flush_burst")
# Fallback with no Python:  break gateway.cpp:170     (the call site inside flush_burst)
run --max 400
bt
print e
