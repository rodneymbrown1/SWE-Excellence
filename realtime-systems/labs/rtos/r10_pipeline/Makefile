NAME = r10_pipeline
# make DUMP=1   : also print one "L <latency_us>" line per actuation (feed to tools/lathist.py)
# make TRACE=1  : also dump a context-switch trace (feed to tools/trace2gantt.py)
# make REVEAL=1 : ANSWER KEY -- print the hidden counters (do this last)
DUMP ?= 0
TRACE ?= 0
REVEAL ?= 0
EXTRA_CFLAGS = -DDUMP=$(DUMP) -DDUMP_TRACE=$(TRACE) -DREVEAL=$(REVEAL) $(if $(filter 1,$(TRACE)),-DLAB_TRACE,)
include ../common/rules.mk
