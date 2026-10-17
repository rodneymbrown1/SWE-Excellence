#!/usr/bin/env python3
"""Generate every SVG figure into book/diagrams/.   python3 book/diagrams/gen/make_figures.py
Figures that come from lab output read labs/transcripts/*, so run the lab captures first."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import figures_a, figures_b, figures_c


def write(name, svg):
    with open(os.path.join(OUT, name + ".svg"), "w") as fh:
        fh.write(svg)


for name, fn in figures_a.ALL + figures_c.ALL:
    write(name, fn())
for name, fn in figures_b.ALL_SINGLE:
    write(name, fn())
a, b = figures_b.g_setB_pair()
write("gantt-setb-rm", a); write("gantt-setb-edf", b)
for k, v in figures_b.g_inversion().items():
    write("gantt-inversion-" + k, v)
t1, t2 = figures_b.g_trace_inversion()
write("trace-inversion-p1", t1); write("trace-inversion-p2", t2)
write("trace-r10", figures_b.g_trace_r10())
print("wrote", len([f for f in os.listdir(OUT) if f.endswith(".svg")]), "figures to", OUT)
