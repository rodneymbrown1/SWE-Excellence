# Probe 2 (LOG + TRAP): log every write to state_ and who made it, without stopping.   [MANUAL]
set pagination off
break Gateway::run
run --max 400
# -l = watch the memory location, so it survives leaving this frame.  This will be watchpoint 2.
watch -l monitor_.state_
commands
  silent
  echo state_ written -> 
  output this->state_
  echo \n
  bt 3
  continue
end
# Delete the watchpoint near the end so it cannot fire on reused stack memory after main() returns.
break Gateway::summary
commands
  silent
  delete 2
  continue
end
continue
