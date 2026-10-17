/* h1_tickwrap.c -- Lab H1b: every counter wraps.
 *
 * An RTOS tick is a fixed-width unsigned counter. Application code that compares two tick values
 * with ">=" works for a while and then fails when the counter wraps. The correct comparison
 * subtracts first, in unsigned arithmetic, and looks at the SIGN of the difference.
 *
 *   ./h1_tickwrap          (uses an 8-bit "tick" so the wrap is easy to see)
 */
#include <stdint.h>
#include <stdio.h>

typedef uint8_t tick_t;                      /* the lab shrinks the type; real kernels use 16 or 32 bits */

static int expired_naive(tick_t now, tick_t deadline) { return now >= deadline; }
static int expired_safe(tick_t now, tick_t deadline)  { return (int8_t)(tick_t)(now - deadline) >= 0; }

int main(void) {
    tick_t start = 240;                      /* 16 ticks before the counter wraps to 0 */
    tick_t timeout = 30;                     /* ask for a 30-tick timeout */
    tick_t deadline = (tick_t)(start + timeout);   /* = 14 after wrap-around */
    printf("start=%u timeout=%u deadline=%u (wrapped)\n\n", start, timeout, deadline);
    printf("elapsed  now  naive(now>=deadline)  safe((int8)(now-deadline)>=0)\n");
    for (int elapsed = 0; elapsed <= 40; elapsed += 4) {
        tick_t now = (tick_t)(start + elapsed);
        int n = expired_naive(now, deadline), s = expired_safe(now, deadline);
        printf("%5d  %4u  %-20s%-20s%s\n", elapsed, now, n ? "EXPIRED" : "waiting", s ? "EXPIRED" : "waiting",
               n != s ? "   <-- naive is wrong" : "");
    }
    printf("\nThe naive test says 'expired' at elapsed=0 (it is already >= 14), so a 30-tick timeout fires immediately.\n");
    printf("The safe test is correct as long as the interval you measure is less than half the counter range (127 here).\n");
    return 0;
}
