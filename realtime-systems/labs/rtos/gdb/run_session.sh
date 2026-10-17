#!/bin/sh
# Run the scripted gdb sessions and save transcripts.  usage: sh labs/rtos/gdb/run_session.sh   (from realtime-systems/)
set -e
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; cd "$ROOT"
T=labs/transcripts; mkdir -p $T
gdb_batch() { perl -e 'alarm 120; exec @ARGV' arm-none-eabi-gdb -q -batch "$@" 2>&1; }

# ---- A. R3 priority inversion, inspected with the freertos.py helpers
(cd labs/rtos/r3_inversion && make clean >/dev/null && make OPT=-O0 >/dev/null)
python3 labs/rtos/run.py labs/rtos/r3_inversion/build/r3_inversion.elf --gdb --timeout 150 >/dev/null 2>&1 &
sleep 2
gdb_batch -x labs/rtos/gdb/r3_session.gdb labs/rtos/r3_inversion/build/r3_inversion.elf | sed -e 's#/Users/[^ ]*/labs/#labs/#g' > $T/r9_gdb_r3_session.txt || true
pkill -f qemu-system-arm || true
(cd labs/rtos/r3_inversion && make clean >/dev/null)

# ---- B. the observer effect: the same program, with and without two silent breakpoints
(cd labs/rtos/r0_hello && make clean >/dev/null && make >/dev/null)
python3 labs/rtos/run.py labs/rtos/r0_hello/build/r0_hello.elf | sed -n 2,5p > $T/r9_observer_effect.txt
echo "--- same program, two silent breakpoints on 'worker' (each one stops the target, then resumes it) ---" >> $T/r9_observer_effect.txt
printf 'set pagination off\ntarget remote :1234\nbreak worker\ncommands\nsilent\ncontinue\nend\ncontinue\n' > /tmp/r9_obs.gdb
python3 labs/rtos/run.py labs/rtos/r0_hello/build/r0_hello.elf --gdb --timeout 60 > /tmp/r9_obs_out.txt 2>&1 &
sleep 2
gdb_batch -x /tmp/r9_obs.gdb labs/rtos/r0_hello/build/r0_hello.elf >/dev/null || true
sleep 1; pkill -f qemu-system-arm || true
grep '^\[' /tmp/r9_obs_out.txt | head -4 >> $T/r9_observer_effect.txt
(cd labs/rtos/r0_hello && make clean >/dev/null)
echo "gdb transcripts written"
