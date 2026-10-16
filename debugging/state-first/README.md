# STATE FIRST

A printable field guide: build confidence in a problem, state it as data and conditions, then aim gdb (conditional
breakpoints, watchpoints, logging) at exactly the right place. Same seven steps for every task.

**Print these two files** (US Letter, large accessible type, Atkinson Hyperlegible):

| File | What |
|---|---|
| `print/state-first-book.pdf` | The book: 25 chapters + appendices, ~126 pages |
| `print/state-first-field-cards.pdf` | 10 one-page cards (method, blank Behavior Card, intake, time, probes, recipes, …) |

Rebuild after editing: `python3 print/build.py` (needs pandoc and Google Chrome; fonts are local).

| Folder | Contents |
|---|---|
| `chapters/` | Book source (Markdown) |
| `cards/` | Field card source |
| `diagrams/` | SVG figures |
| `lab/` | Practice program with a real bug, lldb probes [RAN], gdb probes [MANUAL], patches, transcripts |
| `resource/research/` | Source registry, verified quotes, GDB mechanics, and what could NOT be verified (`05-…`) |

**Before relying on the gdb commands:** on a Linux box run `cd lab && make CXX=g++ && sh gdb/smoke-test.sh`.
