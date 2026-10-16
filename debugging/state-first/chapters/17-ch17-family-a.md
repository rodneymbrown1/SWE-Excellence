# Family A · Understand tasks {.chapter}

<p class="lede">"I don't know how this code works." "I don't know where this is called." "What variable controls this?" These are your first three scenarios. The output is not a change to the code. It is a map you can trust.</p>

**What every A task produces:** a short written summary, one diagram (state by event table, call list, or data path), and a Behavior Card whose DEFINE lines you can *predict* against. You are done when you can pass the Confidence Gate for the thing you were asked to understand.

::: pb
### A1 · Who calls this? Is that the only place?
**Looks like** "Where is `LinkMonitor::on_event` used? Does anything else call it, under conditions I have not considered?"

**State signature** A function F is reached from some context. You want the set of contexts and the condition that selects each.

**First probe** LOG the callers: `break F`, commands `silent`, `bt 2`, `continue`. Run a full scenario and tally with `sort | uniq -c`. Add a static search (`rg "F("`, *Find All References*).

**Then** For each caller, find the condition that leads to it (read the caller, or FILTER at the call site). Look for **rare callers**: filter by caller (`$_caller_matches`) or break at a call-site line.

**Done when** You have a list of call sites, each with its condition, and each marked *seen at runtime* or *only seen in code*.

**Trap** Runtime shows only what ran. A caller that your scenario never triggers stays invisible. Compare against the static list.
:::

::: pb
### A2 · How does this module work?
**Looks like** "I just got this code. I don't know what it does."

**State signature** The module holds state and reacts to events. The behavior is its state-by-event table.

**First probe** TRAP and LOG the writes to the module's state (chapter 11). In parallel, log which events arrive and in what state.

**Then** Build the table of what *actually* happened (state by event). Put it beside the table you built from the requirements (chapter 5). Every cell that differs is a question. Every cell that never appeared is a path you have not exercised.

**Done when** You can fill the state-by-event table and predict the next transition before it happens.

**Trap** Reading every function in order. Start from the state variable, not from `main`.
:::

::: pb
### A3 · What variable controls this behavior?
**Looks like** "I need to adjust something but I do not know which variable affects it." (And the name appears a hundred times.)

**State signature** An output O changes (or fails to). O is computed from inputs.

**First probe** TRAP the *output*: `watch -l O`, with a backtrace log. Each write shows the line that computed it.

**Then** Walk the dependency chain backward. At the writing line, read the variables it uses (the inputs). Repeat on each input until you reach a configuration value, a constant, or an external input. **Count the distinct variables on the way.** Test each candidate by changing it by hand (`set var`) and watching whether O responds.

**Rate the complexity** (this book's heuristic): 1 to 2 variables, simple. 3 to 5, moderate. More than 5, high. **Can I change one variable in one method?** Yes if one `set var` at one place gives the behavior you want.

**Done when** You can name the variable, the line that reads it, and the experiment that shows it controls O.

**Trap** Picking by name. Pick by *effect*.
:::

::: pb
### A4 · Where does this data go?
**Looks like** "What happens to this value between input and output?" Possibly across a messaging system.

**State signature** One value travels through several stages.

**First probe** **Tag the value.** Feed in a distinctive input (a sequence number, an easily recognized value). FILTER or LOG at each stage boundary on that tag.

**Then** The sequence of log lines *is* the data path. Draw it. Mark every stage where the value is copied, changed, or dropped.

**Done when** You have a data path diagram where every arrow is backed by a log line.

**Trap** Following the variable *name*. Names change across stages; the tagged value does not.
:::

## The Understand deliverable

A one-page summary you could hand to the next person:

```
MODULE:     LinkMonitor
PURPOSE:    Decide link health so data flows only on a healthy link.
STATE:      state_ (Down/Up/Degraded), missed_, good_
EVENTS:     Tick, Heartbeat, Data      (table attached)
CALLED BY:  Gateway::dispatch (every event); Gateway::flush_burst (rare: Data with payload >= 99)
WRITERS:    on_tick (2 sites), on_heartbeat (2 sites)
UNKNOWNS:   ...
```

Chapter 22 builds this one for real, for the practice program.

## Check yourself

* For A1, why is a runtime log not enough on its own?
* For A3, how does counting variables help you decide whether a one-line change is realistic?
