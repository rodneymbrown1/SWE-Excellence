#!/usr/bin/env python3
"""Build the ON TIME documents:  Markdown -> HTML (pandoc) -> PDF (headless Chrome).

usage:  python3 print/build.py [book|handbook|labs|all]
Needs: pandoc, Google Chrome, pdftotext/pdfinfo (poppler).  Fonts are local (print/fonts).

Markdown conventions
  # Title {.chapter data-part="PART 1 · TIME"}      numbered chapter (data-part is optional: prints a part label)
  # Title {.chapter data-label="Lab R3"}            explicit label instead of an auto number
  # Title {.appendix}                               Appendix A, B, ...
  {{fig:name | Caption text}}                        inline book/diagrams/name.svg as a numbered figure
  ::: rule / trap / try / why / note / check / case  callout boxes (see style.css)
"""
import html, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRINT = os.path.join(ROOT, "print")
DIAGRAMS = os.path.join(ROOT, "book", "diagrams")
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
PANDOC_FMT = "markdown+fenced_divs+pipe_tables+bracketed_spans+backtick_code_blocks+raw_html+smart+header_attributes+definition_lists"

DOCS = {
    "book": dict(title="ON TIME", running="ON TIME", pdf="on-time-book.pdf", base="11.2", chapters=os.path.join(ROOT, "book", "chapters"),
                 kicker="SWE Excellence · Real-time fundamentals", sub="Timing, scheduling, messaging, synchronization, reliability and observability — for software engineers who build on top of an RTOS.",
                 art="cover-art", foot="Reference implementation: FreeRTOS on QEMU. Every [RAN] result was executed; every claim traces to research/.", label="Chapter", toc=True),
    "handbook": dict(title="FIELD HANDBOOK", running="ON TIME · Field Handbook", pdf="on-time-handbook.pdf", base="10.4", chapters=os.path.join(ROOT, "handbook", "chapters"),
                     kicker="SWE Excellence · First day on the device", sub="What to do, what to ask and what to check when you build, debug or simply need to understand an application on an RTOS.",
                     art="recon-flow", foot="A working document: print it, write in it, keep it next to the keyboard.", label="Section", toc=True),
    "labs": dict(title="LAB WORKBOOK", running="ON TIME · Lab Workbook", pdf="on-time-labs.pdf", base="10.6", chapters=os.path.join(ROOT, "labs", "workbook"),
                 kicker="SWE Excellence · Hands-on", sub="Sixteen labs plus setup: five on your laptop, eleven on a real RTOS in an emulator — including a gdb session and a capstone with planted defects.",
                 art="trace-inversion-p1", foot="Needs: a C compiler, Python 3, QEMU, arm-none-eabi-gcc/gdb. Setup in Lab 0.", label="Lab", toc=True),
}


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def pandoc(md_text):
    p = subprocess.run(["pandoc", "-f", PANDOC_FMT, "-t", "html5", "--no-highlight", "--wrap=none"], input=md_text, capture_output=True, text=True, check=True)
    return p.stdout


class Counter:
    def __init__(self):
        self.fig = 0


def inline_figs(h, ctr):
    def sub(m):
        name, cap = m.group(1), (m.group(2) or "").strip()
        path = os.path.join(DIAGRAMS, name + ".svg")
        if not os.path.exists(path):
            return "<p><b>[missing figure %s]</b></p>" % name
        svg = re.sub(r"<\?xml.*?\?>", "", open(path).read()).strip()
        cls = ""
        if cap.startswith("[small]"):
            cls, cap = ' class="small"', cap[7:].strip()
        if cap:
            ctr.fig += 1
            return "<figure%s>%s<figcaption><b>Figure %d.</b> %s</figcaption></figure>" % (cls, svg, ctr.fig, cap)
        return "<figure%s>%s</figure>" % (cls, svg)
    return re.sub(r"(?:<p>)?\{\{fig:([\w\-]+)\s*(?:\|\s*(.*?))?\}\}(?:</p>)?", sub, h, flags=re.S)


def mark_long_tables(h):
    def f(m):
        t = m.group(0)
        return t.replace("<table>", '<table class="keep">', 1) if t.count("<tr") <= 4 else t
    return re.sub(r"<table>.*?</table>", f, h, flags=re.S)


def mark_callouts(h):
    """Callout boxes longer than ~650 characters may split across pages (class "long"); short ones stay whole."""
    def f(m):
        cls, body = m.group(1), m.group(2)
        if len(re.sub(r"<[^>]+>", "", body)) > 650:
            return '<div class="%s long">%s</div>' % (cls, body)
        return m.group(0)
    return re.sub(r'<div class="(rule|trap|try|why|note|check|case)">(.*?)</div>(?=\s*(?:<|$))', f, h, flags=re.S)


def mark_pre(h):
    def f(m):
        return m.group(0).replace("<pre", '<pre class="long"', 1) if m.group(0).count("\n") > 38 else m.group(0)
    return re.sub(r"<pre[^>]*>.*?</pre>", f, h, flags=re.S)


def expand_transcripts(md):
    """{{transcript:NAME}} / {{transcript:NAME:N}} / {{transcript:NAME:A-B}} -> fenced block with real lab output."""
    def sub(m):
        name, rng = m.group(1), m.group(2)
        path = os.path.join(ROOT, "labs", "transcripts", name)
        if not os.path.exists(path):
            return "```out\n[missing transcript %s]\n```" % name
        lines = open(path, errors="replace").read().rstrip("\n").split("\n")
        if rng:
            if "-" in rng:
                a, b = rng.split("-")
                lines = lines[int(a) - 1:int(b)]
            else:
                lines = lines[:int(rng)]
        lines = [l.rstrip() for l in lines]
        return "```out\n" + "\n".join(lines) + "\n```"
    return re.sub(r"^\{\{transcript:([\w.\-]+)(?::([\d\-]+))?\}\}\s*$", sub, md, flags=re.M)


def build_body(files, cfg):
    ctr = Counter()
    n = appx = 0
    toc, parts = [], []
    last_part = None
    out = []
    for cf in files:
        h = pandoc(expand_transcripts(open(cf).read()))
        h = inline_figs(h, ctr)
        h = mark_callouts(mark_long_tables(mark_pre(h)))

        def h1(m):
            nonlocal n, appx, last_part
            attrs, text = m.group(1), m.group(2)
            cls = (re.search(r'class="([^"]*)"', attrs) or [None, ""])[1]
            cid = (re.search(r'id="([^"]*)"', attrs) or [None, ""])[1]
            part = (re.search(r'data-part="([^"]*)"', attrs) or [None, None])[1]
            explicit = (re.search(r'data-label="([^"]*)"', attrs) or [None, None])[1]
            plain = re.sub(r"<[^>]+>", "", text)
            if part and part != last_part:
                toc.append(("part", "", html.unescape(part.split("·", 1)[-1].strip() if False else part), ""))
                last_part = part
            extra = ' data-part="%s"' % part if part else ""
            if "chapter" in cls.split():
                if explicit:
                    label, num = explicit, explicit.replace("Lab ", "").replace(cfg["label"] + " ", "")
                else:
                    n += 1
                    label, num = "%s %d" % (cfg["label"], n), str(n)
                toc.append(("chapter", num, plain, cid))
                return '<h1 id="%s" class="%s" data-label="%s"%s>%s</h1>' % (cid, cls, label, extra, text)
            if "appendix" in cls.split():
                letter = chr(ord("A") + appx)
                appx += 1
                toc.append(("chapter", letter, plain, cid))
                return '<h1 id="%s" class="%s" data-label="Appendix %s"%s>%s</h1>' % (cid, cls, letter, extra, text)
            toc.append(("chapter", "", plain, cid))
            return "<h1%s>%s</h1>" % (attrs, text)
        h = re.sub(r"<h1([^>]*)>(.*?)</h1>", h1, h, flags=re.S)
        out.append(h)
    return out, toc


def toc_html(toc, pages):
    out = ['<section class="toc"><h1 class="nobreak">Contents</h1><ol>']
    for kind, num, text, cid in toc:
        if kind == "part":
            out.append('<li class="part">%s</li>' % html.escape(text))
        else:
            label = ("%s&nbsp;&nbsp;" % num) if num else ""
            pg = pages.get(cid, "") if pages else ""
            out.append('<li><span class="t">%s%s</span><span class="dots"></span><span class="p">%s</span></li>' % (label, html.escape(text), pg))
    out.append("</ol></section>")
    return "\n".join(out)


def cover_html(cfg):
    art = ""
    p = os.path.join(DIAGRAMS, cfg["art"] + ".svg")
    if os.path.exists(p):
        art = '<div class="art">%s</div>' % re.sub(r"<\?xml.*?\?>", "", open(p).read()).strip()
    six = ""
    if cfg["title"] == "ON TIME":
        six = '<div class="six">1&nbsp; Timing<br>2&nbsp; Scheduling<br>3&nbsp; Messaging<br>4&nbsp; Synchronization<br>5&nbsp; Reliability<br>6&nbsp; Observability</div>'
    t = cfg["title"].replace(" ", "<br>") if len(cfg["title"]) < 12 else cfg["title"]
    return ('<section class="cover"><div class="band"><div class="kicker">%s</div><h1>%s</h1><div class="sub">%s</div></div>%s%s<div class="foot">%s</div></section>'
            % (cfg["kicker"], t, cfg["sub"], art, six, cfg["foot"]))


def chrome_pdf(html_path, pdf_path):
    run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files", "--export-tagged-pdf",
         "--generate-pdf-document-outline", "--virtual-time-budget=30000", "--print-to-pdf=" + pdf_path, "file://" + html_path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def pdf_pages(pdf):
    return int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout).group(1))


def page_map(pdf, toc, first_page=3):
    npages = pdf_pages(pdf)
    texts = []
    for p in range(1, npages + 1):
        t = subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), "-layout", pdf, "-"], capture_output=True, text=True).stdout
        texts.append(re.sub(r"\s+", " ", t))
    pages, start = {}, first_page
    for kind, num, text, cid in toc:
        if kind != "chapter":
            continue
        key = re.sub(r"\s+", " ", text).strip()[:38]
        for i in range(start - 1, npages):
            if key in texts[i][:500]:
                pages[cid] = i + 1
                start = i + 1
                break
    return pages, npages


def write_doc(path, css, fonts, inner, title):
    doc = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>%s</title><meta name="viewport" content="width=device-width,initial-scale=1">'
           '<meta name="author" content="SWE Excellence"><style>%s\n%s</style></head><body>%s</body></html>' % (html.escape(title), fonts, css, inner))
    open(path, "w").write(doc)


def render_unit(unit_html, z, css, fonts, tmp, tag):
    """Render one chapter on its own at zoom z; return (pages, fill of the last page)."""
    import hashlib
    from PIL import Image
    path = os.path.join(tmp, "u_%s.html" % tag)
    pdf = os.path.join(tmp, "u_%s.pdf" % tag)
    write_doc(path, css, fonts, '<div class="unit" style="zoom:%.3f">%s</div>' % (z, unit_html), "unit")
    run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files", "--user-data-dir=" + os.path.join(tmp, "prof_" + tag),
         "--virtual-time-budget=30000", "--print-to-pdf=" + pdf, "file://" + path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    n = pdf_pages(pdf)
    png = os.path.join(tmp, "u_%s" % tag)
    subprocess.run(["pdftoppm", "-r", "50", "-gray", "-png", pdf, png], check=True)
    fills = []
    top, bottom = int(0.75 * 50), int(10.1 * 50)
    for f in sorted(x for x in os.listdir(tmp) if x.startswith("u_%s-" % tag) and x.endswith(".png")):
        im = Image.open(os.path.join(tmp, f)).convert("L")
        w, h = im.size
        px = im.load()
        last = top
        for y in range(min(bottom, h) - 1, top, -1):
            if any(px[x, y] < 200 for x in range(30, w - 30)):
                last = y
                break
        fills.append(max(0.0, min(1.0, (last - top) / float(bottom - top))))
        os.remove(os.path.join(tmp, f))
    return n, fills


Z_ORDER = [1.00, 0.99, 1.01, 0.98, 1.02, 0.97, 1.03, 0.96, 1.04, 0.95, 1.05, 0.94, 1.06]


def fit_score(z, fills):
    """Lower is better: penalise near-empty last pages and large mid-chapter gaps; prefer zoom close to 1.0."""
    body, last = fills[:-1], fills[-1]
    return sum(max(0.0, 0.84 - f) for f in body) + 1.5 * max(0.0, 0.60 - last) + 0.6 * abs(z - 1.0)


def fit_unit(unit_html, css, fonts, tmp, tag):
    """Choose the zoom (within a few percent of 1.0) that gives the cleanest pagination for this chapter."""
    best = None
    for z in Z_ORDER:
        n, fills = render_unit(unit_html, z, css, fonts, tmp, "%s_%d" % (tag, int(z * 100)))
        sc = fit_score(z, fills)
        if best is None or sc < best[0]:
            best = (sc, z, n, fills[-1])
    return best[1], best[2], best[3]


def fit_all(units, css, fonts, name):
    import hashlib, json, tempfile
    from concurrent.futures import ThreadPoolExecutor
    cache_path = os.path.join(PRINT, "fit-%s.json" % name)
    cache = json.load(open(cache_path)) if os.path.exists(cache_path) else {}
    key = lambda u: hashlib.md5((css + u).encode()).hexdigest()
    todo = [(i, u) for i, u in enumerate(units) if key(u) not in cache]
    if todo:
        tmp = tempfile.mkdtemp(prefix="fit_")
        with ThreadPoolExecutor(max_workers=4) as ex:
            res = list(ex.map(lambda iu: (iu[0], fit_unit(iu[1], css, fonts, tmp, "c%d" % iu[0])), todo))
        for i, (z, n, fill) in res:
            cache[key(units[i])] = {"z": z, "pages": n, "fill": round(fill, 2)}
        json.dump(cache, open(cache_path, "w"), indent=1)
    return [cache[key(u)]["z"] for u in units], [cache[key(u)] for u in units]


def build(which, fit=True):
    cfg = DOCS[which]
    files = sorted(os.path.join(cfg["chapters"], f) for f in os.listdir(cfg["chapters"]) if f.endswith(".md") and not f.startswith("_"))
    css = open(os.path.join(PRINT, "style.css")).read().replace("__RUNNING__", cfg["running"]).replace("__BASE__", cfg["base"])
    fonts = open(os.path.join(PRINT, "fonts", "fonts.css")).read().replace("url(fonts/", "url(file://" + PRINT + "/fonts/")
    units, toc = build_body(files, cfg)
    zs = [1.0] * len(units)
    if fit:
        zs, info = fit_all(units, css, fonts, which)
        print("fit: zoom range %.2f-%.2f" % (min(zs), max(zs)))
    body = "\n".join('<div class="unit" style="zoom:%.3f">%s</div>' % (z, u) for z, u in zip(zs, units))
    tmp = os.path.join(PRINT, which + ".html")
    pdf = os.path.join(PRINT, cfg["pdf"])
    cover = cover_html(cfg)
    title = "%s — SWE Excellence" % cfg["title"].title()
    write_doc(tmp, css, fonts, cover + toc_html(toc, None) + body, title)
    chrome_pdf(tmp, pdf)
    pages, npages = page_map(pdf, toc)
    for _ in range(2):
        write_doc(tmp, css, fonts, cover + toc_html(toc, pages) + body, title)
        chrome_pdf(tmp, pdf)
        pages2, npages = page_map(pdf, toc)
        if pages2 == pages:
            break
        pages = pages2
    missing = [t[2] for t in toc if t[0] == "chapter" and t[3] not in pages]
    print("%s: %d pages -> %s" % (which, npages, pdf))
    if missing:
        print("  (TOC could not locate: %s)" % missing)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    fit = "--nofit" not in sys.argv
    for w in (DOCS if what == "all" else [what]):
        if os.path.isdir(DOCS[w]["chapters"]) and any(f.endswith(".md") for f in os.listdir(DOCS[w]["chapters"])):
            build(w, fit)
