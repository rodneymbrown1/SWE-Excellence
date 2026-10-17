/* h1_loop.c -- Lab H1: a loop that wants to run every PERIOD microseconds.
 *
 *   ./h1_loop MODE [period_us] [work_us] [iterations] [noise_us]
 *
 *   MODE = busy      spin until the next period boundary (polling the clock)
 *          sleep_rel do the work, then sleep for `period` (the classic mistake: drift)
 *          sleep_abs do the work, then sleep until the *next scheduled instant*
 *
 *   noise_us : every 17th iteration the work takes `noise_us` longer (a rare slow path)
 *
 * It reports, per iteration, how late the loop STARTED relative to the ideal schedule
 * (start0 + i*period) -- that is the jitter -- and the interval between starts.
 */
#define _POSIX_C_SOURCE 200809L
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static inline int64_t now_us(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (int64_t)ts.tv_sec * 1000000 + ts.tv_nsec / 1000;
}

static void sleep_until_us(int64_t target) {
    int64_t d = target - now_us();
    if (d <= 0) return;
    struct timespec req = { .tv_sec = d / 1000000, .tv_nsec = (d % 1000000) * 1000 };
    nanosleep(&req, NULL);
}

static void work(int64_t us) {            /* burn CPU for `us` microseconds */
    int64_t end = now_us() + us;
    while (now_us() < end) { }
}

static int cmp64(const void *a, const void *b) {
    int64_t x = *(const int64_t *)a, y = *(const int64_t *)b;
    return (x > y) - (x < y);
}

int main(int argc, char **argv) {
    const char *mode = argc > 1 ? argv[1] : "sleep_abs";
    int64_t period = argc > 2 ? atoll(argv[2]) : 10000;
    int64_t wk     = argc > 3 ? atoll(argv[3]) : 2000;
    int n          = argc > 4 ? atoi(argv[4]) : 300;
    int64_t noise  = argc > 5 ? atoll(argv[5]) : 0;
    int64_t *late = malloc(sizeof(int64_t) * n), *interval = malloc(sizeof(int64_t) * n);
    int64_t t0 = now_us(), prev = t0;
    for (int i = 0; i < n; i++) {
        int64_t start = now_us();
        late[i] = start - (t0 + (int64_t)i * period);
        interval[i] = start - prev;
        prev = start;
        work(wk + ((noise && i % 17 == 16) ? noise : 0));
        if (strcmp(mode, "busy") == 0) {
            int64_t next = t0 + (int64_t)(i + 1) * period;
            while (now_us() < next) { }                       /* spin: exact, but burns the CPU */
        } else if (strcmp(mode, "sleep_rel") == 0) {
            struct timespec r = { .tv_sec = period / 1000000, .tv_nsec = (period % 1000000) * 1000 };
            nanosleep(&r, NULL);                              /* sleeps `period` AFTER the work: period = work + period */
        } else {
            sleep_until_us(t0 + (int64_t)(i + 1) * period);   /* sleep to an absolute instant: no accumulated drift */
        }
    }
    int64_t total = now_us() - t0;
    qsort(late, n, sizeof(int64_t), cmp64);
    qsort(interval + 1, n - 1, sizeof(int64_t), cmp64);
    printf("mode=%s period=%lldus work=%lldus noise=%lldus iterations=%d\n", mode, (long long)period, (long long)wk, (long long)noise, n);
    printf("wall time: %.1f ms   ideal: %.1f ms   drift: %.1f ms\n", total / 1000.0, n * period / 1000.0, (total - (int64_t)n * period) / 1000.0);
    printf("start lateness (us):  min=%lld  median=%lld  p99=%lld  max=%lld\n", (long long)late[0], (long long)late[n / 2], (long long)late[(n * 99) / 100], (long long)late[n - 1]);
    printf("interval (us):        min=%lld  median=%lld  p99=%lld  max=%lld\n", (long long)interval[1], (long long)interval[n / 2], (long long)interval[(n * 99) / 100], (long long)interval[n - 1]);
    free(late); free(interval);
    return 0;
}
