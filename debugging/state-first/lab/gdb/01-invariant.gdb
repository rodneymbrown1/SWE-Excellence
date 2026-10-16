# Probe 1 (FILTER): stop the first time a Heartbeat leaves missed_ non-zero.   Requirement R5.
# Run from lab/:   gdb -q -batch -x gdb/01-invariant.gdb ./gateway        [MANUAL: not executed on the author's Mac]
# Line 81 is the closing brace of LinkMonitor::on_event in gateway.cpp (check with: list gateway.cpp:75,81).
set pagination off
break gateway.cpp:81 if e.type == EventType::Heartbeat && missed_ != 0
run --max 400
bt
print *this
print e
