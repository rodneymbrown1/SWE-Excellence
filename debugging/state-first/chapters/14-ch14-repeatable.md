# Make probes repeatable {.chapter}

<p class="lede">A probe you type by hand is gone when the session ends. A probe in a file can be run again, improved, shared, and attached to a ticket. That is the difference between "I debugged it" and a repeatable result.</p>

## Why this matters

In the debugging study, one expert said breakpoints are "like a one-shot. Ideally I wouldn't like them to be, but I just set them anew." The authors also observed that "debugging is an internal thought process not usually shared." (Beller et al., 2018.) Saving your probes fixes both. You stop re-creating them, and someone else can read exactly what you asked the program.

## Four levels, cheapest first

### Level 1: save what you typed

```
save breakpoints probes.gdb          # in a session                       [MANUAL]
source probes.gdb                    # in a later session
```

The file is plain gdb commands, so you can edit it. The manual warns that watchpoints on local variables "may fail to be recreated."

### Level 2: a script you run in one command

Write the probe as a file and run gdb non-interactively. [MANUAL]{.manual}

```
gdb -q -batch -x gdb/01-invariant.gdb ./gateway
```

* `-x FILE` runs the commands in the file as if you had typed `source FILE`.
* `-batch` "exit with status 0 after processing all the command files", and turns off paging and confirmations.
* `-ex 'COMMAND'` runs a single command and can be repeated.
* "An error in any command terminates execution of the command file", so a typo stops the run instead of quietly doing nothing.

lldb: `lldb -b -s lldb/01-invariant.lldb ./gateway`. [RAN]{.ran} Every probe in the book's lab is a file you can run this way. Start with `set pagination off` in gdb scripts so output is not held at a prompt.

**Do not depend on a project-local `.gdbinit`.** GDB reads a `.gdbinit` in the current directory last, but it will not blindly run files from untrusted places (the `auto-load safe-path` setting), so it may be refused and print a warning. Passing the script with `-x` always works.

### Level 3: Python for conditions that need real code

When a condition is too awkward for one expression, write it as a Python class. A `gdb.Breakpoint` subclass overrides `stop()`: return `True` to stop, `False` to keep running. [MANUAL]{.manual}

```python
import gdb

class StaleMissed(gdb.Breakpoint):
    def stop(self):
        etype = str(gdb.parse_and_eval("e.type"))
        missed = int(gdb.parse_and_eval("missed_"))
        return etype.endswith("Heartbeat") and missed != 0

StaleMissed("gateway.cpp:81")
```

Rules from the manual: inside `stop()` you must not step, change the frame, or add or delete breakpoints. Reading and printing are what it is for. The lldb equivalent is a callback function that returns `False` or `True`, which you have already seen in `lab/lldb/probes.py`. [RAN]{.ran}

This is also where "gdb Python API for testing and team workflows" starts to pay off. A probe file that sits next to a test is a regression check you can run against a live process.

### Level 4: a nicer screen

**gdb-dashboard** is "a standalone `.gdbinit` file written using the Python API that enables a modular interface showing relevant information about the program being debugged." Per its README, it installs by downloading one file, and "the dashboard will appear automatically every time the inferior program stops." It needs a gdb built with Python.

::: trap
**Check before you install anything on a work machine.** gdb-dashboard is a file downloaded from the internet that gdb then executes. Ask your team or IT whether it is allowed, and if so use a reviewed, pinned copy. To find out whether your gdb has Python: `gdb -batch -ex 'python print(1)'`. To find out whether it is already set up: look for `~/.gdbinit` and ask what your team uses.
:::

**VS Code** shows the same information in panes (Variables, Call Stack, Watch) and lets you set breakpoints in the file you are editing. Its breakpoint types include: [SEC]{.sec}

* **Conditional**: an expression, a hit count, or "wait for breakpoint". The docs note that hit-count syntax "varies by debugger."
* **Logpoints**: "writes a message to the Debug Console without pausing execution." Write text with expressions in curly braces, such as `heartbeat t={e.tick}`. Available only if the debugger extension implements them.
* **Data breakpoints**: pause when a variable changes. The docs say the options "depend on the debugger" and do not say which debuggers support them. Try it with your setup. If the menu is not offered, use a raw gdb command.
* **Raw commands**: in the Debug Console, the C/C++ extension lets you run gdb commands with the `-exec` prefix (for example `-exec watch -l missed_`). The docs warn this is "untested and might crash VS Code in some cases."

Appendix A has a step-by-step setup for VS Code over SSH, which you said is on your backlog.

## Conventions that keep a probe library useful

* **One file per probe.** Name it by task and behavior: `TKT-1234-stale-missed.gdb`.
* **Put the card reference and the prediction in the header comment.** The next person needs the *question*, not only the commands.
* **Use function names over line numbers when you can** (`break LinkMonitor::on_event`). Line numbers drift when the file changes. If you must use a line, say which line it is in a comment.
* **Delete watchpoints near the end of the run** so they cannot fire during shutdown.
* **Keep them in the repository** (for example `tools/probes/`) or in your own notes, whichever your team prefers. Commit them with the fix that they proved.

## Check yourself

* What does `-batch` change about how gdb runs?
* When would you write a Python probe instead of a conditional expression?
* Why is a probe file better than a screenshot in a ticket?
