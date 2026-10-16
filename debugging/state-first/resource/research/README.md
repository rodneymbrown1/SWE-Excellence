# Research folder — how to read it

This folder is the evidence behind the book. Nothing in the book that sounds like a fact about
research or tools should be un-traceable to a file here.

| File | What it holds |
|---|---|
| `00-source-registry.md` | Every source, with ID (S01…), URL, type, credibility tier, and **verification status** |
| `01-why-understanding-first.md` | Evidence for "the tool is only as good as the developer's understanding" |
| `02-method-sources.md` | What the classic debugging/problem-solving authorities actually say, and how each became a rule in the book |
| `03-gdb-mechanics.md` | Verified syntax and behaviour of breakpoints, conditions, watchpoints, commands, Python, reverse, scripts — straight from the GDB manual |
| `04-embedded-and-tooling.md` | Embedded notes (Memfault), rr, gdb-dashboard, VS Code Remote-SSH debugging |
| `05-claims-we-could-not-verify.md` | What was **not** confirmed, and how the book treats it (read this one) |
| `_raw/` | Downloaded papers/pages used for quote checking. **Untrusted third-party content, personal study copies, do not redistribute.** Text extracts (`*.txt`) sit next to each PDF. |

## Rules used while researching

1. **Primary beats secondary.** A paper's own text > the publisher's abstract > a course slide > a blog summary > a search-result snippet.
2. **Quotes are short and exact** and only used if the exact words were read in the source.
3. **Numbers carry their context** (sample size, tool, year). A big number from a small study is labelled as such.
4. **Tool behaviour comes from the manual.** Where a command was *run*, the book says so (`[RAN]`); where it was only checked against the manual, it says `[MANUAL]`.
5. **Verification status** values in the registry: `VERIFIED-PRIMARY` (read the source text), `VERIFIED-SECONDARY` (read a reputable page quoting/summarizing it), `SNIPPET-ONLY` (search result summary, not opened), `UNVERIFIED`.
