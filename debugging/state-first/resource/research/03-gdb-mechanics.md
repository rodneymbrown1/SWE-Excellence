# 03 · GDB mechanics (verified against the official manual)

Base URL: `https://sourceware.org/gdb/current/onlinedocs/gdb.html/<Page>.html` (the `/gdb/` path 301-redirects here).
Status: **[MANUAL]** = read in the manual, not executed (this Mac has only lldb). **[RAN]** = executed here with lldb.

## Breakpoints and conditions (pages `Set-Breaks`, `Conditions`, `Disabling`, `Break-Commands`, `Dynamic-Printf`, `Save-Breakpoints`)
- `break LOCSPEC [if COND]`; `tbreak` = "enabled only for one stop"; `rbreak REGEX`; `hbreak`/`thbreak` hardware bps.
- `condition N EXPR` (set), `condition N` (remove). GDB checks syntax when you set it but "does not actually evaluate expression" then.
- `ignore N COUNT`: "the breakpoint does not stop the next n times"; and "If a breakpoint has a positive ignore count and a condition, the condition is not checked."
- "Conditions are also accepted for watchpoints." `watch EXPR if COND` works (Conditions page).
- "Break conditions can have side effects, and may even call functions in your program"; the manual says command lists are "usually more convenient and flexible than break conditions" for side effects.
- `enable once N`, `enable count C N`, `enable delete N`; `disable`.
- `commands [N] … end`. First command `silent` suppresses the stop banner. "Any other commands in the command list, after a command that resumes execution, are ignored." The manual's example:
  ```
  break foo if x>0
  commands
  silent
  printf "x is %d\n",x
  cont
  end
  ```
- `dprintf LOCSPEC,"template",expr,…` — a breakpoint that prints and continues; `info break` shows it as a breakpoint with commands. `set dprintf-style gdb|call|agent`.
- `$bpnum` is set when a breakpoint is created; `$_hit_bpnum` / `$_hit_locno` when one is hit (Set-Breaks page); `disable $_hit_bpnum` disables the one that hit (Break-Commands).
- `save breakpoints FILE` → reload with `source FILE`. Watchpoints on locals "may fail to be recreated."
- `set breakpoint condition-evaluation host|target|auto` (default auto) — conditions may be evaluated on the target for remote debugging.

## Watchpoints (page `Set-Watchpoints`)
- Syntax: `watch [-l|-location] EXPR [thread ID] [mask M]`, same for `rwatch` (read) and `awatch` (read or write).
- `-location`: "tells GDB to instead watch the memory referred to by expr" (not tied to variable scope).
- Hardware when possible. Software watchpoints "report the change in value at the next statement, not the instruction."
- `rwatch`/`awatch` can only be hardware; error if impossible: "Expression cannot be implemented with read/access watchpoint."
- Scope: "GDB automatically deletes watchpoints that watch local (automatic) variables … when they go out of scope."
- Too many hardware watchpoints → "Hardware watchpoint num: Could not insert watchpoint". No fixed number given in the manual (target-dependent).
- `set can-use-hw-watchpoints 0` forces software (slow).
- "Cannot watch constant value" → write `watch *(int *) 0x600850`.
- `thread ID` form works only with hardware watchpoints.

## Convenience functions/variables (pages `Convenience-Funs`, `Convenience-Vars`)
- Need Python-enabled GDB: `$_streq(a,b)`, `$_regex(str,re)`, `$_strlen`, `$_memeq`, `$_caller_is(name[,n])`, `$_caller_matches(re[,n])`, `$_any_caller_is(name[,n])`, `$_any_caller_matches(re[,n])`. `$_caller_*` look at one frame (default 1 = caller); `$_any_caller_*` "checks all stack frames from the immediate caller to the frame specified by number_of_frames".
- Variables: `set $i = 0`; "Using a convenience variable for the first time creates it, but its value is void until you assign a new value."; `init-if-undefined $v = 0`.
- Caution (our note): `re.match`-style anchoring of `$_caller_matches` is **not stated** in the manual page we read. Use patterns that tolerate a class prefix (e.g. `".*flush_burst"`) and verify on first use.

## Python breakpoints (page `Breakpoints-In-Python`)
- `class Probe(gdb.Breakpoint): def stop(self): …` — "If the method returns True, the inferior will be stopped at the location of the breakpoint, otherwise the inferior will continue." Do **not** step, change frame, or add/delete breakpoints inside `stop`.
- Constructor takes `type` (`gdb.BP_BREAKPOINT`, `gdb.BP_WATCHPOINT`, …) and `wp_class` (`gdb.WP_WRITE` default, `WP_READ`, `WP_ACCESS`).
- Attributes: `enabled`, `condition`, `hit_count` (writable only to 0), `ignore_count`, `commands`, `silent`.
- `FinishBreakpoint`: **not read** (separate page).

## Looking at state (pages `Frame-Info`, `Variables`, `Print-Settings`, `Selection`)
- `info args`, `info locals`: "all variables … accessible at the point of execution of the selected frame." The manual does **not** say `info locals` lists members of `this`; in practice use `print *this` (**[RAN]** in lldb: `frame variable` showed `this` and `e`, `p *this` showed all members).
- `frame N`, `up [n]`, `down [n]`; `select-frame`.
- `set print pretty on` (one member per line, default off); `set print object on`; `set print elements N` (default 200).

## Reverse execution (page `Reverse-Execution`)
- `reverse-continue` (`rc`), `reverse-step`, `reverse-next`, `reverse-finish`, `reverse-stepi/nexti`; `set exec-direction reverse`.
- Needs `record` (or `record btrace`); "not all target environments can support reverse execution."
- With **rr** (T07): `rr record PROG`, `rr replay`; example in the wiki is `watch -l mRect.width` then `reverse-cont`; rr "requires a reasonably modern x86 CPU or certain ARM CPUs (Apple M1+)", "emulates a single-core machine", Linux-only in practice.

## Catchpoints (page `Set-Catchpoints`)
- `catch throw|catch|rethrow [regexp]` (C++, gnu-v3 ABI), `catch syscall [names]`, `catch signal [sigs]`, `catch fork|vfork|exec`, `catch load|unload [regexp]`; `tcatch` = one-shot.

## Scripts and startup (pages `Command-Files`, `Mode-Options`, `File-Options`, `Initialization-Files`, `Auto_002dloading-safe-path`)
- `gdb -batch -x script.gdb ./prog` — `-batch` "Exit with status 0 after processing all the command files specified with '-x'"; "An error in any command terminates execution of the command file." `-ex CMD` runs one command; `-x FILE` "evaluated exactly as the `source` command would".
- `-nx` skips init files.
- A `.gdbinit` in the current directory is read last (after command line options other than `-x`/`-ex`). GDB does not auto-load files from untrusted places: `set auto-load safe-path`, `add-auto-load-safe-path DIR`; refusal message includes "auto-loading has been declined by your `auto-load safe-path'". (Manual text read concerns auto-load scripts generally; **exact behaviour for local `./.gdbinit` not confirmed** → the book recommends explicit `-x`.)
- `source [-s] [-v] FILE`; `if/else/while … end` available in command files.
