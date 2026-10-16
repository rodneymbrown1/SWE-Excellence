#!/bin/sh
# Run this ONCE on your Linux box to confirm every gdb probe in the book works on YOUR gdb.
#   cd lab && make CXX=g++ && sh gdb/smoke-test.sh
# Prints PASS/FAIL per probe.  A FAIL means: read gdb's message, fix the script, tell me what it said.
cd "$(dirname "$0")/.." || exit 1
[ -x ./gateway ] || { echo "build first:  make CXX=g++"; exit 1; }
command -v gdb >/dev/null || { echo "gdb not found"; exit 1; }
gdb --version | head -1
gdb -q -batch -ex 'python print("python-ok")' 2>&1 | grep -q python-ok && echo "gdb has Python: yes" || echo "gdb has Python: NO (probe 3 needs the fallback)"
mkdir -p transcripts
check() {  # name, file, pattern
  out="transcripts/gdb-$1.txt"
  gdb -q -batch -x "gdb/$1.gdb" ./gateway > "$out" 2>&1
  if grep -q -E "$2" "$out"; then echo "PASS  $1"; else echo "FAIL  $1   (see $out)"; fi
}
check 01-invariant          'missed_ = 7'
check 02-log-state-writes   'state_ written -> (LinkState::)?Degraded'
check 03-rare-caller        'payload = 99'
check 04-counterfactual     'Degraded +-> Up'
check 05-count              'heartbeats handled: 160'
check 06-arm-then-watch     'missed_ ->'
check 07-break-on-output    'LinkMonitor::announce'
check 08-python-probe       'missed_ = 7'
check 09-callers            'Gateway::flush_burst'
