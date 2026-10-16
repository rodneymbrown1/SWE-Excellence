# Smoke test for your Linux machine {.appendix}

<p class="lede">I could not run gdb on the machine where I wrote this book. Every gdb command here was checked against the official manual, not executed. This two-minute test closes that gap on <em>your</em> gdb.</p>

## Run it

```
cd lab
make CXX=g++
sh gdb/smoke-test.sh
```

It prints your gdb version, whether gdb has Python, and one line per probe:

```
GNU gdb (…) 12.1
gdb has Python: yes
PASS  01-invariant
PASS  02-log-state-writes
PASS  03-rare-caller
PASS  04-counterfactual
PASS  05-count
PASS  06-arm-then-watch
PASS  07-break-on-output
PASS  08-python-probe
PASS  09-callers
```

(That is the shape of the output, not a captured result.) Each probe's full output is saved in `lab/transcripts/gdb-NN-name.txt`.

## If a probe fails

1. Open its transcript. Read gdb's message. It is usually specific.
2. Find the message in the table below.
3. Fix the script. Then tell me the message, and I will fix the book.

| gdb says | It means | Do this |
|---|---|---|
| `No symbol table is loaded. Use the "file" command.` | The binary has no debug info | Rebuild with `-g -O0` |
| `Make breakpoint pending on future shared library load?` | The name or file was not found | Check spelling; check `info functions NAME` |
| `Python scripting is not supported in this copy of GDB.` | gdb built without Python | Probes 3 and 8 need a Python build. Use the fallback in probe 3 (`break gateway.cpp:170`) |
| `Function "$_caller_matches" not defined.` | Same: no Python | Same fallback |
| `Could not insert hardware watchpoint` | Too many hardware watchpoints for this target | Delete some; or `set can-use-hw-watchpoints 0` (slow) |
| `Cannot watch constant value` | You gave an address literal | `watch *(int *) 0xADDR` |
| `<optimized out>` | Built with optimization | Rebuild with `-O0` |
| `No frame selected.` | The program is not running | `run` first |
| A watchpoint keeps firing after the program ends | The watched stack memory is being reused | Delete it at a breakpoint near the end (the lab scripts do) |
| Line-number probes stop at the wrong place | The file changed | Use function names, or re-check the line with `list gateway.cpp:75,81` |

## Quick checks you can run in 10 seconds

```
gdb --version                              # which gdb
gdb -batch -ex 'python print(1)'           # does it have Python? prints 1 if yes
gdb -batch -ex 'list main' ./gateway       # are symbols present?
```

## What the smoke test does not check

* It does not test your *own* project. It tests that your gdb understands the forms used here.
* It does not test VS Code. Appendix A covers that.
* It does not test rr, core dumps, or reverse execution (chapter 13).

## What I verified, and how

| Where | What I did |
|---|---|
| lldb on macOS | Ran every lldb probe in `lab/lldb/` and saved the output in `lab/transcripts/`. |
| gdb | Checked syntax against the GDB manual pages listed in `resource/research/03-gdb-mechanics.md`. Did not execute. |
| Patches | Applied in order with `patch -p1`, built, and ran. |
| Assert example | Built both ways and ran (chapter 24). |
