# Shared build rules.  A lab Makefile sets NAME (and optionally EXTRA_CFLAGS, HEAP) then includes this file.
HERE      := $(dir $(lastword $(MAKEFILE_LIST)))
FREERTOS  ?= $(abspath $(HERE)/../../third_party/FreeRTOS-Kernel)
HEAP      ?= heap_4
OPT       ?= -O1
CROSS     ?= arm-none-eabi-
CC        := $(CROSS)gcc
SIZE      := $(CROSS)size

KSRC := $(FREERTOS)/tasks.c $(FREERTOS)/queue.c $(FREERTOS)/list.c $(FREERTOS)/timers.c \
        $(FREERTOS)/event_groups.c $(FREERTOS)/stream_buffer.c \
        $(FREERTOS)/portable/GCC/ARM_CM3/port.c $(FREERTOS)/portable/MemMang/$(HEAP).c
CSRC := $(HERE)startup.c $(HERE)bsp.c $(HERE)libc_min.c $(HERE)lab.c
SRC  := $(KSRC) $(CSRC) $(wildcard *.c)

CPU      := -mcpu=cortex-m3 -mthumb
INCLUDES := -I. -isystem $(HERE)sysinc -I$(HERE) -I$(FREERTOS)/include -I$(FREERTOS)/portable/GCC/ARM_CM3
# -O1 keeps timing loops honest; -g3 keeps every symbol and macro visible to the debugger (see the Debugging project).
CFLAGS   := $(CPU) $(OPT) -g3 -std=gnu11 -Wall -Wextra -Wno-unused-parameter -ffreestanding -fno-builtin \
            -ffunction-sections -fdata-sections $(INCLUDES) $(EXTRA_CFLAGS)
LDFLAGS  := $(CPU) -nostdlib -T $(HERE)mps2_m3.ld -Wl,--gc-sections -Wl,-Map=build/$(NAME).map

build/$(NAME).elf: $(SRC) $(wildcard *.h) $(HERE)FreeRTOSConfig.h $(HERE)bsp.h
	@mkdir -p build
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $(SRC) -lgcc
	@$(SIZE) $@

clean:
	rm -rf build
.PHONY: clean
