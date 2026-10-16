# When you do not know the names yet {.chapter}

<p class="lede">If you are new to a code base, you do not know which function, which variable, or which condition. So your first task is investigating and finding the missing information. This chapter gives every <code>?</code> on the card a probe.</p>

## The discovery loop

You cannot write a condition about a variable you cannot name. So:

1. Write the card as far as you can. Mark each missing name `?`.
2. For each `?`, pick the discovery probe from the table below.
3. Run the probe. Write the answer into the card.
4. Repeat until no `?` blocks you.

Each probe is cheap and answers one question. None of them requires reading the whole system.

## Discovery probes

| The `?` is… | Probe | Command |
|---|---|---|
| **Where is the code for this behavior?** | Search for visible text from the output: log strings, error messages | `rg -n "recovered" src/` |
| | Break on the **output function** and read the backtrace (walk from effect to cause) | `break printf`, `run`, `bt` |
| | List functions matching a name pattern | `info functions Link` (gdb) / `image lookup -r -n Link` (lldb) |
| **Who calls this function?** | Break on it and look at the stack | `break F`, `run`, `bt` |
| | Log every caller, then count them | commands list below |
| **Which data does it use?** | Look at arguments, locals, and the object | `info args`, `info locals`, `print *this` |
| | Show a type's fields | `ptype LinkMonitor` (gdb) / `type lookup LinkMonitor` (lldb) |
| **What values does it take?** | Log the value each time, then tally | `dprintf`, then tally the output with `uniq -c` |
| **Who changes this variable?** | Watchpoint with a log (chapter 11) | `watch -l expr` |
| **When does it run?** | Count hits; log with a tick or timestamp | breakpoint `info breakpoints` hit counts |

### Break on the output

When you know *what the program says* but not *where it says it*, break on the thing that does the saying. [RAN]{.ran}

```out
(lldb) breakpoint set -n printf
(lldb) run --max 400
(lldb) bt 5
* frame #0: libsystem_c.dylib`printf
  frame #1: gateway`LinkMonitor::announce(this=…, from=Down) at gateway.cpp:128:5
  frame #2: gateway`LinkMonitor::on_heartbeat(this=…) at gateway.cpp:115:9
  frame #3: gateway`LinkMonitor::on_event(this=…, e=…) at gateway.cpp:78:34
  frame #4: gateway`Gateway::dispatch(this=…, e=…) at gateway.cpp:159:14
```

One command took you from a log line to the function that prints it, the function that decided to print it, and the loop that called both. In gdb it is the same idea. [MANUAL]{.manual}

```
break printf
run --max 400
bt 5
```

### Log every caller, then count

"Is this the only place it is called?" Run, log the callers, tally them. [MANUAL]{.manual}

```
break LinkMonitor::on_event
commands
  silent
  bt 2
  continue
end
run --max 400
```

Save the output and run `grep "Gateway::" out.txt | sort | uniq -c`. You get the callers seen at runtime and how often. **Limit:** this only shows what *ran*. A path that was not exercised stays invisible, so complement it with a static search (`rg "on_event("`, *Find All References*). Chapter 22 does this for real.

## Reading a backtrace

`bt` lists **frames**, innermost first. Frame 0 is where you are stopped. Frame 1 called frame 0, and so on. For each frame you can look at its own arguments and locals (chapter 12).

```
#0  LinkMonitor::on_event   <- you are here
#1  Gateway::dispatch        <- who called you
#2  Gateway::run             <- and who called them
#3  main
```

A backtrace answers *how did I get here*, which is the control-flow question. The next question, *where did this data come from*, is answered with watchpoints.

## When the code base is large

* Start from an **effect** you can see (output, a file, a message) and walk back.
* Start from a **function you already know** and walk out.
* Use the **slice rule** (chapter 5): you only need the code that touches your data.

::: note
**Messaging systems.** When data goes out of a class through a message and comes back, the data path is broken in the code but not at runtime. Break on the *send* function and on the *receive* handler, log a distinctive field (a sequence number, an id) at both, and you can follow one message across the gap. Chapter 17 (type A4) uses the same idea.
:::

## Check yourself

* For each `?` on your card, which probe from the table will answer it?
* Why does a backtrace from an output call find code faster than reading?
