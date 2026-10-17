# C survival kit for application engineers {.appendix data-part="APPENDICES"}

<p class="lede">Just enough C and memory to read embedded application and middleware code. Not an encyclopedia; the list of things that surprise people who write in higher-level languages.</p>

## Types, sizes and wrap-around

| Idiom | Why |
|---|---|
| Use `<stdint.h>`: `uint8_t`, `int16_t`, `uint32_t` | `int` and `long` have different sizes on different targets |
| `unsigned` arithmetic **wraps** silently; `signed` overflow is **undefined behaviour** | compare tick differences in unsigned, then cast to signed (chapter 3) |
| `size_t` for sizes; `TickType_t` for ticks | FreeRTOS: 16 or 32 bits by configuration |
| `float` may be software-emulated (slow, variable time) | check the target: a "float" in a 1 kHz loop may dominate its budget |
| a 64-bit read or write on a 32-bit core is **two** accesses | not atomic (chapter 12) |

## Pointers, in one page

A pointer is a number: an address. `&x` is the address of *x*; `*p` is the value at address *p*. A struct passed **by value** is copied; by pointer, shared. In embedded code you will see:

```c
typedef struct { uint32_t seq, t_us; int32_t angle; } att_t;
att_t a;          /* a block of 12 bytes */
att_t *p = &a;    /* p holds the address of a */
p->angle = 5;     /* same as (*p).angle = 5 */
```

- A pointer into a **stack variable** is invalid after the function returns.
- A pointer to a message in a queue slot is **not yours** after the next send or receive unless the API says so.
- `const` on a pointer or array lets the linker place data in flash: use it for tables.

## Memory-mapped hardware

A peripheral register is a fixed address; reading or writing it does something. The compiler must not remove, merge or reorder those accesses, so register pointers are `volatile`:

```c
#define UART0_DATA (*(volatile uint32_t *)0x40004000)
UART0_DATA = 'x';           /* sends a character */
```

`volatile` means "every access in the source is a real access"; it is *not* atomicity and *not* ordering against other variables (chapters 4, 12). You will seldom write these lines: a vendor library or the framework does. You will read them, and you need to know a statement like `TIMER1_CTRL = 1 | 8` is "set bits 0 and 3".

## Bit operations

| Operation | Meaning |
|---|---|
| `x \| (1u << n)` | set bit *n* |
| `x & ~(1u << n)` | clear bit *n* |
| `(x >> n) & 1u` | read bit *n* |
| `x ^ (1u << n)` | toggle bit *n* |

Read-modify-write of a register or shared flag is **not atomic**; if an interrupt can touch the same word, protect it.

## Where each variable lives

| Declaration | Lives in | Initial value | Note |
|---|---|---|---|
| global / `static` with initialiser | `.data` (RAM, copied from flash at boot) | the initialiser | |
| global / `static` without initialiser | `.bss` (RAM, zeroed at boot) | 0 | |
| local variable | the task's **stack** | **undefined** | stack size matters (chapter 14) |
| `pvPortMalloc` block | heap | undefined | can fail; can fragment |
| `const` global | flash | the initialiser | no RAM |
| `__attribute__((section(".noinit")))` | RAM, not zeroed | **survives a software reset** | post-mortem notes (lab R5) |

## Things that look right and are not

| Code | Problem |
|---|---|
| `if (count++ > 0)` on a shared variable | read-modify-write race |
| `memcpy(dst, src, n)` of a struct that another task is writing | torn copy |
| `char buf[512];` inside a task with a 256-byte stack | overflow, detected late |
| `printf` in an ISR or a high-priority task | long, may lock, uses a lot of stack |
| comparing `now >= deadline` | wraps (chapter 3) |
| `for (;;) { poll(); }` with no delay | starves lower priorities |
| `static` local in a function called by two tasks | shared state, silently |
| a large struct returned by value from a function | stack and copy cost |
