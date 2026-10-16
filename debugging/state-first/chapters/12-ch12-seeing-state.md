# Seeing state the way your editor shows it {.chapter}

<p class="lede">You said you only want to see what you would write or read in a text editor: arguments, classes, variables. Good. That is all this chapter covers. No memory dumps, no assembly.</p>

## "Does `info locals` show all the variables of my object?"

You asked this directly: for an initialized class, how do I see the state of all its variables in a given frame, or will `info locals` only show what is visible in `list`?

**No, it does not show the object's members.** `info locals` and `info args` show the **local variables and arguments of the selected frame**. The GDB manual describes `info locals` as "all variables (declared either static or automatic) accessible at the point of execution of the selected frame." It does not claim that the members of `this` are included, and in practice they are not. To see the whole object, print the object.

Here it is on the practice program. Stopped inside `LinkMonitor::on_event`: [RAN]{.ran}

```out
(lldb) frame variable
(LinkMonitor *) this = 0x000000016fdff02c
(const Event &) e = 0x000000016fdfefd0 (type = Heartbeat, tick = 26, payload = 0)

(lldb) p *this
(LinkMonitor)  (state_ = Degraded, missed_ = 7, good_ = 1, now_ = 26, data_seen_ = 8)

(lldb) p e
(const Event &) 0x000000016fdfefd0 (type = Heartbeat, tick = 26, payload = 0)
```

`frame variable` showed the two things the *frame* owns: the pointer `this` and the argument `e`. `p *this` showed every member of the object. In gdb the same two steps are `info args` and `print *this`. [MANUAL]{.manual}

::: rule
**To see an object: `print *this` inside a method, `print obj` where the object is in scope, `print *ptr` through a pointer.** The frame's locals are one thing; the object's members are another.
:::

## What do I want to see?

| I want to see… | gdb | lldb |
|---|---|---|
| Arguments of this call | `info args` | `frame variable` [RAN]{.ran} |
| Local variables | `info locals` | `frame variable` [RAN]{.ran} |
| **All members of the object I am in** | `print *this` | `p *this` [RAN]{.ran} |
| One member | `print this->missed_` or just `print missed_` | `p missed_` [RAN]{.ran} |
| An object through a pointer | `print *ptr` | `p *ptr` |
| An argument passed by reference | `print e` | `p e` [RAN]{.ran} |
| What a call returned | `finish` (prints "Value returned") | `finish` |
| Locals of **every** frame in the stack | `bt full` | `bt`, then `frame select N` |
| The definition of a type | `ptype LinkMonitor` | `type lookup LinkMonitor` |
| A value that updates at every stop | `display missed_` (and `undisplay N`) | `display missed_` (untested) |

Two of these are worth pausing on.

**`finish`.** It runs until the current function returns and prints what it returned. "What did this call give back?" is the *out* half of "what went in, what is in here, what came out."

**`display`.** It prints an expression every time the program stops. Put the three or four variables from your card on `display` and every stop becomes a status line.

## Moving between frames without moving the program

A backtrace is a stack of frames. You can **look** at any of them without running anything.

| Goal | gdb | lldb |
|---|---|---|
| Show the stack | `bt` | `bt` [RAN]{.ran} |
| Look at the caller | `up` (`up 2`) | `up` [RAN]{.ran} |
| Back down | `down` | `down` |
| Jump to frame N | `frame 3` | `frame select 3` |

`up` does not move execution. It changes which frame `print`, `info locals`, and `info args` refer to. This is how you answer "what did the caller pass in?" For example, `up` from `on_event` lands in `Gateway::dispatch`, where `frame variable` shows the Gateway's own `this` and the same `e`. [RAN]{.ran}

## Making the output readable

| Setting | Effect |
|---|---|
| `set print pretty on` | One member per line for nested structs. Default is off. |
| `set print object on` | For polymorphic objects, show the actual derived type instead of the declared one. Default is off. |
| `set print elements unlimited` | Show whole arrays and strings. The default limit is 200 elements. |

Put them in a startup file so they are always on (chapter 14).

## Containers and library types

`print vec` for a `std::vector` should show the elements if pretty-printers for the standard library are installed. Linux distributions normally ship them with GDB, but I have not verified this for your server. If you see raw internal pointers, that is the sign they are not loaded. lldb includes built-in formatters for the C++ standard library. [UNTESTED]{.unt}

## When a value says `<optimized out>`

The program was built with optimization. Rebuild with `-O0 -g` (chapter 4). Debugging an optimized build is possible but you spend your attention fighting the tool.

## Check yourself

* Which command shows the members of `this`? Which shows the arguments?
* You are stopped in a function and you want to know what its caller passed. What do you type?
* What does `finish` give you that `next` does not?
