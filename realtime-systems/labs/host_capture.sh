#!/bin/sh
# Regenerate labs/transcripts/h*.txt from the host labs.  usage: sh labs/host_capture.sh
set -e
cd "$(dirname "$0")/host"
T=../transcripts; mkdir -p $T
make >/dev/null
python3 rtsim.py > $T/h3_selftest.txt
python3 h1_patriot.py > $T/h1_patriot.txt
./h1_tickwrap > $T/h1_tickwrap.txt
./h1_loop sleep_rel 10000 2000 300 > $T/h1_loop_sleep_rel.txt
./h1_loop sleep_abs 10000 2000 300 > $T/h1_loop_sleep_abs.txt
./h1_loop sleep_abs 10000 2000 300 6000 > $T/h1_loop_sleep_abs_noise.txt
./h2_cyclic > $T/h2_nominal.txt
./h2_cyclic overrun > $T/h2_overrun.txt
./h2_cyclic overrun skip > $T/h2_overrun_skip.txt
for n in 1 2 3 4; do python3 h3_demos.py $n > $T/h3_demo$n.txt; done
python3 rtcalc.py sense:1:10 filter:3:20 control:4:40 log:10:100 --gantt 60 > $T/h3_rtcalc_example.txt
python3 h4_queue.py > $T/h4_queue.txt
python3 h4_queue.py apollo > $T/h4_apollo.txt
python3 h5_latency.py > $T/h5_latency.txt
make clean >/dev/null
echo "host transcripts written to labs/transcripts"
