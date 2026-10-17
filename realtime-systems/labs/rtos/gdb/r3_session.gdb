# gdb session for R3 (priority inversion), driven from a script so it is repeatable.
#   make -C labs/rtos/r3_inversion clean && make -C labs/rtos/r3_inversion OPT=-O0
#   python3 labs/rtos/run.py labs/rtos/r3_inversion/build/r3_inversion.elf --gdb &
#   arm-none-eabi-gdb -q -batch -x labs/rtos/gdb/r3_session.gdb labs/rtos/r3_inversion/build/r3_inversion.elf
set pagination off
set confirm off
source labs/rtos/gdb/freertos.py
target remote :1234

echo \n### 1. LOGPOINT: log every bus_dist job without touching the code (phase 1 = binary semaphore)\n
break xTaskDelayUntil if $_caller_is("bus_dist") && H_jobs > 0
commands
  silent
  printf "tick %4d: bus_dist finished job %d, response %d ms\n", xTickCount, H_jobs - 1, H_resp[H_jobs - 1]
  continue
end

echo \n### 2. WATCHPOINT on a shared variable: stop when bc_sched declares the first reset\n
watch resets if resets == 1
commands
  silent
  printf "\n>>> resets became 1 at tick %d\n", xTickCount
  fr-tasks
  echo \n--- the lock (a binary semaphore): who owns it? ---\n
  fr-queue lock
  echo \n
  continue
end

echo \n### 3. PROBE THE KERNEL: stop where the kernel raises a task's priority (only a MUTEX does this)\n
break xTaskPriorityInherit

# run: the logpoint and the watchpoint print and continue by themselves; this one stops us
continue
printf "\n>>> xTaskPriorityInherit called at tick %d (phase 2: the lock is a mutex)\n", xTickCount
echo before the boost:\n
fr-tasks
finish
echo \nafter the boost (back in xQueueSemaphoreTake):\n
fr-tasks
echo \n--- the lock (a mutex): who owns it? ---\n
fr-queue lock
delete
kill
quit
