/* startup.c -- vector table, reset, and a fault handler that tells you where it died. */
#include <stdint.h>
#include "bsp.h"

extern uint32_t _sidata, _sdata, _edata, _sbss, _ebss, _estack;
extern int main(void);

void Reset_Handler(void);
void Default_Handler(void);
void HardFault_Handler(void);

/* FreeRTOS handlers (names set by FreeRTOSConfig.h: vPortSVCHandler -> SVC_Handler, etc.) */
void SVC_Handler(void)     __attribute__((weak, alias("Default_Handler")));
void PendSV_Handler(void)  __attribute__((weak, alias("Default_Handler")));
void SysTick_Handler(void) __attribute__((weak, alias("Default_Handler")));
void TIMER0_Handler(void)  __attribute__((weak, alias("Default_Handler")));
void TIMER1_Handler(void)  __attribute__((weak, alias("Default_Handler")));

#define NIRQ 48
__attribute__((section(".isr_vector"), used))
void (*const vector_table[16 + NIRQ])(void) = {
    (void (*)(void))(&_estack),   /* 0: initial stack pointer */
    Reset_Handler,                /* 1 */
    Default_Handler,              /* 2: NMI */
    HardFault_Handler,            /* 3 */
    Default_Handler,              /* 4: MemManage */
    Default_Handler,              /* 5: BusFault */
    Default_Handler,              /* 6: UsageFault */
    0, 0, 0, 0,                   /* 7-10 */
    SVC_Handler,                  /* 11 */
    Default_Handler,              /* 12: DebugMon */
    0,                            /* 13 */
    PendSV_Handler,               /* 14 */
    SysTick_Handler,              /* 15 */
    /* external interrupts: 0..47; TIMER0 = 8, TIMER1 = 9 on mps2-an385 */
    [16 + 8] = TIMER0_Handler,
    [16 + 9] = TIMER1_Handler,
};

void Reset_Handler(void) {
    for (uint32_t *s = &_sidata, *d = &_sdata; d < &_edata;) *d++ = *s++;
    for (uint32_t *d = &_sbss; d < &_ebss;) *d++ = 0;
    /* fill the rest of RAM below the main stack lightly? no: keep boot fast */
    bsp_init();
    main();
    bsp_exit(0);
}

void Default_Handler(void) { kprintf("\n*** unexpected exception/interrupt ***\n"); bsp_exit(1); }

/* HardFault: print the stacked registers (PC is where the fault happened), then stop the run. */
__attribute__((used)) void hardfault_c(uint32_t *sp) {
    kprintf("\n*** HardFault ***\n r0=%08x r1=%08x r2=%08x r3=%08x\n r12=%08x lr=%08x pc=%08x psr=%08x\n",
            (unsigned)sp[0], (unsigned)sp[1], (unsigned)sp[2], (unsigned)sp[3], (unsigned)sp[4], (unsigned)sp[5], (unsigned)sp[6], (unsigned)sp[7]);
    kprintf(" CFSR=%08x HFSR=%08x\n", (unsigned)*(volatile uint32_t *)0xE000ED28, (unsigned)*(volatile uint32_t *)0xE000ED2C);
    bsp_exit(2);
}
__attribute__((naked)) void HardFault_Handler(void) {
    __asm volatile("tst lr, #4\n ite eq\n mrseq r0, msp\n mrsne r0, psp\n b hardfault_c\n");
}
