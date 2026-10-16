<section class="part-title"><p class="pn">Part 3</p><div class="ph">State it</div><p>Step 3. Turn a human description of behavior into data and conditions, in the words a debugger understands.</p></section>

# Step 3 · State it {.chapter}

<p class="lede">You know the behavior. You do not yet know how to describe it as a state in a specific module, class, and method. This chapter gives you three building blocks and one page to write them on.</p>

## The translation problem

In your own words: "A bug is *we can't do this*, or *the system is doing the opposite of what we want*. It is behavior. So how do we describe the behavior in code?" And for a feature: describe the new behavior in terms of what has already been declared, defined, and implemented. You cannot use a watchpoint or a conditional breakpoint until you can do that translation, because you are not yet speaking the tool's language.

The translation has three parts.

## Declare, Define, Implement

::: note
These words come from C and C++, where they have exact meanings: a *declaration* introduces a name and a type, a *definition* creates the thing or gives it its value or body, and the *implementation* is the code that does the work. We borrow them with a slightly wider working meaning that maps onto what you write on the card.
:::

| Block | Working meaning | The question | Where you find it | Becomes, in the debugger |
|---|---|---|---|---|
| **DECLARE** | **What exists, and where.** The nouns: data, with names and types, and the places (module, class, function, file:line) they live. | *What are the things involved?* | Headers, class definitions, data members, enums. `ptype`, `info scope`. | What to `print` and what to `watch` |
| **DEFINE** | **What must be true, and when.** Initial values, legal ranges, the condition that turns the behavior on or off, the expected value and the observed value. | *When is the behavior right or wrong?* | Requirements, tests, `assert`s, constants, comments, the run output. | The `if` in a conditional breakpoint or watchpoint |
| **IMPLEMENT** | **What changes it, and how.** The verbs: the code that writes the data (writers), reads it (readers), the branch that decides, the calls that carry it. | *What changes the data, and under what branch?* | Function bodies. A watchpoint log. `bt`. | Where to put a probe, and where the fix or feature goes |

This is the same structure as the classic `{P} C {Q}` of Hoare and Meyer: if condition P holds before code C runs, condition Q holds after. **Declare** names the things inside P and Q. **Define** *is* P, Q, and the invariants. **Implement** is C. A bug is a state where Q (or an invariant) is false. The *infection* in Zeller's chain is the first such state.

## The Behavior Card {.pagebreak}

One card per behavior. It fits on one page. A blank, full-size copy is Card 2 in the Field Cards.

<div class="form">
<div class="hd">Behavior Card</div>
<div class="f"><b>Task:</b> ______________________ <b>Date:</b> ________ <b>Family / type:</b> A &#9633; B &#9633; C &#9633; ____</div>
<div class="f"><b>RUN</b> (command and the exact line you saw) <span class="ln s"></span></div>
<div class="f"><b>EXPECTED</b> (and who says so: ticket, spec, person) <span class="ln s"></span></div>
<div class="f"><b>PURPOSE</b> in one sentence <span class="ln s"></span></div>
<div class="f"><b>DECLARE</b>: what exists (name · type · file:line · which instance)<span class="ln s"></span><span class="ln s"></span><span class="ln s"></span></div>
<div class="f"><b>DEFINE</b>: before/trigger (P) <span class="ln s"></span> after/expected (Q) <span class="ln s"></span> always true (I) <span class="ln s"></span> observed instead (Q&prime;) <span class="ln s"></span></div>
<div class="f"><b>IMPLEMENT</b>: writers <span class="ln s"></span> readers <span class="ln s"></span> deciding branch <span class="ln s"></span> unknowns <b>?</b> <span class="ln s"></span></div>
<div class="f"><b>PROBES</b>: verb · command · <i>prediction</i> · if wrong <span class="ln s"></span><span class="ln s"></span></div>
<div class="f"><b>HYPOTHESES</b>: H1 <span class="ln s"></span> H2 <span class="ln s"></span></div>
</div>

### The card, filled in for the practice program

Here is the card you would write after steps 1 and 2 for the false `Down` in the gateway. [RAN]{.ran} means the run behind it is real. The probes it lists are run in chapter 21.

```
BEHAVIOR CARD — link falsely goes Down                 Family B (Fix) · type B1
RUN       ./gateway --max 400
          "[t= 27] Degraded -> Down     (missed=8 good=0)"
EXPECTED  R5: a link that is receiving heartbeats must not be declared Down.
          (source: the requirement comment at the top of gateway.cpp)
PURPOSE   Decide link health from ticks and heartbeats, so data is forwarded
          only when the link is usable.

DECLARE   what exists
  D1  LinkMonitor::state_   enum LinkState {Down,Up,Degraded}   gateway.cpp:132   (one instance)
  D2  LinkMonitor::missed_  int  ticks since the last heartbeat   gateway.cpp:133
  D3  LinkMonitor::good_    int  consecutive heartbeats           gateway.cpp:134
  D4  Event e               {type, tick, payload}  argument of LinkMonitor::on_event

DEFINE    what must be true
  P  (trigger)   a Heartbeat event is handled          e.type == Heartbeat
  Q  (expected)  missed_ == 0 afterwards                 (R5 and the Heartbeat column)
  I  (always)    after any Heartbeat is handled, missed_ == 0
  Q' (observed)  ?  at t=26 a Heartbeat arrived but the Down at t=27 says missed=8

IMPLEMENT what changes it
  writers of missed_   on_tick: ++ ; on_heartbeat: = 0 in SOME branches  (? which)
  readers of missed_   on_tick compares to 4 and 8 -> decides Degraded / Down
  ? Does every branch of on_heartbeat clear missed_?   -> probe P1

PROBES
  P1 FILTER      stop after on_event if e.type==Heartbeat && missed_!=0
                 predict: never fires.  If it fires: the invariant is broken, note state.
  P2 EXPERIMENT  at that stop, set missed_ = 0 and continue
                 predict: Degraded -> Up at t=27 instead of Down.

HYPOTHESES
  H1  a Heartbeat while Degraded does not clear missed_.        status: open
```

Notice what the card does. It turned "the link drops when it should not" into a **named variable** (`missed_`), a **condition** (`e.type == Heartbeat && missed_ != 0`), and a **place** (the end of `on_event`). That is the input a debugger needs.

## What makes a good card

* **Testable.** Every DEFINE line can be written as an expression that is true or false.
* **Named and located.** Each piece of data has a name, a type, and a file and line.
* **Expected value has a source.** You did not invent it. A ticket, a spec, a test, or a person said so.
* **Observed value is copied.** The exact line from the run, not a paraphrase.
* **Unknowns are marked `?`** and each `?` has a probe next to it (chapter 8).
* **One behavior per card.** Two symptoms get two cards.

## The card for each kind of task

Only the DEFINE section changes in spirit.

| Family | EXPECTED means | Q′ (observed) means |
|---|---|---|
| **A. Understand** | The behavior you must be able to explain | What you saw it do. The card is complete when Q is *explained*, not changed. |
| **B. Fix** | What the spec says should happen | The wrong state you saw |
| **C. Build** | The new behavior, written as before and after states | What happens today in the same situation (the nearest existing behavior) |

::: gate
**Gate 2: the Card.** Before probing: does every DEFINE line have a testable expression? Does every piece of data have a location? Is every unknown a `?` with a plan? If not, you will be setting breakpoints at random.
:::

## Check yourself

* Write one DEFINE line for your current task as an expression a debugger could evaluate.
* Which part of your card is the weakest: the nouns, the conditions, or the verbs?
