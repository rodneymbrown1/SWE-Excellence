<section class="part-title"><p class="pn">Part 2</p><div class="ph">Understand</div><p>Steps 1 and 2. Watch the program, then build enough confidence in what it should do that you can name the data and conditions.</p></section>

# Step 1 · Run it {.chapter}

<p class="lede">Before you read code, before you open a debugger, run the program and look at what it does. This is the cheapest probe there is.</p>

## Why it comes first

Mike Shah and Chris Croft-White open their method for unfamiliar code bases with "Step 1: run your program." David Agans's second rule is "Make It Fail": you cannot debug what you cannot produce. Andreas Zeller's TRAFFIC steps start with *Track* and *Reproduce*. Three sources, one instruction. A high-level feel for what the program actually does is the foundation everything else stands on.

For a **bug**, running it means reproducing the failure. For a **feature**, it means seeing the nearest existing behavior. For an **understanding** task, it means seeing the behavior you must explain.

## Build for the debugger

Debuggers show you names only if the program carries them.

| Build setting | What it does | If you skip it |
|---|---|---|
| `-g` | Adds symbols: variable names, types, line numbers | You see addresses, not names |
| `-O0` | No optimization | Variables show `<optimized out>`, lines jump around |
| CMake: `-DCMAKE_BUILD_TYPE=Debug` | Sets both for you | Release builds usually have neither |

Check that symbols are present before you start:

```
gdb -batch -ex "list main" ./yourprogram      # prints source lines if symbols are found
```

If your project builds in release mode only, ask how to get a debug build. Never debug a different binary from the one that shows the problem without saying so in your notes.

## What to write down: the Run Record

Three minutes, and it saves hours.

```
RUN RECORD
Command:   ./gateway --max 400
Directory: lab/
Input/config: none (deterministic event source)
Build:     -O0 -g, commit abc123
Output saved to: run1.log
What I expected: ...
What I saw:      ...  (copy the exact line)
First thing that looks wrong: ...
```

## Make it repeatable

1. **Fixed input.** Same data, same seed, same config every run.
2. **Finite run.** An endless loop needs a way to stop: a `--max N` flag, `timeout 20 ./prog`, or Ctrl-C after N seconds. Save the output.
3. **Run it twice and compare.**

```
./gateway --max 400 > run1.log 2>&1
./gateway --max 400 > run2.log 2>&1
diff run1.log run2.log && echo "deterministic"
```

If the two runs differ, your first discovery is that the behavior is **non-deterministic** (timing, threads, uninitialized data). That changes the plan: see type B7 in chapter 18.

## Read the output as a stream of state

Do not just skim. Look for four things:

* **Transitions.** Lines that say something changed (`Up -> Degraded`).
* **Counts.** Numbers that should add up or should not grow.
* **Timing.** What happened *after* what, and how long it took.
* **The first oddity.** Mark the earliest line that looks wrong. Everything before it is probably fine.

::: try
**Lab.** Build and run the practice program. Read the output. Before you open any code, write one sentence about what looks wrong and why.
```
cd lab && make && ./gateway --max 400
```
:::

This is what comes out. [RAN]{.ran}

```out
[t=  3] Down     -> Up       (missed=0 good=3)
[t= 23] Up       -> Degraded (missed=4 good=0)
[t= 27] Degraded -> Down     (missed=8 good=0)
[t= 29] Down     -> Up       (missed=0 good=3)
[t=123] Up       -> Degraded (missed=4 good=0)
[t=127] Degraded -> Down     (missed=8 good=0)
[t=134] Down     -> Up       (missed=0 good=3)
final: state=Up forwarded=54 dropped=6 data_seen=153
```

Seven state changes. You do not know yet which ones are wrong. You cannot know without the requirements, and that is step 2. But you can already say something useful: "at t=27 the link went Down only four ticks after it went Degraded." Keep that line; chapter 21 comes back to it.

## Anchor on `main`

When the code base is large, find where it starts. From `main` you often learn the architecture: is there an event loop, are plugins loaded, what happens before and after the loop.

```
rg -n "int main" src/            # find the entry point
rg -n "while *\(" src/ | head    # find loops near it
```

::: note
`cloc` counts lines of code per language. Run it once to size the job. A million lines is roughly 18,000 pages. You will not read it all, and chapter 5 explains why you do not need to.
:::

## When the program never ends

An event-driven system is not supposed to finish. For step 1 you only need a **window** of behavior:

* Add or use an event limit (`--max`).
* Or capture a fixed time: `timeout 30 ./prog > run1.log 2>&1`.
* Or Ctrl-C when the symptom appears, and note the last lines.

Part 4 shows how to look *inside* such a loop without stepping through it.

## Check yourself

* Can you run it, on demand, the same way twice?
* Did you save the exact line that looks wrong?
* Is the build a debug build (`-O0 -g`)?
