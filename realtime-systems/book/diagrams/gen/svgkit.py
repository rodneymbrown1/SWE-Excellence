"""svgkit -- tiny helpers for print-safe, accessible SVG figures.

Design rules (all figures):
  * readable in grayscale: meaning is carried by fill PATTERN + text label, never by colour alone
  * one accent colour (teal) used for emphasis only
  * every figure has <title> and <desc> (alt text) and role="img"
  * minimum text size ~11 px at the design width (figures are scaled to the text column, ~6.9 in)
"""
from xml.sax.saxutils import escape

INK = "#111"
SOFT = "#444"
ACC = "#0b5d73"        # accent (teal); contrast on white 7.6:1
ACC_L = "#d6e8ee"
GRAY1 = "#f1f1f1"
GRAY2 = "#d9d9d9"
GRAY3 = "#a8a8a8"

DEFS = """<defs>
<pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" height="6" fill="#fff"/><line x1="0" y1="0" x2="0" y2="6" stroke="#111" stroke-width="1.6"/></pattern>
<pattern id="dots" width="5" height="5" patternUnits="userSpaceOnUse"><rect width="5" height="5" fill="#fff"/><circle cx="2.5" cy="2.5" r="1" fill="#555"/></pattern>
<pattern id="cross" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" fill="#fff"/><path d="M0 0L6 6M6 0L0 6" stroke="#111" stroke-width="1"/></pattern>
<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#111"/></marker>
<marker id="arrA" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#0b5d73"/></marker>
</defs>"""


class Fig:
    def __init__(self, w, h, title, desc, uid):
        self.w, self.h, self.title, self.desc, self.uid = w, h, title, desc, uid
        self.parts = []

    def add(self, s):
        self.parts.append(s)

    def rect(self, x, y, w, h, fill="#fff", stroke=INK, sw=1.6, rx=0, dash=None, extra=""):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%s" fill="%s" stroke="%s" stroke-width="%s"%s %s/>' % (x, y, w, h, rx, fill, stroke, sw, d, extra))

    def line(self, x1, y1, x2, y2, stroke=INK, sw=1.6, dash=None, arrow=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        m = ""
        if arrow == "end":
            m = ' marker-end="url(#arr)"'
        elif arrow == "endA":
            m = ' marker-end="url(#arrA)"'
        elif arrow == "both":
            m = ' marker-end="url(#arr)" marker-start="url(#arr)"'
        self.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%s"%s%s/>' % (x1, y1, x2, y2, stroke, sw, d, m))

    def path(self, d, fill="none", stroke=INK, sw=1.6, dash=None, arrow=None):
        da = ' stroke-dasharray="%s"' % dash if dash else ""
        m = ' marker-end="url(#arr)"' if arrow == "end" else (' marker-end="url(#arrA)"' if arrow == "endA" else "")
        self.add('<path d="%s" fill="%s" stroke="%s" stroke-width="%s"%s%s/>' % (d, fill, stroke, sw, da, m))

    def text(self, x, y, s, size=13, weight=400, anchor="start", fill=INK, style="", rotate=None):
        tr = ' transform="rotate(%s %.1f %.1f)"' % (rotate, x, y) if rotate else ""
        self.add('<text x="%.1f" y="%.1f" font-size="%s" font-weight="%s" text-anchor="%s" fill="%s"%s%s>%s</text>' % (x, y, size, weight, anchor, fill, (' style="%s"' % style) if style else "", tr, escape(s)))

    def lines(self, x, y, ss, size=13, lh=1.25, weight=400, anchor="start", fill=INK):
        for i, s in enumerate(ss):
            self.text(x, y + i * size * lh, s, size, weight, anchor, fill)

    def box(self, x, y, w, h, label, sub=None, fill="#fff", stroke=INK, size=13, weight=700, rx=4, sw=1.8, dash=None):
        self.rect(x, y, w, h, fill, stroke, sw, rx, dash)
        if sub:
            self.text(x + w / 2, y + h / 2 - 3, label, size, weight, "middle")
            self.text(x + w / 2, y + h / 2 + size, sub, size - 2, 400, "middle", SOFT)
        else:
            self.text(x + w / 2, y + h / 2 + size * 0.35, label, size, weight, "middle")

    def render(self):
        return ('<svg viewBox="0 0 %d %d" role="img" aria-labelledby="%s-t %s-d" xmlns="http://www.w3.org/2000/svg">'
                '<title id="%s-t">%s</title><desc id="%s-d">%s</desc>%s%s</svg>' %
                (self.w, self.h, self.uid, self.uid, self.uid, escape(self.title), self.uid, escape(self.desc), DEFS, "".join(self.parts)))


# ----------------------------------------------------------------------------- timeline (Gantt) from a rtsim Result

def gantt(res, uid, title, desc, t0=0, t1=None, px=14.0, row_h=34, label_w=78, names=None, mark_deadlines=True, show_axis_every=5, extra_note=None, pad_right=18):
    """Draw an rtsim.Result as a print-safe Gantt chart.
    solid dark = running, dotted = ready but not running, hatched = blocked on a resource, X = deadline miss."""
    t1 = res.horizon if t1 is None else t1
    names = names or [t.name for t in sorted(res.tasks, key=lambda t: -(t.prio or 0))]
    n = len(names)
    W = int(label_w + (t1 - t0) * px + pad_right)
    H = 34 + n * row_h + 46
    f = Fig(W, H, title, desc, uid)
    top = 26
    # axis
    for t in range(t0, t1 + 1):
        x = label_w + (t - t0) * px
        if (t - t0) % show_axis_every == 0:
            f.line(x, top - 6, x, top + n * row_h + 4, "#bbb", 0.8)
            f.text(x, top - 10, str(t), 11, 400, "middle", SOFT)
    for r, name in enumerate(names):
        y = top + r * row_h
        f.text(label_w - 8, y + row_h * 0.62, name, 13, 700, "end")
        f.line(label_w, y + row_h - 3, label_w + (t1 - t0) * px, y + row_h - 3, "#ddd", 0.8)
    idx = {nm: i for i, nm in enumerate(names)}
    # ready spans
    for j in res.jobs:
        if j.task.name not in idx:
            continue
        fin = j.finish if j.finish is not None else res.horizon
        for t in range(max(j.release, t0), min(fin, t1)):
            if res.timeline[t] != j.task.name and j.task.name not in res.blocked[t]:
                y = top + idx[j.task.name] * row_h
                f.rect(label_w + (t - t0) * px, y + 8, px, row_h - 16, "url(#dots)", "#777", 0.6)
    for t in range(t0, t1):
        for nm in res.blocked[t]:
            if nm in idx:
                y = top + idx[nm] * row_h
                f.rect(label_w + (t - t0) * px, y + 8, px, row_h - 16, "url(#hatch)", INK, 0.8)
        nm = res.timeline[t]
        if nm in idx:
            y = top + idx[nm] * row_h
            holding = res.holding[t]
            f.rect(label_w + (t - t0) * px, y + 6, px, row_h - 12, ACC if holding else INK, "#fff", 0.6)
    # releases / deadlines
    for j in res.jobs:
        if j.task.name not in idx:
            continue
        y = top + idx[j.task.name] * row_h
        if t0 <= j.release <= t1:
            x = label_w + (j.release - t0) * px
            f.line(x, y + 2, x, y + 10, INK, 1.4)
            f.path("M%.1f %.1f l-3 4 l6 0 z" % (x, y + 12), INK, INK, 0.5)
        if mark_deadlines and t0 <= j.deadline <= t1:
            x = label_w + (j.deadline - t0) * px
            f.line(x, y + row_h - 14, x, y + row_h - 3, SOFT, 1.2, dash="2 2")
        if j.missed and j.finish is not None and t0 <= j.finish <= t1:
            x = label_w + (j.finish - t0) * px
            f.text(x, y + 14, "X", 14, 800, "middle", "#b00020")
    # legend
    ly = top + n * row_h + 14
    lx = label_w
    f.rect(lx, ly, 14, 12, INK, "#fff", 0.6); f.text(lx + 19, ly + 10, "running", 11)
    f.rect(lx + 78, ly, 14, 12, "url(#dots)", "#777", 0.6); f.text(lx + 97, ly + 10, "ready (waiting for CPU)", 11)
    f.rect(lx + 245, ly, 14, 12, "url(#hatch)", INK, 0.8); f.text(lx + 264, ly + 10, "blocked on lock", 11)
    f.rect(lx + 372, ly, 14, 12, ACC, "#fff", 0.6); f.text(lx + 391, ly + 10, "running, holding the lock", 11)
    f.text(lx, ly + 28, "tick up-arrow = release   dashed tick = deadline   X = deadline missed" + (("   " + extra_note) if extra_note else ""), 11, 400, "start", SOFT)
    f.h = ly + 36
    return f.render()
