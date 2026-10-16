# lab/ — the practice program

`gateway.cpp` is a small event-driven link monitor that runs in an endless loop (pass `--max N` to stop it).
It has one planted bug (requirement R5, see the comment block at the top of the file).
The book's worked examples (chapters 19–21) all run on it.

```
make                      # builds ./gateway with -O0 -g   (on Linux: make CXX=g++)
./gateway --max 400       # watch the log; spot what looks wrong before opening the book chapter
```

| Folder | What | Status |
|---|---|---|
| `lldb/` | Probe scripts + `probes.py` (Python callbacks) | **[RAN]** on macOS, lldb-1700; transcripts in `transcripts/` |
| `gdb/`  | The same probes as gdb scripts | **[MANUAL]** — checked against the GDB manual, not executed. Run `sh gdb/smoke-test.sh` on your Linux box |
| `solutions/` | `01-fix-missed-reset.patch`, `02-feature-outage-duration.patch` (apply in order with `patch -p1 < file`) | built and run |
| `transcripts/` | Captured output of the lldb runs | real output |

Don't read the solutions first — the point is to find the bug with the probes.
