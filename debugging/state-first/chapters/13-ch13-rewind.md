# Rewind, snapshots, and crashes {.chapter}

<p class="lede">The state is bad <em>now</em>, but the cause was earlier. There are three ways to get back to it: run again with a better probe, record and rewind, or examine a snapshot taken at the moment of failure.</p>

## Option 1: run it again (the cheap rewind)

This is the one you will use ninety percent of the time. If step 1 made the run **repeatable**, you can simply restart and follow the data from the beginning to the point where it goes bad. In your words: note the thing that is off, restart, and follow that variable from initialization to the bad state.

1. A FILTER probe finds the first bad moment (say, tick 26, `missed_ = 7`).
2. Note the **tick or count** at which it happened.
3. Restart. Put a TRAP or LOG on the variable, and an **ignore count** or **arm** so you only look near the bad moment.

This is why determinism matters so much. A bug you can replay exactly is a bug you can bisect.

## Option 2: record and replay

When you cannot predict where to look until after you have seen the failure, record the whole run and move backward through it.

**rr** records a Linux run and replays it deterministically inside gdb. [SEC]{.sec}

```
rr record ./prog args        # run once, recorded
rr replay                    # gdb, connected to the recording
```

Under rr, "gdb's `reverse-continue`, `reverse-step`, `reverse-next`, and `reverse-finish` commands all work." The pattern for *who wrote this bad value* is the one from the rr wiki: [MANUAL]{.manual}

```
(gdb) break the_line_where_it_is_wrong
(gdb) continue                    # arrive at the bad state
(gdb) watch -l mRect.width        # watch that location
(gdb) reverse-continue            # run backward to the write that set it
```

The wiki says `watch -l` "is important", for the reason in chapter 11: it watches the memory, not a scope.

**Limits** from the rr site: it "requires a reasonably modern x86 CPU or certain ARM CPUs (Apple M1+)", "emulates a single-core machine", and the recorded executable must not change before replay. Single-core emulation can hide or change the behavior of timing-dependent bugs. I do not know whether your Linux server exposes what rr needs (virtual machines sometimes do not), so test it before you plan around it.

**gdb's own `record`** gives reverse commands without rr: [MANUAL]{.manual}

```
break main
run
record
continue
reverse-continue
```

The manual says "not all target environments can support reverse execution", and that reverse-next may fail "if the code is too heavily optimized." Recording in gdb is slow, so use it on short windows (start `record` shortly before the event you care about).

::: note
**Embedded targets.** Reverse execution needs a target that supports it. On most microcontrollers over a hardware probe it is not available. Use option 1 (repeatable runs with probes) or option 3.
:::

## Option 3: a snapshot at the moment of failure (core dumps)

A **core dump** is the memory and thread state of a process written to a file when it crashes. You cannot run it. You can inspect it: stack of every thread, every variable in every frame. [UNTESTED]{.unt}

```
ulimit -c unlimited            # allow core files in this shell (Linux)
./prog                         # crashes, writes a core file
gdb ./prog core                # load program and core together
(gdb) bt                       # where did it die?
(gdb) frame 2                  # select a frame
(gdb) print *this              # look at that object
(gdb) info threads
(gdb) thread apply all bt      # the stack of every thread
```

Where the core file goes is a system setting (`cat /proc/sys/kernel/core_pattern`). You need the **same binary, built with symbols**, that produced the core.

Your notes from the GDB Deep Dive talk describe the embedded version of this: after release, a device that crashes in the field sends a core dump, and each RTOS thread (main thread, system workqueue, service threads) has its own stack to inspect. You said you will not be doing that while training, and may later. All of the *reading* skills in chapter 12 carry over.

## Crashes: the first move

For a crash (a signal such as SIGSEGV), the first move is simple.

1. Run under the debugger. It stops at the signal. Run `bt`.
2. The crashing line is rarely the cause. Walk **up** the stack (`up`) and look at which pointer or index is bad.
3. Ask: *where did that value come from?* That is a TRAP question. Restart and `watch -l` it, or use rr and `reverse-continue`.

`catch signal` stops on a signal without having to wait for the crash, and `catch throw` stops where a C++ exception is thrown rather than where it is caught. [MANUAL]{.manual}

Compilers can also help find memory errors before they become crashes. AddressSanitizer (`-fsanitize=address`) is the standard first tool for memory bugs in C and C++. [UNTESTED]{.unt}

## Which option when?

| Situation | Use |
|---|---|
| You can reproduce it every time | Option 1: run again with a probe |
| You see it, but cannot guess where to probe | Option 2: record, then rewind |
| It only happens in the field, or once in a thousand runs | Option 3 (core dump), or record in a loop until it fails |
| It crashes | Debugger stops at the signal, then walk up and trace the bad value back |

## Check yourself

* What property of step 1 makes option 1 work?
* Why is `watch -l` needed before `reverse-continue`?
* What can you do with a core dump that you cannot do with a log?
