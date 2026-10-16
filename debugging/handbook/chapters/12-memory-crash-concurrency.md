# 12 · Memory, Crashes & Concurrency  **[added — beyond the talk]**

> The talk covers *understanding* code; it explicitly says other lenses (performance, **safety**) "are follow-on talks"
> but "some of the tools could be used for them" **[talk]**. This chapter adds the standard C++ toolbox for the
> problems you will meet next as a new C++ developer. The core rule: **crash site ≠ bug site.**

## Triage by symptom

| Symptom | Likely class | First move |
|---|---|---|
| `Segmentation fault`, `SIGSEGV` | null / dangling / out-of-bounds | run under debugger → `bt` → then **ASan** |
| `abort()` / `terminate called after throwing…` | uncaught exception, failed assert | `bt`; `catch throw` to see where it originated |
| Random garbage values, "works on my machine" | uninitialized memory, UB | UBSan + ASan; valgrind `--track-origins=yes`; compile `-Wall -Wextra` |
| Memory grows forever | leak | LeakSanitizer / `leaks` / valgrind |
| Frozen, 0% CPU | deadlock / blocked on I/O | attach, `thread apply all bt` |
| Frozen, 100% CPU | busy loop / livelock | `perf top` / `sample`, then attach and `bt` |
| Wrong only sometimes, changes with `-O2`, or when you add a print | race / UB | TSan; `rr --chaos`; reduce threads |
| Fine in Debug, broken in Release | UB, uninit var, or `assert` doing real work | build RelWithDebInfo + sanitizers (ch.05) |

## 1 · Sanitizers — the fastest way to find memory bugs ✅ ASan tested on macOS

Build a **separate** dir so it doesn't disturb your normal build:
```bash
cmake -S . -B build-asan -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_CXX_FLAGS="-fsanitize=address,undefined -fno-omit-frame-pointer -g"
cmake --build build-asan -j && ./build-asan/app            # a bug prints a report with the exact line and allocation/free stacks
# single file, no CMake:
clang++ -g -O0 -fsanitize=address,undefined x.cpp -o x && ./x
```
Tested output for a 1-line heap overflow: `ERROR: AddressSanitizer: heap-buffer-overflow … WRITE of size 4 … #0 main leak.cpp:2`.
- **ASan** (`-fsanitize=address`): out-of-bounds, use-after-free, double-free, stack/heap overflow (~2× slowdown). Docs: <https://clang.llvm.org/docs/AddressSanitizer.html>
- **UBSan** (`-fsanitize=undefined`): signed overflow, bad shifts, null deref, misaligned access. <https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html>
- **TSan** (`-fsanitize=thread`): data races. Can't combine with ASan. <https://clang.llvm.org/docs/ThreadSanitizer.html>
- **LSan** leaks: included with ASan on Linux (`ASAN_OPTIONS=detect_leaks=1`).
- Useful env: `ASAN_OPTIONS=abort_on_error=1:halt_on_error=1` (then a debugger/core catches it), `UBSAN_OPTIONS=print_stacktrace=1`.
- Run under a debugger and break on the report: `b __asan::ReportGenericError` (GDB/LLDB) 📖.

## 2 · Valgrind (Linux; no rebuild needed) **[talk mentions valgrind for leaks]** 📖
```bash
valgrind --leak-check=full --track-origins=yes --error-exitcode=1 ./build/app
#   "Invalid read of size 4 … Address … is 0 bytes after a block of size 16 alloc'd at …"
#   --track-origins=yes → "Uninitialised value was created by a stack allocation at …"
valgrind --tool=helgrind ./build/app           # threads: lock-order violations & races
```
~20–50× slower; use a small input. Manual: <https://valgrind.org/docs/manual/manual.html> · Helgrind <https://valgrind.org/docs/manual/hg-manual.html>

## 3 · macOS memory tools ✅ `leaks` tested
```bash
MallocStackLogging=1 leaks --atExit -- ./build/app    # ✅ "1 leak for 1536 total leaked bytes" (finds the allocation stack too)
leaks $(pgrep -n app)                                  # leak check on a running process
heap $(pgrep -n app) | head                            # what's on the heap, by class
vmmap $(pgrep -n app) | head -30                       # address space layout
MallocScribble=1 MallocGuardEdges=1 ./build/app        # 📖 fill freed/alloc'd memory with patterns; guard pages
```

## 4 · Crashes: get the stack, then work backwards

```bash
# live: run under the debugger — it stops AT the crash
gdb --args ./build/app --case 42          # (gdb) run  … SIGSEGV …  (gdb) bt   (gdb) frame 1   (gdb) info locals   (gdb) p *ptr
lldb -- ./build/app --case 42             # (lldb) run  … (lldb) bt  (lldb) frame variable  (lldb) p *ptr

# post-mortem: crash happened elsewhere (CI / test rig / field)                                      📖
ulimit -c unlimited                       # allow core files in THIS shell (then run the app)
cat /proc/sys/kernel/core_pattern         # where do cores go? (could be piped to systemd-coredump / apport)
coredumpctl list ; coredumpctl gdb        # systemd systems
gdb ./build/app core                      # then: bt full   |   thread apply all bt
# macOS: crash reports ~/Library/Logs/DiagnosticReports/ ; cores in /cores if enabled
```
**Reading a crash:** frame #0 is *where it died* — usually innocent. Move up (`up`) to the first frame in **your** code; print the pointer; ask
*"who last set this pointer / freed this object?"* → `watch -l ptr` (ch.07) or reverse-continue (ch.08) or ASan's "freed by thread T0 here:" stack.

**Exceptions:** `catch throw` stops where the exception is *thrown* (the interesting place), not where it's finally uncaught.
```gdb
catch throw            # GDB 📖        lldb: breakpoint set -E cxx
catch catch            # where it's caught
```

**Cheap hardening flags while debugging [added]:**
`-D_GLIBCXX_ASSERTIONS` (bounds-checks `operator[]`, `front()` on empty containers etc. in libstdc++) · `-D_GLIBCXX_DEBUG` (heavier, changes ABI —
rebuild everything) · `-fstack-protector-strong` · `-Wall -Wextra -Wshadow -Wconversion`.

## 5 · Hangs & deadlocks 📖 (✅ `sample` tested)

```bash
# Linux: attach and dump EVERY thread's stack — then READ for two threads waiting on each other's mutex
sudo gdb -p $(pgrep -n app) -batch -ex 'thread apply all bt'        # one-shot, non-interactive
sudo eu-stack -p $(pgrep -n app)        # elfutils: stacks without gdb;   also: pstack PID
sudo strace -f -p $(pgrep -n app)       # what syscall is it blocked in? (futex = lock wait, read/poll = I/O)
cat /proc/$(pgrep -n app)/stack         # kernel stack (root)
top -H -p $(pgrep -n app)               # which THREAD is burning CPU

# macOS
sample $(pgrep -n app) 3 -file /tmp/s.txt      # ✅ per-thread call graphs
sudo spindump $(pgrep -n app) 5 -file /tmp/sd.txt   # 📖
lldb -p $(pgrep -n app) -o 'bt all' -o 'detach' -o quit
```
Deadlock signature: two threads, each in `pthread_mutex_lock` / `futex_wait`, each holding the lock the other needs. Fix = lock ordering (`std::scoped_lock(a, b)`), or less sharing.

## 6 · Races & heisenbugs: make them deterministic
```bash
# 1. Detect:   cmake … -DCMAKE_CXX_FLAGS="-fsanitize=thread -g"    →  "WARNING: ThreadSanitizer: data race" with both stacks
# 2. Reproduce: rr record --chaos ./app   (ch.08)   or   taskset -c 0 ./app (pin to one core)   or   run it in a loop:
n=0; while ./build/app >/dev/null 2>&1; do n=$((n+1)); done; echo "failed after $n runs"      # ✅ shell pattern
# 3. Shake it:  stress -c 8 &   # (or `yes > /dev/null &` ×N) while the loop runs — contention exposes races
```
Adding a print "fixes" it? That's the signature of a race or UB — don't trust the fix; find the shared state (ch.07 watch with `awatch`).

## Links
- AddressSanitizer / UBSan / TSan — <https://clang.llvm.org/docs/AddressSanitizer.html> · <https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html> · <https://clang.llvm.org/docs/ThreadSanitizer.html>
- GCC instrumentation options — <https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html>
- Valgrind — <https://valgrind.org/docs/manual/manual.html> · `strace(1)` — <https://man7.org/linux/man-pages/man1/strace.1.html> · `core(5)` — <https://man7.org/linux/man-pages/man5/core.5.html>
- libstdc++ debug mode / assertions — <https://gcc.gnu.org/onlinedocs/libstdc++/manual/debug_mode.html>
- Apple: *Diagnosing memory, thread, and crash issues early* — <https://developer.apple.com/documentation/xcode/diagnosing-memory-thread-and-crash-issues-early>
