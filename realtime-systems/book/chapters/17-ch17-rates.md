# Rates and end-to-end latency {.chapter data-part="PART 4 · FLOW"}

<p class="lede">Each component has a rate. Why that rate? And when data crosses from a fast component to a slow one, or through a chain of three, how old is it when it arrives? These questions decide whether a system whose every component meets its deadline still misses its requirement.</p>

## Why a component runs at its rate

| Driver | The question | Typical consequence |
|---|---|---|
| **Responsiveness** | how soon must the world see a reaction? | a lower bound on the rate (and an upper bound on latency) |
| **Input data rate** | how fast does the data arrive, and does an extra run add information? | running faster than the input only repeats work; running slower drops information |
| **Dynamics of the controlled thing** | how fast can it change? | control stability needs a minimum rate |
| **CPU budget** | what is the utilization (chapter 8)? | an upper bound on the rate |
| **Jitter tolerance** | how much variation in the period is acceptable? | a limit on the priority and priority-inversion budget |
| **Compatibility** | what rates do neighbours use? | harmonic rates simplify everything (below) |

**A rule from control theory.** Åström and Wittenmark's rule of thumb, quoted in Cervin's thesis (2003): the sampling interval *h* should satisfy **ω_c·h = 0.2–0.6**, where ω_c is the closed-loop bandwidth. "A real-time system where the product ω_c·h is small for all control tasks will be less sensitive to scheduling-induced latencies and jitter, but it will also consume more CPU resources." The same thesis states that variation of the sampling interval below **10%** of nominal "need not be compensated for", and that latency and jitter together "degrade the control performance". You will usually be *given* the rate; this tells you what you are trading when you are asked to move it.

## Harmonic rates

Rates are **harmonic** if each is a whole multiple of the slower ones: 100, 50, 25, 10 Hz. Benefits: the hyperperiod is the longest period (ch. 5); RM can reach U = 1 (ch. 8); samples line up, so a slow task's input is exactly the *n*-th fast sample; end-to-end patterns repeat every long period. Non-harmonic rates (7, 11 and 13 ms; hyperperiod 1,001 ms) move relative phases continuously, which finds rare collisions but makes tests slow to cover them (chapter 12).

## Crossing rates

| From → to | Problem | Common choices |
|---|---|---|
| **fast → slow** (100 Hz → 10 Hz) | which of ten samples does the slow task use? | take the latest · average · decimate · keep a window |
| **slow → fast** (10 Hz → 100 Hz) | what does the fast task use between updates? | hold · extrapolate · interpolate (adds latency) |
| **unrelated rates** | aliasing, phase drift, occasional double/zero delivery | resample with timestamps |

Pick **one** rule per crossing and write it down. An unwritten crossing is an implicit decision made by whichever component reads last.

## End-to-end latency is not the sum of response times

Consider a chain: a sampling task (T = 10 ms), a filter (T = 20 ms), a controller (T = 40 ms), each reading the latest value the previous one wrote. Each task's response time may be a few milliseconds; the *data* waits for the next period of every stage.

{{fig:e2e-chain | Worst case for a signal that appears just after a stage has read its input: it waits a full period (hatched) and then a response time (solid) at every stage: 80 ms in total against 10 ms of execution.}}

Feiertag, Richter, Nordlander and Jonsson (2008) formalised this for register-based systems with periodic sampling, and showed that "different path semantics" give different numbers: **data age** (how old is the newest value when it is used? — what control engineers need) and **reaction time** (how long until a stimulus has some effect? — what body electronics needs). "Because the two can differ, a clear distinction is mandatory." This book uses a loose bound, in the spirit of their work and not a quotation: for a register-based chain of tasks,

**worst-case data age ≲ Σ (T_i + R_i)**

and checks it by measurement rather than relying on it. A stricter analysis exists and depends on phase and on how data is passed. The lesson that survives all variants: **end-to-end latency is dominated by the sampling delays at the rate boundaries**. Faster stages, aligned phases, and **timestamping at the source** shrink or reveal it.

::: rule
**Rule.** Stamp each datum with the time it was *measured*, at the place it was measured, and carry the stamp with it. A consumer that can compute the **age** of its input can check its requirement; one that cannot is guessing.
:::

## When the timestamp is wrong

::: case
**Ingenuity Mars helicopter, Flight 6, 22 May 2021.** About 54 seconds into the flight, NASA/JPL reported, "a glitch in the pipeline of images delivered by the navigation camera" caused a single image to be lost, and "all subsequent navigation images" to be "delivered with an erroneous timestamp". The navigation filter kept correcting for errors that were not there; "large oscillations ensued" (roll and pitch excursions above 20 degrees) and the helicopter landed safely, aided by a safeguard that ignored images during the descent. In a follow-up post, the team's hypothesis was that "the large CPU load involved in capturing the RTE's 13-megapixel color images, could result in rare instances of navigation camera images being dropped in the pipeline", and the fix would "address the Flight 6 anomaly, where image timing delays manifested into aircraft estimation and control challenges."
**What it teaches.** (1) A **dropped message plus a position-based timestamp** corrupts every later message: the stamp must travel with the datum. (2) The proximate trigger was **CPU load** causing rare drops, so budget the load of an optional feature, not only the baseline. (3) A consumer should **check the consistency of timestamps** (a gap or a repeat means a loss) and degrade rather than act. The posts do not say which software layer assigned the timestamps.
:::

## Phase and the clocks that disagree

Two periodic activities derived from the same clock have a **fixed phase**; from independent clocks, a **drifting** one. [RAN]{.ran} In Lab R10 the sensor runs from its own 997 µs clock while control runs at 10 ms ticks; a read-twice race collided with the filter in 47 of 309 cycles and drifted with time. Had they been phase-locked, it would have collided *every* cycle or *never* — either of which passes or fails a short test for the wrong reason (chapter 12).

## A rate review in five questions

1. What is the **source** rate, and is it exact or does the sensor have its own oscillator?
2. What is the **required reaction time** end to end, and what is its source (a person, a spec, a plant)?
3. Which rate crossings exist, and which rule applies at each?
4. What is the **worst-case data age** at the consumer, from the formula, and what did the *measurement* give?
5. What happens when a message is missing, repeated, or out of order?

## Check yourself

::: check
1. A chain samples at 5 ms, filters at 10 ms and commands at 20 ms with responses of 1, 2 and 3 ms. Compute the loose worst-case data age. Which stage change reduces it most?
2. A 50 Hz task uses the latest of a 400 Hz stream. What is the worst-case age of the sample it uses, ignoring jitter?
3. Where is the timestamp on a message in your system assigned? By what clock?
:::

**Lab links.** R10 (timestamps and latency histograms), H5 (reporting latency honestly).
