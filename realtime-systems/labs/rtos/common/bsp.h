/* bsp.h -- tiny board support for the labs (QEMU mps2-an385, Cortex-M3, 25 MHz system clock). */
#ifndef BSP_H
#define BSP_H
#include <stdint.h>
#include <stddef.h>

#define BSP_CLOCK_HZ 25000000UL

void bsp_init(void);                         /* UART, free-running timer, burn calibration */
void kputs(const char *s);
int  kprintf(const char *fmt, ...) __attribute__((format(printf, 1, 2)));
void bsp_exit(int code);                     /* ends the QEMU run via semihosting */

/* Free-running 32-bit microsecond clock (wraps every ~171 s of virtual time). */
uint32_t now_us(void);

/* Consume `us` microseconds of CPU time, *not* wall time: a task preempted while burning takes longer to finish.
 * Calibrated once at boot against the hardware timer. */
void burn_us(uint32_t us);

/* Second hardware timer (TIMER1) as a periodic interrupt source for the labs.  `handler` runs in interrupt context. */
void timer1_start(uint32_t period_us, void (*handler)(void));
void timer1_stop(void);

/* Lightweight trace ring buffer ------------------------------------------------------------------------------- */
enum { EV_SWITCH_IN = 1, EV_USER = 2, EV_ISR = 3, EV_MARK = 4 };
typedef struct { uint32_t t_us; uint8_t type; uint8_t id; uint16_t arg; } trace_ev_t;
void trace_record(uint8_t type, uint8_t id, uint16_t arg);
extern volatile uint32_t trace_count;
extern trace_ev_t trace_buf[];
#define TRACE_CAPACITY 1024
void trace_dump(void);                       /* prints "T <t_us> <type> <id> <arg>" lines */
void trace_reset(void);

#endif
