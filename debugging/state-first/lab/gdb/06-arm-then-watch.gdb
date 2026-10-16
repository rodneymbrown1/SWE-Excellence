# Probe 6 (ARM): watch missed_ only AFTER the link has become Degraded.   [MANUAL]
# Idea: a breakpoint is the trigger; its command list switches the (initially disabled) watchpoint on.
set pagination off
break Gateway::run
run --max 400
watch -l monitor_.missed_
# This is watchpoint 2.  Keep it off until armed.
disable 2
commands 2
  silent
  echo missed_ ->
  output this->missed_
  echo \n
  continue
end
break LinkMonitor::announce if state_ == LinkState::Degraded
commands
  silent
  enable 2
  continue
end
break Gateway::summary
commands
  silent
  delete 2
  continue
end
continue
