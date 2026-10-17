#!/usr/bin/env python3
"""Run a lab image in QEMU (mps2-an385, Cortex-M3).

    python3 run.py r0_hello/build/r0_hello.elf [--icount N] [--gdb] [--timeout S]

  --icount N   deterministic virtual time: 1 instruction = 2^N ns (default 5).  Same output every run.
  --real       use host time instead (timing then depends on your machine)
  --gdb        wait for a debugger on localhost:1234 (see the gdb commands printed)
  --reboot     let the guest reset itself (SYSRESETREQ) and boot again; default is to stop QEMU on reset
"""
import argparse, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument("elf")
ap.add_argument("--icount", type=int, default=5)
ap.add_argument("--real", action="store_true")
ap.add_argument("--gdb", action="store_true")
ap.add_argument("--reboot", action="store_true", help="allow the guest to reset itself and boot again (watchdog lab)")
ap.add_argument("--timeout", type=float, default=60.0)
a = ap.parse_args()

cmd = ["qemu-system-arm", "-machine", "mps2-an385", "-cpu", "cortex-m3", "-kernel", a.elf,
       "-display", "none", "-monitor", "none", "-serial", "stdio",
       "-semihosting-config", "enable=on,target=native"]
if not a.reboot:
    cmd += ["-no-reboot"]
if not a.real:
    cmd += ["-icount", "shift=%d,sleep=off" % a.icount]
if a.gdb:
    cmd += ["-S", "-s"]
    print("# waiting for gdb:  arm-none-eabi-gdb %s -ex 'target remote :1234'" % a.elf, file=sys.stderr)
try:
    r = subprocess.run(cmd, timeout=a.timeout)
    sys.exit(r.returncode)
except subprocess.TimeoutExpired:
    print("\n[run.py] timeout after %.0f s of real time" % a.timeout, file=sys.stderr)
    sys.exit(124)
