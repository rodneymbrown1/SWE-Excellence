/* bsp.c -- UART, timers, burn_us, printf, trace.  Freestanding: no libc. */
#include "bsp.h"
#include <stdarg.h>

/* ---- memory-mapped devices on mps2-an385 --------------------------------------------------------------------- */
#define REG(a) (*(volatile uint32_t *)(a))
#define UART0_DATA     REG(0x40004000)
#define UART0_STATE    REG(0x40004004)
#define UART0_CTRL     REG(0x40004008)
#define UART0_BAUDDIV  REG(0x40004010)
#define TIMER0_CTRL    REG(0x40000000)
#define TIMER0_VALUE   REG(0x40000004)
#define TIMER0_RELOAD  REG(0x40000008)
#define TIMER1_CTRL    REG(0x40001000)
#define TIMER1_VALUE   REG(0x40001004)
#define TIMER1_RELOAD  REG(0x40001008)
#define TIMER1_INTCLR  REG(0x4000100C)
#define NVIC_ISER0     REG(0xE000E100)
#define NVIC_ICER0     REG(0xE000E180)
#define NVIC_IPR(n)    (*(volatile uint8_t *)(0xE000E400 + (n)))
#define TIMER1_IRQ 9

static void (*timer1_handler)(void);

void bsp_init(void) {
    UART0_BAUDDIV = 16;
    UART0_CTRL = 1;                       /* TX enable */
    TIMER0_RELOAD = 0xFFFFFFFFu;          /* free-running down-counter */
    TIMER0_CTRL = 1;
    /* calibrate burn_us */
    extern void burn_calibrate(void);
    burn_calibrate();
}

uint32_t now_us(void) { return (0xFFFFFFFFu - TIMER0_VALUE) / (BSP_CLOCK_HZ / 1000000UL); }

/* ---- burn_us ---------------------------------------------------------------------------------------------------- */
static uint32_t iters_per_us_x256 = 256;

static void spin(uint32_t n) { for (volatile uint32_t i = 0; i < n; i++) { } }

void burn_calibrate(void) {
    const uint32_t N = 20000;
    uint32_t t0 = TIMER0_VALUE;
    spin(N);
    uint32_t counts = t0 - TIMER0_VALUE;                          /* timer counts down */
    uint32_t us_x256 = (uint32_t)(((uint64_t)counts * 256u) / (BSP_CLOCK_HZ / 1000000UL));
    iters_per_us_x256 = us_x256 ? (uint32_t)(((uint64_t)N * 256u * 256u) / us_x256) : 256;
}

void burn_us(uint32_t us) { spin((uint32_t)(((uint64_t)us * iters_per_us_x256) >> 8)); }

/* ---- UART / printf ------------------------------------------------------------------------------------------ */
static void putc_raw(char c) { UART0_DATA = (uint32_t)(uint8_t)c; }

void kputs(const char *s) { while (*s) putc_raw(*s++); }

static char *fmt_uint(char *p, unsigned long v, unsigned base, int upper) {
    char tmp[24]; int n = 0;
    do { unsigned d = (unsigned)(v % base); tmp[n++] = (char)(d < 10 ? '0' + d : (upper ? 'A' : 'a') + d - 10); v /= base; } while (v);
    while (n) *p++ = tmp[--n];
    return p;
}

int kprintf(const char *fmt, ...) {
    char out[192]; char *p = out; va_list ap; va_start(ap, fmt);
    while (*fmt && p < out + sizeof(out) - 24) {
        if (*fmt != '%') { *p++ = *fmt++; continue; }
        fmt++;
        int left = 0, zero = 0, width = 0, lng = 0;
        if (*fmt == '-') { left = 1; fmt++; }
        if (*fmt == '0') { zero = 1; fmt++; }
        while (*fmt >= '0' && *fmt <= '9') width = width * 10 + (*fmt++ - '0');
        while (*fmt == 'l') { lng++; fmt++; }
        char tmp[40]; char *e = tmp; const char *src = tmp; size_t len;
        switch (*fmt) {
        case 'd': { long v = lng ? va_arg(ap, long) : va_arg(ap, int); if (v < 0) { *e++ = '-'; v = -v; } e = fmt_uint(e, (unsigned long)v, 10, 0); len = (size_t)(e - tmp); break; }
        case 'u': { unsigned long v = lng ? va_arg(ap, unsigned long) : va_arg(ap, unsigned); e = fmt_uint(e, v, 10, 0); len = (size_t)(e - tmp); break; }
        case 'x': { unsigned long v = lng ? va_arg(ap, unsigned long) : va_arg(ap, unsigned); e = fmt_uint(e, v, 16, 0); len = (size_t)(e - tmp); break; }
        case 'c': { tmp[0] = (char)va_arg(ap, int); len = 1; break; }
        case 's': { src = va_arg(ap, const char *); if (!src) src = "(null)"; len = 0; while (src[len]) len++; break; }
        case '%': { tmp[0] = '%'; len = 1; break; }
        default:  { tmp[0] = '?'; len = 1; break; }
        }
        fmt++;
        size_t pad = (size_t)width > len ? (size_t)width - len : 0;
        if (!left) while (pad--) *p++ = zero ? '0' : ' ';
        for (size_t i = 0; i < len && p < out + sizeof(out) - 2; i++) *p++ = src[i];
        if (left) while (pad--) *p++ = ' ';
    }
    va_end(ap);
    /* write the whole line at once so lines from different tasks do not interleave mid-line */
    uint32_t primask; __asm volatile("mrs %0, primask\n cpsid i" : "=r"(primask) :: "memory");   /* short critical section */
    for (char *q = out; q < p; q++) putc_raw(*q);
    __asm volatile("msr primask, %0" :: "r"(primask) : "memory");
    return (int)(p - out);
}

void bsp_exit(int code) {
    (void)code;
    register uint32_t r0 __asm("r0") = 0x18;        /* SYS_EXIT */
    register uint32_t r1 __asm("r1") = 0x20026;     /* ADP_Stopped_ApplicationExit */
    __asm volatile("bkpt 0xAB" : : "r"(r0), "r"(r1) : "memory");
    for (;;) { }
}

/* ---- TIMER1 periodic interrupt ------------------------------------------------------------------------------ */
void timer1_start(uint32_t period_us, void (*handler)(void)) {
    timer1_handler = handler;
    TIMER1_CTRL = 0;
    TIMER1_RELOAD = period_us * (BSP_CLOCK_HZ / 1000000UL);
    TIMER1_VALUE = TIMER1_RELOAD;
    NVIC_IPR(TIMER1_IRQ) = 0xC0;                    /* 0xC0 >= configMAX_SYSCALL_INTERRUPT_PRIORITY (0xA0): numerically larger = less urgent, so FromISR calls are allowed */
    NVIC_ISER0 = 1u << TIMER1_IRQ;
    TIMER1_CTRL = 1 | 8;                            /* enable + interrupt enable */
}

void timer1_stop(void) { TIMER1_CTRL = 0; NVIC_ICER0 = 1u << TIMER1_IRQ; }

void TIMER1_Handler(void) {
    TIMER1_INTCLR = 1;
    if (timer1_handler) timer1_handler();
}

/* ---- trace ring buffer ----------------------------------------------------------------------------------------- */
volatile uint32_t trace_count;
trace_ev_t trace_buf[TRACE_CAPACITY];

void trace_record(uint8_t type, uint8_t id, uint16_t arg) {
    uint32_t primask; __asm volatile("mrs %0, primask\n cpsid i" : "=r"(primask) :: "memory");
    uint32_t i = trace_count++ % TRACE_CAPACITY;
    trace_buf[i].t_us = now_us(); trace_buf[i].type = type; trace_buf[i].id = id; trace_buf[i].arg = arg;
    __asm volatile("msr primask, %0" :: "r"(primask) : "memory");
}

void trace_reset(void) { trace_count = 0; }

void trace_dump(void) {
    uint32_t n = trace_count > TRACE_CAPACITY ? TRACE_CAPACITY : trace_count;
    uint32_t first = trace_count > TRACE_CAPACITY ? trace_count % TRACE_CAPACITY : 0;
    if (trace_count > TRACE_CAPACITY) kprintf("# trace wrapped: oldest %lu events lost\n", (unsigned long)(trace_count - TRACE_CAPACITY));
    for (uint32_t k = 0; k < n; k++) {
        trace_ev_t *e = &trace_buf[(first + k) % TRACE_CAPACITY];
        kprintf("T %lu %u %u %u\n", (unsigned long)e->t_us, e->type, e->id, e->arg);
    }
}
