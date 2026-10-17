# Research folder — how to read it

This folder is the evidence behind **ON TIME** (book), the **Field Handbook**, and the **Lab Workbook**.
Anything in those documents that sounds like a fact about research, history, or a tool should be traceable to a file here.

| File | What it holds |
|---|---|
| `00-source-registry.md` | Every source: ID, URL, type, credibility tier, **verification status** |
| `01-what-real-time-means.md` | Definition of real-time, history of the loop → interrupt → executive → RTOS, Liu & Layland, Apollo's Executive |
| `02-time-clocks-measurement.md` | Clocks, ticks, wrap-around, jitter, latency, WCET, histograms, coordinated omission |
| `03-scheduling-and-analysis.md` | RM, EDF, response-time analysis, utilization bounds, overload, evidence on RM vs EDF |
| `04-synchronization.md` | Data races, priority inversion, deadlock, `volatile`, evidence on real concurrency bugs |
| `05-messaging-and-end-to-end.md` | Queues, backpressure, pub/sub, QoS, rates, end-to-end latency, lifecycle |
| `06-memory-reliability-observability.md` | Memory rules, stack, watchdogs, fault containment, tracing |
| `07-frameworks-and-resources.md` | FreeRTOS, Zephyr, cFS, F´, ROS 2, AUTOSAR/OSEK, Linux RT; best books/courses and why |
| `08-case-files.md` | The real-world incidents used in the book: what is verified, what is not |
| `09-claims-we-could-not-verify.md` | **Read this one.** What was not confirmed and how the documents treat it |
| `10-lab-environment-notes.md` | What was actually run for the labs, versions, and findings |
| `fetch.sh`, `pyget.py` | The helper used to download each source into its own directory |
| `_raw/<id>/` | Downloaded sources (untrusted third-party content; personal study copies; **not committed** — see `.gitignore`) |

## Rules used while researching

1. **Primary beats secondary.** A paper's own text > an official report > an official manual > a course slide > a blog > a search snippet.
2. **Quotes are short and exact**, and only used when the exact words were read in a downloaded source.
3. **Numbers carry their context** (sample size, system, year). A big number from a small study is labelled as such.
4. **Tool behaviour comes from the manual, and is then run.** Where a command or program was executed in this project, the documents say `[RAN]`; where it was only checked against documentation, `[MANUAL]`.
5. **Expert testimony is not a finding.** The Toyota material comes from a plaintiff's expert; it is labelled as such.
6. **Verification status values:** `P` = read the source text itself · `S` = read a reputable secondary page that quotes it · `Sn` = search-result summary only (not opened) · `U` = unverified.

## Tiers

**A** peer-reviewed paper, official report, standard, or official manual · **B** reputable practitioner or course material · **C** blog or aggregator.
