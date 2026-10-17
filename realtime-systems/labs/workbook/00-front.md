# Read this first

<p class="lede">Sixteen labs, in the order of the book. Each one makes you <b>predict</b>, <b>run</b>, and <b>compare</b>. The output you will see is real and repeatable: the host labs are deterministic simulations or small C programs, and the RTOS labs run on an emulator with a deterministic instruction-count clock, so your numbers will match the printed ones.</p>

## The method of every lab

1. **Read the goal and the book chapter** it names.
2. **Predict.** Write your answer to the *Predict first* questions before you run anything. A wrong prediction is the lesson.
3. **Run** the commands exactly as written.
4. **Compare** your run with the printed output; answer the *Questions*.
5. **Extend.** Change one thing and predict again.

## Lab map

| Lab | Topic | Book ch. | Runs on | Time |
|---|---|---|---|---|
| **0** | Setup and smoke test | — | laptop + emulator | 20 min |
| **H1** | A loop and its clock; tick wrap; the Patriot arithmetic | 2, 3 | laptop (C, Python) | 30 min |
| **H2** | Cyclic executive and the domino effect | 5 | laptop (C) | 20 min |
| **H3** | Scheduler workbench: bounds, RTA, EDF, overload, inversion | 8–11, 13 | laptop (Python) | 60 min |
| **H4** | Queues, bursts, sizing; the Apollo pool toy | 15, 11 | laptop (Python) | 30 min |
| **H5** | Honest latency: coordinated omission | 20 | laptop (Python) | 20 min |
| **R0** | Two tasks on FreeRTOS | 6 | QEMU | 15 min |
| **R1** | Delays, drift and the tick | 3 | QEMU | 20 min |
| **R2** | Predict, then measure a task set | 9 | QEMU | 40 min |
| **R3** | Priority inversion on a real kernel | 13 | QEMU | 40 min |
| **R4** | Interrupt → queue: size it and break it | 15 | QEMU | 30 min |
| **R5** | Three watchdogs, one fault | 19 | QEMU | 30 min |
| **R6** | Stack, heap, fragmentation, overflow | 14 | QEMU | 30 min |
| **R7** | Tick wrap | 3 | QEMU | 20 min |
| **R8** | Trace, run-time stats, interrupts in the analysis | 4, 20 | QEMU | 40 min |
| **R9** | gdb on the target without wrecking the timing | 20 | QEMU + gdb | 45 min |
| **R10** | Capstone: four planted defects | 24 | QEMU | 2–3 h |

## Where things are

```
realtime-systems/
  labs/host/           H1–H5 (C and Python)         rtsim.py = the scheduler workbench
  labs/rtos/           R0–R10, common/ (BSP, config), run.py, gdb/
  labs/tools/          trace2gantt.py, lathist.py
  labs/transcripts/    every output printed in this workbook (regenerate with the capture scripts)
  labs/third_party/    FreeRTOS-Kernel V11.3.2 (fetched by fetch-deps.sh; not in git)
```

## Marks

[RAN]{.ran} output was produced by the command shown, on the project machine. [MANUAL]{.manual} was not executed. **Predict first** questions have answers in Appendix A, in the same order.

::: trap
**What the RTOS labs do and do not prove.** The emulated CPU runs at one instruction per 32 ns of *virtual* time with the 25 MHz timer driven by that clock. The numbers (µs) are not any real board's. What transfers are the *relationships*: model against measurement, priority protocol against inversion, queue depth against loss.
:::
