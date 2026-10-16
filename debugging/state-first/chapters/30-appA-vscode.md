<section class="part-title"><p class="pn">Appendices</p><div class="ph">Reference</div><p>VS Code setup, the gdb and lldb command map, a smoke test for your Linux machine, the evidence behind the book, and a glossary.</p></section>

# VS Code over SSH: the step-by-step {.appendix}

<p class="lede">Your setup: VS Code on a Windows laptop, connected by SSH to a Linux server. You installed the C/C++ extension on the server, wrote a launch.json, and when you pressed debug it ran from the terminal with no connected UI. This appendix is a working setup and a ranked list of things to check.</p>

::: note
**What I could and could not do.** I cannot see your machines. The steps below come from Microsoft's VS Code documentation (Remote-SSH, C/C++ launch.json reference, Linux configuration page). I did not run them against a Windows-to-Linux setup. The troubleshooting table lists *hypotheses to test*, not a diagnosis. The gdb in the terminal always works; the GUI is a convenience.
:::

## Where each piece runs

| Piece | Runs on | Notes |
|---|---|---|
| VS Code window (the UI) | Windows laptop | What you see and click |
| VS Code Server, extensions, terminal | Linux server | Started for you by Remote-SSH |
| C/C++ extension (`cppdbg`) | **Linux server** | Must be installed *on the remote* |
| `gdb`, `g++`, your code, the program | Linux server | `gdb` and the compiler must exist here |

The Microsoft docs say: "Local extensions that actually need to run remotely will appear dimmed and disabled in the Local - Installed category. Select Install to install an extension on your remote host."

## Setup, in order

**1. Connect.** Install the *Remote - SSH* extension locally. In VS Code, run **Remote-SSH: Connect to Host…**, choose your server. A new window opens with the host name in the bottom-left corner.

**2. Open your folder on the remote.** **File → Open Folder** and pick the project directory *on the server*. The debug configuration lives in `.vscode/` inside it.

**3. Install the C/C++ extension on the remote.** In the Extensions view of the *remote window*, find **C/C++** (Microsoft) and select **Install** for your host. If the button says "Install in SSH: your-host", that is the one.

**4. Check the server has the tools.** In the remote integrated terminal:

```
gdb --version
g++ --version
which gdb            # note the path for miDebuggerPath
```

If `gdb` is missing: `sudo apt-get install build-essential gdb` (Debian/Ubuntu, from the VS Code Linux page).

**5. Build with symbols.** `-g -O0` (chapter 4). For the lab: `make -C lab CXX=g++`. Confirm symbols exist:

```
gdb -batch -ex "list main" lab/gateway      # should print source lines
```

**6. Create `.vscode/launch.json`.**

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug gateway (gdb)",
      "type": "cppdbg",
      "request": "launch",
      "program": "${workspaceFolder}/lab/gateway",
      "args": ["--max", "400"],
      "stopAtEntry": false,
      "cwd": "${workspaceFolder}/lab",
      "externalConsole": false,
      "MIMode": "gdb",
      "miDebuggerPath": "/usr/bin/gdb",
      "setupCommands": [
        { "description": "Pretty-print STL", "text": "-enable-pretty-printing", "ignoreFailures": true }
      ],
      "preLaunchTask": "build gateway"
    }
  ]
}
```

**7. Create `.vscode/tasks.json`** (the build step that runs first).

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "type": "shell",
      "label": "build gateway",
      "command": "make",
      "args": ["-C", "${workspaceFolder}/lab", "CXX=g++"],
      "problemMatcher": ["$gcc"],
      "group": { "kind": "build", "isDefault": true }
    }
  ]
}
```

**8. Set a breakpoint and start the right way.** Click in the gutter next to a line in `gateway.cpp`. Open **Run and Debug** (the bug-and-play icon), choose **Debug gateway (gdb)** in the dropdown, and press the green **Start Debugging** button (F5).

::: trap
**Do not use "Run Without Debugging" (Ctrl+F5), a "Run" button from another extension, or the terminal.** Those start the program with no debugger attached. They look similar and are the most common reason the UI never connects.
:::

**9. Check that the UI is connected.** You should see: a yellow arrow on the stopped line, the **Variables** pane (expand `this` to see members), a **Call Stack**, and a **Debug Console**. In the Debug Console, `-exec info breakpoints` should list your breakpoint.

**10. Try the features from this book in the UI.** Right-click the gutter: **Add Conditional Breakpoint** (an expression, a hit count, or "wait for breakpoint"), or **Add Logpoint** (text with `{expressions}`). Per the VS Code docs, data breakpoints "depend on the debugger", so test whether your setup offers them. If not, use `-exec watch -l …` in the Debug Console.

## If it ran in the terminal with no UI: hypotheses, most likely first

These are **things to test**, not conclusions. Work down the list.

| # | Hypothesis | How to test | If true |
|---|---|---|---|
| 1 | The program was started some other way (terminal, `make run`, Ctrl+F5, another extension's Run button) | Open the Run and Debug panel. Is **Debug gateway (gdb)** in the dropdown? Did you press F5 with that selected? | Use the green Start Debugging with that configuration |
| 2 | `type` or `request` is wrong in `launch.json` | The dropdown shows no configuration, or a different debugger. `type` must be `cppdbg`, `request` must be `launch` | Fix the JSON |
| 3 | The C/C++ extension is not installed on the **remote** | Extensions view in the remote window: does it say **Install** (not "Installed") next to C/C++? Does the dropdown lack `C++ (GDB/LLDB)`? | Install it on the SSH host |
| 4 | `externalConsole` is true, so output goes to another window | Check the property | Set `"externalConsole": false` |
| 5 | Breakpoints are hollow or grey ("unbound") | Hover the breakpoint. Was the binary built with `-g -O0`? Is `program` the same file you built? | Rebuild with symbols; fix `program` |
| 6 | `miDebuggerPath` is wrong or gdb is missing | A pop-up or error in the **Debug Console** or **Output → C/C++** | Use the path from `which gdb` |
| 7 | The adapter failed silently | Add the `logging` options from the launch.json reference and read **Output → C/C++** | Follow the message |
| 8 | Attach errors: `ptrace: Operation not permitted` | Only when *attaching* to a running process | See the VS Code C++ debugging page; may need ptrace permission |
| 9 | Corporate restrictions on installing extensions on the remote | Install fails or is blocked | Ask your team about an approved offline install route. *Plausible, unverified.* |

## The terminal is always an option

Everything in this book works in a plain terminal:

```
gdb -q ./lab/gateway
(gdb) break gateway.cpp:81 if e.type == EventType::Heartbeat && missed_ != 0
(gdb) run --max 400
```

If the GUI costs you more time than it saves on a given day, use the terminal and come back to it.

## Sources

VS Code docs: *Debugging* (breakpoint types), *C/C++ launch.json reference*, *Configure VS Code for debugging on Linux*, *Remote - SSH*, and *C/C++ debugging* (the `-exec` note). See Appendix D.
