# A1: log every caller of LinkMonitor::on_event, then tally with:  grep "Gateway::" out.txt | sort | uniq -c   [MANUAL]
set pagination off
break LinkMonitor::on_event
commands
  silent
  bt 2
  continue
end
run --max 400
