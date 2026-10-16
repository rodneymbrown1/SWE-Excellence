# Probe 8 (FILTER, in Python): same question as probe 1, but the condition is real code.   [MANUAL]
set pagination off
source gdb/08-stale-missed.py
run --max 400
print *this
