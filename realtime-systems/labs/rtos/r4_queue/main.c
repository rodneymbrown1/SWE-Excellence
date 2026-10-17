/* R4: an interrupt produces messages, a task consumes them.  What does "queue full" do?
 *
 * Same traffic as host lab H4: a timer interrupt fires every 1 ms.  Every 10th interrupt posts one message (100 msg/s),
 * and during 20 consecutive milliseconds each second it posts an extra one (burst: 1100 msg/s).  The consumer needs
 * 5 ms per message (capacity 200 msg/s).  Mean load = 60%, but the burst arrives faster than it can be drained.
 *
 * For each queue length and overflow policy we report delivered / dropped / peak depth / latency (ISR post -> done).
 */
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"
#include "bsp.h"

typedef struct { uint32_t seq; uint32_t t_us; } msg_t;

#define RUN_MS      5000
#define SERVICE_US  5000
enum { DROP_NEWEST, DROP_OLDEST };

static QueueHandle_t q;
static volatile int policy;
static volatile uint32_t isr_n, seq, dropped, produced, peak;
static uint32_t lat[2048], nlat;
static volatile uint32_t done_flag;

static void post(BaseType_t *woken) {
    msg_t m = { seq++, now_us() };
    produced++;
    if (xQueueSendToBackFromISR(q, &m, woken) != pdTRUE) {
        dropped++;                                              /* the producer cannot block in an ISR: drop and COUNT it */
        if (policy == DROP_OLDEST) {
            msg_t old;
            xQueueReceiveFromISR(q, &old, woken);                /* discard the oldest ... */
            xQueueSendToBackFromISR(q, &m, woken);               /* ... and keep the newest */
        }
    }
    uint32_t d = (uint32_t)uxQueueMessagesWaitingFromISR(q);
    if (d > peak) peak = d;
}

static void producer_isr(void) {
    BaseType_t woken = pdFALSE;
    uint32_t n = isr_n++;
    uint32_t ms_in_s = n % 1000;
    if (n % 10 == 0) post(&woken);
    if (ms_in_s >= 500 && ms_in_s < 520) post(&woken);
    if (n >= RUN_MS) { timer1_stop(); done_flag = 1; }
    portYIELD_FROM_ISR(woken);
}

static void consumer(void *arg) {
    msg_t m;
    for (;;) {
        if (xQueueReceive(q, &m, portMAX_DELAY) == pdTRUE) {
            burn_us(SERVICE_US);
            if (nlat < 2048) lat[nlat++] = now_us() - m.t_us;
        }
    }
}

static void sort(uint32_t *a, uint32_t n) {                   /* tiny shell sort: there is no libc qsort */
    for (uint32_t gap = n / 2; gap > 0; gap /= 2)
        for (uint32_t i = gap; i < n; i++) { uint32_t t = a[i], j = i; for (; j >= gap && a[j - gap] > t; j -= gap) a[j] = a[j - gap]; a[j] = t; }
}

static void run_case(int depth, int pol, const char *name) {
    isr_n = seq = dropped = produced = peak = done_flag = nlat = 0;
    policy = pol;
    q = xQueueCreate((UBaseType_t)depth, sizeof(msg_t));
    TaskHandle_t c;
    xTaskCreate(consumer, "consumer", 2 * configMINIMAL_STACK_SIZE, NULL, 3, &c);
    vTaskDelay(1);
    timer1_start(1000, producer_isr);
    while (!done_flag) vTaskDelay(10);
    vTaskDelay(pdMS_TO_TICKS(600));                             /* let the consumer drain what is left */
    uint32_t delivered = nlat;
    sort(lat, nlat);
    kprintf("%-12s %5d %9lu %8lu %9lu %9lu %10lu\n", name, depth, (unsigned long)delivered, (unsigned long)dropped, (unsigned long)(peak),
            (unsigned long)(nlat ? lat[nlat / 2] / 1000 : 0), (unsigned long)(nlat ? lat[nlat - 1] / 1000 : 0));
    vTaskDelete(c);
    vQueueDelete(q);
}

static void manager(void *arg) {
    kprintf("R4: ISR producer (100/s + 20-message burst each second), consumer 5 ms/msg, %d ms of traffic per case\n\n", RUN_MS);
    kprintf("%-12s %5s %9s %8s %9s %9s %10s\n", "policy", "depth", "delivered", "dropped", "peak depth", "p50 ms", "max lat ms");
    const int depths[] = { 4, 8, 18, 19, 32 };
    for (unsigned i = 0; i < sizeof depths / sizeof depths[0]; i++) run_case(depths[i], DROP_NEWEST, "drop_newest");
    kprintf("\n");
    for (unsigned i = 0; i < 4; i++) run_case(depths[i], DROP_OLDEST, "drop_oldest");
    kprintf("\nNote 'peak depth' counts queued items only (the one being processed is not in the queue).\n");
    bsp_exit(0);
}

int main(void) {
    xTaskCreate(manager, "manager", 3 * configMINIMAL_STACK_SIZE, NULL, 5, NULL);
    vTaskStartScheduler();
    for (;;) { }
}
