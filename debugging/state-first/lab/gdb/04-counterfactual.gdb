# Probe 4 (EXPERIMENT): stop at the first violation, set missed_ = 0 by hand, see if R4 now holds.   [MANUAL]
set pagination off
break gateway.cpp:81 if e.type == EventType::Heartbeat && missed_ != 0
run --max 400
print *this
set var missed_ = 0
delete 1
continue
