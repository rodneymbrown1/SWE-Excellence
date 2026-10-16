# Breakpoints and conditions {.chapter}

<p class="lede">A breakpoint is a place. Everything else in this chapter is how to make that place stop only when it matters, or not stop at all.</p>

Commands are gdb first. lldb versions are shown where I ran them. [RAN]{.ran} marks lldb output I captured; [MANUAL]{.manual} marks gdb syntax checked against the manual only.

## The basics

| Goal | gdb | lldb |
|---|---|---|
| Stop at a function | `break Gateway::run` | `breakpoint set -n Gateway::run` [RAN]{.ran} |
| Stop at a file and line | `break gateway.cpp:81` | `breakpoint set -f gateway.cpp -l 81` [RAN]{.ran} |
| List breakpoints and **hit counts** | `info breakpoints` | `breakpoint list` [RAN]{.ran} |
| Turn off, on, remove | `disable 2`, `enable 2`, `delete 2` | `breakpoint disable 2`, `enable 2`, `delete 2` |
| Continue, finish the function | `continue`, `finish` | `continue`, `finish` |

`finish` runs until the current function returns and prints the returned value. It is the quickest way to ask "what did this call give back?"

## FILTER: conditions

```
break gateway.cpp:81 if e.type == EventType::Heartbeat && missed_ != 0       [MANUAL]
condition 1 missed_ > 5        # add or change a condition on breakpoint 1
condition 1                    # remove it
```

lldb [RAN]{.ran}:

```
breakpoint set -f gateway.cpp -l 81 -c 'e.type == EventType::Heartbeat && missed_ != 0'
```

This stopped exactly at t=26 with `state_ = Degraded, missed_ = 7`.

::: trap
**An ignore count switches the condition off.** The manual says: "If a breakpoint has a positive ignore count and a condition, the condition is not checked." So `ignore 1 100` plus a condition means "skip the first 100 times the location is *reached*", not "skip the first 100 times the condition is true." If you need the second, count with a variable (below).
:::

## Ignore counts: skip the warm-up

```
ignore 1 1000        # breakpoint 1: let it pass the next 1000 times      [MANUAL]
```

lldb [RAN]{.ran}: `breakpoint set -n LinkMonitor::on_tick -i 3` skipped three hits and stopped on the fourth. `breakpoint list` then showed `hit count = 4`.

Hit counts are free information. After a run, `info breakpoints` tells you how many times every location was reached, including breakpoints that never stopped you.

## One-shot breakpoints

| Goal | gdb | lldb |
|---|---|---|
| Stop once, then remove | `tbreak LOC` | `breakpoint set … -o true` [RAN]{.ran} |
| Stop once, keep it disabled | `enable once N` | |
| Stop the next C times | `enable count C N` | |

Use one-shots to get *into* the right context (for example, to read an instance's address) without leaving a breakpoint behind.

## LOG: print without stopping

**`dprintf`** is a breakpoint that prints and continues. [MANUAL]{.manual}

```
dprintf gateway.cpp:108,"heartbeat t=%d state=%d missed=%d\n", now_, (int)state_, missed_
```

**A command list** gives you more control. The manual's own example:

```
break foo if x>0
commands
silent
printf "x is %d\n",x
cont
end
```

Rules from the manual: `silent` must be the first command; "any other commands in the command list, after a command that resumes execution, are ignored", so put `continue` **last**. Use `echo`, `printf`, or `output` for exact formatting.

lldb has no `silent` command list that prints reliably in batch mode, so I used **Python callbacks**. A callback returns `False` to keep running (a log line) or `True` to stop. [RAN]{.ran}

```python
def log_state_write(frame, bp_loc, internal_dict):
    this = frame.FindVariable("this")
    state = this.GetChildMemberWithName("state_").GetValue()
    print("  state_ written -> %s" % state)
    return False          # keep running
```

Attach with `breakpoint command add -F probes.log_state_write 1` (or `watchpoint command add -F …`). The full file is `lab/lldb/probes.py`.

## COUNT: tally with a variable

```
set $n = 0
break LinkMonitor::on_heartbeat
commands
  silent
  set $n = $n + 1
  continue
end
break Gateway::summary
commands
  silent
  printf "heartbeats handled: %d\n", $n
end
```

[MANUAL]{.manual} The same idea with an lldb callback printed `heartbeats handled: 160` for `--max 400`. [RAN]{.ran}

A convenience variable (`$name`) is created when you first assign it and is void until then. `init-if-undefined $n = 0` sets it only if it does not exist yet.

## Scope filters: only this caller, instance, or thread

**By caller** (needs a Python-enabled gdb): [MANUAL]{.manual}

```
break LinkMonitor::on_event if $_caller_matches(".*flush_burst")
```

`$_caller_is(name)` checks the immediate caller. `$_caller_matches(regex)` matches a pattern. `$_any_caller_is(name, N)` and `$_any_caller_matches(regex, N)` check all frames up to N levels. The manual does not say whether the regex is anchored at the start, so write patterns like `".*flush_burst"` and confirm the first time you use it. If you have no Python, break at the **call site** instead (`break gateway.cpp:170`).

**By instance.** When there are many objects of one class, pick one by its address and condition on it:

```
break LinkMonitor::on_heartbeat
run
# stopped in the instance you care about:
set $target = this
condition 1 this == $target                                                  [MANUAL]
```

In lldb: `p this`, then `-c 'this == 0x16fdff02c'`. [RAN]{.ran} (I recorded the address with a one-shot breakpoint and printed it.) The address changes each run, so redo this step each session.

**By thread.** `break LOC thread N` limits a breakpoint to one thread. See the manual's *Thread-Specific Breakpoints* section; I did not read that page.

**By string.** `$_streq(name, "left")` compares text. Do not use `==` on `char*`.

## Other useful forms

| Goal | gdb |
|---|---|
| Breakpoint on every function matching a pattern | `rbreak ^Link` |
| Run to a line without a permanent breakpoint | `until 120`, `advance 120` |
| Save and reload your breakpoints | `save breakpoints probes.gdb`, later `source probes.gdb` |
| Breakpoint on a location not loaded yet | `set breakpoint pending on` |

`save breakpoints` is how a one-shot setup becomes a repeatable one (chapter 14). The manual warns that watchpoints on local variables "may fail to be recreated."

## Check yourself

* What is the difference between an ignore count and a counter variable?
* How do you read how many times a breakpoint was reached?
* You have 100 objects of one class. How do you stop only for one?
