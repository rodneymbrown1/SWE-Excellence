# 04 · Embedded notes and tooling

## Memfault — "Faster Debugging with Watchpoints" (T03)
- Watchpoints are "data breakpoints"; on Cortex-M they use hardware comparators in the DWT unit. The article's example dump shows `NUMCOMP=0x4` on an nRF52840 — **one device's value; the count is chip-specific** (check `DWT_CTRL.NUMCOMP` in your core's manual).
- Example commands from the article: `watch *(uint8_t[2] *)0x200029a0`, `rwatch *(uint8_t[4] *)0x200029a0`.
- "it is only possible to watch ranges of addresses that are aligned on the size being watched."
- Halt timing: "When a watchpoint event is triggered the `$pc` has already advanced to the next instruction." and the article says that by the time the system halts, "we are two instructions past where the load or store occurred." → the stop line is *after* the write.
- GDB quirk: "If both values are equal, GDB will suppress the debug event generated and auto-resume the processor." → a write of the **same value does not stop** a plain `watch`. (Matters when hunting "who wrote it" — use `awatch` or a data-value comparator, or a breakpoint.)
- The article builds a custom GDB Python command (`watch_ext`) for data-value watchpoints; that part was only read via a model summary — **not used in the book**.

## Gillian Minnehan, "GDB Deep Dive" (T04, EOC 2024, 32:29)
Session page: "a rundown of important GDB commands, the GDB Python API, options for visual debugging, and how GDB plays a role even after you ship IoT device firmware." Speaker is at Memfault. Video is behind a free login — we did not watch it; your notes.txt is the source for what the talk contained (gdb-dashboard demo, VS Code GUI, core-dump primer).

## gdb-dashboard (T05)
- "a standalone `.gdbinit` file written using the Python API that enables a modular interface showing relevant information about the program being debugged."
- Install per README: `wget -P ~ https://github.com/cyrus-and/gdb-dashboard/raw/master/.gdbinit` (optional `pip install pygments`). "the dashboard will appear automatically every time the inferior program stops."
- README does not state GDB/Python version requirements → requires GDB built with Python (check `gdb -batch -ex 'python print(1)'`).
- **Work-machine caution (our note):** it is a single file you download from the internet and GDB executes. Ask your team/IT whether it is allowed and pin a reviewed copy.

## VS Code (T06)
- C/C++ (`cppdbg`) required: `program`; `MIMode` = `gdb`/`lldb`; `miDebuggerPath` = "The path to the debugger (such as gdb)"; `cwd`; `args` (array); `stopAtEntry` (default false); `externalConsole` (on Linux: true → external console, false → VS Code's integrated terminal); `setupCommands` (run in GDB at start); `preLaunchTask` for the build (tasks.json must compile with `-g`).
- Sample launch/tasks files in the Linux config page; install prerequisites `sudo apt-get install build-essential gdb`.
- Remote-SSH: "Local extensions that actually need to run remotely will appear dimmed and disabled in the Local - Installed category. Select Install to install an extension on your remote host." and "most extensions will reside on the SSH host"; there is also "Install Local Extensions in SSH: {Hostname}".
- Debugging remote: "Once you are connected to a remote host, you can use VS Code's debugger in the same way you would when running the application locally."
- UI breakpoint types (Debugging page): conditional (expression / hit count / wait for breakpoint), function breakpoints, data breakpoints ("The available options depend on the debugger" — **the page does not say which debuggers support them**), logpoints ("writes a message to the Debug Console without pausing execution"; curly-brace expressions; "available only when the debugger extension implements them").
- Debug Console raw commands for cppdbg: "you can execute GDB, LLDB and LLDB-MI commands directly through the debug console with the `-exec` command, but be careful, executing commands directly in the debug console is untested and might crash VS Code in some cases." (C++ debugging page, dated 2020).
- Known Linux error: `ptrace: Operation not permitted` (attach needs ptrace permission).

## rr (T07)
`rr record /path/to/app [args]` then `rr replay` (launches gdb connected to the replay). "gdb's `reverse-continue`, `reverse-step`, `reverse-next`, and `reverse-finish` commands all work under rr." Limits: modern x86 or certain ARM (Apple M1+); single-core emulation; cannot record processes sharing memory with processes outside the recording tree; the recorded executable must not change before replay. The PMU (hardware counter) requirement is **not** stated on the pages we read.

## LLDB (T08) — what we ran here
`lldb-1700.0.9.502` on macOS arm64. Verified in this project: `breakpoint set -f F -l N -c 'COND'`; `breakpoint command add -F module.func` (Python callback; return False = keep running); `watchpoint set variable this->monitor_.state_`; `watchpoint command add -F module.func N`; `frame variable`; `p *this`; `expression missed_ = 0`; `bt`; `up`; `breakpoint list` (hit counts). Observations: (1) a stack-variable watchpoint kept firing after the program exited unless deleted — delete it at a breakpoint near the end; (2) `-o` command lists attached to a watchpoint did not print their output in `-b` batch mode — use a Python callback.
