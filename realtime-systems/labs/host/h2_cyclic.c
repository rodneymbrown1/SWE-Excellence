/* h2_cyclic.c -- Lab H2: a cyclic executive (the "boxcar") on a virtual clock.
 *
 * Time is simulated in microseconds, so the output is identical on every run.
 *
 *   minor cycle (frame) = 10 ms        major cycle (hyperperiod) = 40 ms
 *   tasks:  A every frame (10 ms)  | B every 2nd frame (20 ms) | C every 4th frame (40 ms)
 *
 *   ./h2_cyclic                  nominal execution times
 *   ./h2_cyclic overrun          task B takes 6 ms longer than budget in major cycle #2
 *   ./h2_cyclic overrun skip     same, but the executive SKIPS tasks it cannot start in time
 */
#include <stdio.h>
#include <string.h>

#define FRAME_US 10000
#define NTASKS 3

typedef struct { const char *name; int every; int budget_us; } task_t;
static const task_t tasks[NTASKS] = { { "A", 1, 2000 }, { "B", 2, 3000 }, { "C", 4, 4000 } };

static int extra_us(int frame, const char *name, int inject) {
    return (inject && frame / 4 == 2 && name[0] == 'B') ? 6000 : 0;   /* overrun in major cycle #2 */
}

int main(int argc, char **argv) {
    int inject = argc > 1 && strcmp(argv[1], "overrun") == 0;
    int skip = argc > 2 && strcmp(argv[2], "skip") == 0;
    long now = 0;
    int late_frames = 0;
    printf("frame  start_ms  task  begins_ms  ends_ms  note\n");
    for (int f = 0; f < 16; f++) {
        long frame_start = (long)f * FRAME_US, frame_end = frame_start + FRAME_US;
        if (now < frame_start) now = frame_start;               /* the executive waits for the frame timer */
        else if (now > frame_start) { late_frames++; }          /* we are already behind: the frame starts late */
        for (int i = 0; i < NTASKS; i++) {
            if (f % tasks[i].every != 0) continue;
            if (skip && now + tasks[i].budget_us > frame_end) { printf("%5d  %8ld  %-4s  %9s  %7s  SKIPPED (its budget no longer fits in this frame)\n", f, frame_start / 1000, tasks[i].name, "-", "-"); continue; }
            long b = now;
            now += tasks[i].budget_us + extra_us(f, tasks[i].name, inject);
            printf("%5d  %8ld  %-4s  %9.1f  %7.1f  %s\n", f, frame_start / 1000, tasks[i].name, b / 1000.0, now / 1000.0,
                   now > frame_end ? "** crossed the frame boundary **" : "");
        }
    }
    printf("\nframes that STARTED late (domino effect): %d of 16\n", late_frames);
    return 0;
}
