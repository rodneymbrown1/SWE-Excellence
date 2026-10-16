# Discovery probe: "where does this log line come from?"  Break on the output function, read the backtrace.   [MANUAL]
set pagination off
break printf
run --max 400
bt 5
