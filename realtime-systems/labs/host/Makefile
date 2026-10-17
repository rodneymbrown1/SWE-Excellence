# Host labs: plain C + Python 3, no dependencies. -O0 -g so the debugger shows everything (see the Debugging project).
CC      ?= cc
CFLAGS  ?= -std=c11 -O0 -g -Wall -Wextra

BINS = h1_loop h1_tickwrap h2_cyclic

all: $(BINS)

h1_loop: h1_loop.c
	$(CC) $(CFLAGS) -o $@ $<
h1_tickwrap: h1_tickwrap.c
	$(CC) $(CFLAGS) -o $@ $<
h2_cyclic: h2_cyclic.c
	$(CC) $(CFLAGS) -o $@ $<

test: all
	python3 rtsim.py
	python3 h1_patriot.py
	./h1_tickwrap
	./h2_cyclic overrun

clean:
	rm -rf $(BINS) *.dSYM __pycache__

.PHONY: all test clean
