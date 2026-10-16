# Probe 5 (COUNT): tally heartbeats without stopping; print the total at the end.   [MANUAL]
set pagination off
set $hb = 0
break LinkMonitor::on_heartbeat
commands
  silent
  set $hb = $hb + 1
  continue
end
break Gateway::summary
commands
  silent
  printf "heartbeats handled: %d\n", $hb
  continue
end
run --max 400
