#!/bin/sh
# Rebuild every RTOS lab and regenerate labs/transcripts/*.txt (what the workbook shows as expected output).
# usage: sh labs/rtos/capture.sh        (from the repository's realtime-systems/ directory)
set -e
cd "$(dirname "$0")"
T=../transcripts; mkdir -p $T
run() { python3 run.py "$@"; }
for l in r0_hello r1_time r2_rm r4_queue r6_memory r7_tickwrap; do
  (cd $l && make clean >/dev/null && make >/dev/null) && run $l/build/$l.elf --timeout 120 > $T/$l.txt 2>&1
  echo "captured $l"
done
(cd r3_inversion && make clean >/dev/null && make >/dev/null) && run r3_inversion/build/r3_inversion.elf --timeout 120 > $T/r3_inversion.txt 2>&1
(cd r3_inversion && make clean >/dev/null && make TRACE_PHASE=1 >/dev/null) && run r3_inversion/build/r3_inversion.elf --timeout 120 > $T/r3_trace_phase1.raw 2>&1
python3 ../tools/trace2gantt.py $T/r3_trace_phase1.raw --from 0 --to 120 --width 120 > $T/r3_timeline_phase1.txt
(cd r3_inversion && make clean >/dev/null && make TRACE_PHASE=2 >/dev/null) && run r3_inversion/build/r3_inversion.elf --timeout 120 > $T/r3_trace_phase2.raw 2>&1
python3 ../tools/trace2gantt.py $T/r3_trace_phase2.raw --from 0 --to 120 --width 120 > $T/r3_timeline_phase2.txt
echo "captured r3"
for m in 1 2 3; do
  (cd r5_watchdog && make clean >/dev/null && make MODE=$m >/dev/null) && run r5_watchdog/build/r5_watchdog.elf --reboot --timeout 60 > $T/r5_mode$m.txt 2>&1
done
echo "captured r5"
(cd r8_trace && make clean >/dev/null && make >/dev/null) && run r8_trace/build/r8_trace.elf --timeout 120 > $T/r8_trace.txt 2>&1
(cd r8_trace && make clean >/dev/null && make TRACE=1 >/dev/null) && run r8_trace/build/r8_trace.elf --timeout 120 > $T/r8_trace.raw 2>&1
python3 ../tools/trace2gantt.py $T/r8_trace.raw --from 0 --to 36 --scale 250 --width 144 > $T/r8_timeline.txt
echo "captured r8"
(cd r10_pipeline && make clean >/dev/null && make >/dev/null) && run r10_pipeline/build/r10_pipeline.elf --timeout 120 > $T/r10_first_look.txt 2>&1
(cd r10_pipeline && make clean >/dev/null && make DUMP=1 REVEAL=1 >/dev/null) && run r10_pipeline/build/r10_pipeline.elf --timeout 120 > $T/r10_dump.raw 2>&1
grep -v '^L ' $T/r10_dump.raw > $T/r10_reveal.txt
python3 ../tools/lathist.py $T/r10_dump.raw --limit 3000 > $T/r10_hist_baseline.txt
(cd r10_pipeline && make clean >/dev/null && make TRACE=1 >/dev/null) && run r10_pipeline/build/r10_pipeline.elf --timeout 120 > $T/r10_trace.raw 2>&1
python3 ../tools/trace2gantt.py $T/r10_trace.raw --from 0 --to 80 --width 160 > $T/r10_timeline_baseline.txt
# fixed build (all four patches)
cp r10_pipeline/main.c /tmp/r10_main_orig.c
for p in r10_pipeline/solutions/0*.patch; do patch -s r10_pipeline/main.c < $p; done
(cd r10_pipeline && make clean >/dev/null && make DUMP=1 REVEAL=1 >/dev/null) && run r10_pipeline/build/r10_pipeline.elf --timeout 120 > $T/r10_dump_fixed.raw 2>&1
grep -v '^L ' $T/r10_dump_fixed.raw > $T/r10_reveal_fixed.txt
python3 ../tools/lathist.py $T/r10_dump_fixed.raw --limit 3000 > $T/r10_hist_fixed.txt
cp /tmp/r10_main_orig.c r10_pipeline/main.c; rm -f /tmp/r10_main_orig.c
(cd r10_pipeline && make clean >/dev/null)
echo "captured r10"
echo "done. (R9 gdb transcript: see gdb/README.md)"
