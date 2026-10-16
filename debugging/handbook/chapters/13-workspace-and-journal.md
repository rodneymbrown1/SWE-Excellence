# 13 · Workspace & Investigation Journal

> **[talk]** Two "soft" tips that are actually force multipliers: **see more at once** (screens + a window manager)
> and **write things down** (a greppable journal). *"The number of times I've needed to compare code side-by-side…"*
> From your notes: *"screen management was important — I just started using tmux today and have been picking up vim for a couple weeks."*

## 1 · Screens & window management **[talk, slides 54–55]**

- More pixels = more context visible = fewer things held in your head. The speakers' (slightly cheeky) advice: ask for a big/portrait **4K** or second monitor — *"the only thing you physically need from your hardware is to make it easier to do your job."* Build/test are mostly remote anyway.
- Use whatever fits you — IDE, or **tmux + vim** (Mike's setup). *"What works for you is what matters."* Don't force a tool because someone evangelized it.

### tmux in 10 commands (prefix is `Ctrl-b`) ✅ layout script tested

```bash
tmux new -s debug            # new named session          tmux ls   |   tmux attach -t debug   |   tmux kill-session -t debug
# inside tmux (press Ctrl-b, release, then the key):
#   %  split left|right      "  split top/bottom      o / arrows  move between panes     z  zoom a pane (toggle)
#   c  new window            n / p  next/prev window   ,  rename window                   d  detach (keeps everything running)
#   [  scroll/copy mode (q to exit)                    x  kill pane                       ?  list all keys
```
**A debugging layout** — editor on the left, debugger top-right, search/shell bottom-right, a `journal` window for notes:
```
┌───────────────────┬───────────────────┐
│ vim (code)        │ gdb / lldb        │   window 1: "code"
│                   ├───────────────────┤
│                   │ shell: rg / git   │
└───────────────────┴───────────────────┘
window 2: "journal"  →  vim ~/swe-excellence/journal/2025-xx-xx.md
```
Script it once (`~/bin/dbg-session.sh`, then `chmod +x`):
```sh
#!/bin/sh
S=${1:-debug}
tmux has-session -t "$S" 2>/dev/null && exec tmux attach -t "$S"
tmux new-session  -d -s "$S" -n code
tmux send-keys    -t "$S":code 'vim .' C-m
tmux split-window -h -t "$S":code
tmux split-window -v -t "$S":code.1
tmux new-window   -t "$S" -n journal
tmux select-window -t "$S":code ; tmux select-pane -t "$S":code.0
exec tmux attach -t "$S"
```
Nice side effect: if your SSH connection drops, the session (and your running debugger) survives — `tmux attach` and you're back.
Docs: <https://github.com/tmux/tmux/wiki> (Getting Started) · man tmux.

### vim: just the code-reading subset **[added]**
```
Ctrl-o / Ctrl-i      jump back / forward through your jump history      (the "where was I?" keys)
*  /  #              search the word under the cursor, next / previous
gd                   go to local definition       Ctrl-]   go to tag (needs ctags or LSP)      Ctrl-t  back
:vsplit file         side-by-side                  Ctrl-w w / h / l   move between splits       Ctrl-w =  equalize
:set number relativenumber hlsearch incsearch
:grep PATTERN        then  :copen  :cn  :cp     — set  :set grepprg=rg\ --vimgrep  so :grep uses ripgrep
:Ex  or  :Vex        file browser                  gf  open file under cursor
:e +123 src/foo.cpp  open at line 123 (paste a line from a bt!)
```
Learn 2–3 new keys per week, not 30 in a day. `vimtutor` in a terminal takes ~30 minutes.

## 2 · The investigation journal **[talk, slide 44]**

*"Whatever journaling tool is the lowest friction. A physical notebook, but a Google Doc or a **greppable text file** may be best."*
*"What structure did you find for that train? What data were you watching, so you can come back to it later?"* —
and John Carmack's `.plan` files (a running to-do/learnings list): <https://garbagecollected.org/2017/10/24/the-carmack-plan/> · talk on note-taking systems: <https://www.youtube.com/watch?v=SW1fzrB-UEg>.

> ⚠️ **Raytheon / defense-contractor note [added]:** keep the journal inside whatever location your program approves for work notes
> (internal wiki/OneNote/approved laptop). Don't put export-controlled or customer-specific details in personal cloud notes or public repos.
> The generic *method* notes in this handbook are fine; code excerpts and program details are not. Ask your lead where notes may live.

### One-liner to start today's entry (append-only, greppable) ✅ plain shell
```bash
mkdir -p ~/swe-excellence/journal
jrnl() { printf '\n## %s  %s\n' "$(date '+%Y-%m-%d %H:%M')" "$*" >> ~/swe-excellence/journal/$(date +%F).md; ${EDITOR:-vim} + ~/swe-excellence/journal/$(date +%F).md; }
#   usage:  jrnl "why is Tracker::m_total negative"       find old notes:  rg -n 'm_total' ~/swe-excellence/journal/
```
(add the function to `~/.zshrc`)

### Entry template (copy/paste)
```markdown
## <date> <time> — <one-line goal>
**Symptom:**  exact text / value / exit code
**Repro:**    command, input, commit SHA, build dir
**Hypotheses:**
  1. <falsifiable sentence>  → test: <what I ran>  → result: CONFIRMED / FALSIFIED because …
  2. …
**Evidence:** bt / log lines / screenshot of call graph or flame graph (paste the file path)
**Root cause (5 whys):** …
**Fix:** <commit/PR> · **Regression test:** <name>
**What I learned (tool/idea):** …            **Open questions:** …
```
### What to capture on day one in a new area **[talk + added]**
| Capture | Why |
|---|---|
| Build recipe that actually works | the talk: builds take days; this is the best first contribution |
| Entry points & what happens before/after `main` | your map's anchor |
| Key data structures you watched (`ptype` output) | "what structure did you find for that train?" |
| Call graph / flame graph screenshot | visual memory; shows what the subsystem *is* |
| Questions you asked + answers (who answered) | you'll be asked again; so will the next new hire |
| Which tools are approved at work | the talk's advice: ask what's already in use |

## 3 · Pair & shadow **[talk, closing advice]**
*"Ask a senior engineer very nicely: can I shadow you for 15 minutes? … I would always learn a new tool, a new way to investigate the code, and be able to ask the silly questions."*
Template: *"Could I watch you debug something for 15 minutes this week? I'm trying to learn how you find things."* Take notes in the journal's "tools I saw" section.
Also from the talk: seniors — note where recurring questions come from (fix the docs), and consider screen-recording an onboarding session.

## Links
- tmux — <https://github.com/tmux/tmux/wiki> · vim help online — <https://vimhelp.org/> · `vimtutor`
- Carmack `.plan` — <https://garbagecollected.org/2017/10/24/the-carmack-plan/>
- MIT *The Missing Semester* (shell, vim, tmux, debugging, version control — cited on slide 18) — <https://missing.csail.mit.edu/>
