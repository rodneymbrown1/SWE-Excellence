#!/usr/bin/env python3
"""Build STATE FIRST (book + field cards) -> HTML -> PDF with headless Chrome.

usage:  python3 print/build.py            # book + cards
        python3 print/build.py book       # only the book
        python3 print/build.py cards      # only the cards
Needs: pandoc, Google Chrome, pdftotext (for TOC page numbers).  Fonts are local (print/fonts).
"""
import html, json, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRINT = os.path.join(ROOT, "print")
CHAPTERS = os.path.join(ROOT, "chapters")
DIAGRAMS = os.path.join(ROOT, "diagrams")
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
PANDOC_FMT = "markdown+fenced_divs+pipe_tables+bracketed_spans+backtick_code_blocks+raw_html+smart+header_attributes"


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def pandoc(md_text):
    p = subprocess.run(["pandoc", "-f", PANDOC_FMT, "-t", "html5", "--no-highlight", "--wrap=none"],
                       input=md_text, capture_output=True, text=True, check=True)
    return p.stdout


def inline_svgs(h):
    def sub(m):
        name = m.group(1)
        path = os.path.join(DIAGRAMS, name + ".svg")
        if not os.path.exists(path):
            return "<p><b>[missing diagram %s]</b></p>" % name
        svg = open(path).read()
        svg = re.sub(r"<\?xml.*?\?>", "", svg).strip()
        return svg
    return re.sub(r"(?:<p>)?\{\{svg:([\w\-]+)\}\}(?:</p>)?", sub, h)


def mark_out_blocks(h):
    # <pre class="out"> for fenced blocks tagged ```out
    return h.replace('<pre class="out">', '<pre class="out">')


def mark_long_tables(h):
    def f(m):
        t = m.group(0)
        return t.replace("<table>", '<table class="long">', 1) if t.count("<tr") > 5 else t
    return re.sub(r"<table>.*?</table>", f, h, flags=re.S)


def build_html(chapter_files, title, front="", toc_entries=None, page_numbers=None):
    css = open(os.path.join(PRINT, "style.css")).read()
    fonts = open(os.path.join(PRINT, "fonts", "fonts.css")).read()
    body = []
    n = 0
    appx = 0
    toc = []
    for cf in chapter_files:
        md = open(cf).read()
        h = pandoc(md)
        h = inline_svgs(h)
        h = mark_long_tables(h)

        def number_h1(m):
            nonlocal n, appx
            attrs, text = m.group(1), m.group(2)
            cls = re.search(r'class="([^"]*)"', attrs)
            cls = cls.group(1) if cls else ""
            cid = re.search(r'id="([^"]*)"', attrs).group(1)
            plain = re.sub(r"<[^>]+>", "", text)
            if "chapter" in cls.split():
                n += 1
                toc.append(("chapter", str(n), plain, cid))
                return '<h1 id="%s" class="%s" data-label="Chapter %d">%s</h1>' % (cid, cls, n, text)
            if "appendix" in cls.split():
                letter = chr(ord("A") + appx)
                appx += 1
                toc.append(("chapter", letter, plain, cid))
                return '<h1 id="%s" class="%s" data-label="Appendix %s">%s</h1>' % (cid, cls, letter, text)
            toc.append(("chapter", "", plain, cid))
            return "<h1%s>%s</h1>" % (attrs, text)

        def part_or_h1(m):
            if m.group(1):  # a part-title section
                title = re.search(r'<div class="ph">(.*?)</div>', m.group(1), re.S)
                pn = re.search(r'<p class="pn">(.*?)</p>', m.group(1), re.S)
                toc.append(("part", "", (pn.group(1) + " \u2014 " if pn else "") + re.sub(r"<[^>]+>", "", title.group(1)), ""))
                return m.group(1)
            class _M:  # adapt to number_h1's (attrs, text) interface
                def __init__(self, a, t): self._a, self._t = a, t
                def group(self, i): return self._a if i == 1 else self._t
            return number_h1(_M(m.group(2), m.group(3)))

        h = re.sub(r'(<section class="part-title">.*?</section>)|<h1([^>]*)>(.*?)</h1>', part_or_h1, h, flags=re.S)
        body.append(h)
    return css, fonts, "\n".join(body), toc


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


def chrome_pdf(html_path, pdf_path):
    run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
         "--virtual-time-budget=20000", "--print-to-pdf=" + pdf_path, "file://" + html_path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def page_map(pdf_path, toc):
    """Find the PDF page where each chapter heading starts (for TOC numbers)."""
    npages = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf_path], capture_output=True, text=True).stdout).group(1))
    texts = []
    for p in range(1, npages + 1):
        t = subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), "-layout", pdf_path, "-"], capture_output=True, text=True).stdout
        texts.append(re.sub(r"\s+", " ", t))
    pages = {}
    start = 3  # skip cover + contents
    for kind, num, text, cid in toc:
        if kind != "chapter":
            continue
        key = re.sub(r"\s+", " ", text).strip()
        for i in range(start - 1, npages):
            head = texts[i][:400]
            if key[:40] in head:
                pages[cid] = i + 1
                start = i + 1
                break
    return pages, npages


def write_doc(path, css, fonts, inner, title):
    doc = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>%s</title>'
           '<meta name="viewport" content="width=device-width,initial-scale=1"><style>%s\n%s</style></head><body>%s</body></html>'
           % (html.escape(title), fonts, css, inner))
    open(path, "w").write(doc)


def build_book():
    files = sorted(os.path.join(CHAPTERS, f) for f in os.listdir(CHAPTERS) if f.endswith(".md") and not f.startswith("_"))
    cover = open(os.path.join(PRINT, "cover.html")).read()
    css, fonts, body, toc = build_html(files, "STATE FIRST")
    tmp_html = os.path.join(PRINT, "state-first-book.html")
    pdf = os.path.join(PRINT, "state-first-book.pdf")
    # pass 1 (no page numbers)
    write_doc(tmp_html, css, fonts, cover + toc_html(toc, None) + body, "STATE FIRST")
    chrome_pdf(tmp_html, pdf)
    pages, npages = page_map(pdf, toc)
    # pass 2 (with page numbers); TOC length is unchanged so numbers stay valid
    write_doc(tmp_html, css, fonts, cover + toc_html(toc, pages) + body, "STATE FIRST")
    chrome_pdf(tmp_html, pdf)
    pages2, npages2 = page_map(pdf, toc)
    if pages2 != pages:
        write_doc(tmp_html, css, fonts, cover + toc_html(toc, pages2) + body, "STATE FIRST")
        chrome_pdf(tmp_html, pdf)
        pages2, npages2 = page_map(pdf, toc)
    missing = [t[2] for t in toc if t[0] == "chapter" and t[3] not in pages2]
    print("book: %d pages -> %s" % (npages2, pdf))
    if missing:
        print("  (TOC could not locate:", missing, ")")


def build_cards():
    css = open(os.path.join(PRINT, "style.css")).read()
    fonts = open(os.path.join(PRINT, "fonts", "fonts.css")).read()
    md = open(os.path.join(ROOT, "cards", "cards.md")).read()
    h = mark_long_tables(inline_svgs(pandoc(md)))
    tmp_html = os.path.join(PRINT, "state-first-cards.html")
    pdf = os.path.join(PRINT, "state-first-field-cards.pdf")
    write_doc(tmp_html, css, fonts, h, "STATE FIRST — Field Cards")
    chrome_pdf(tmp_html, pdf)
    npages = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout).group(1))
    print("cards: %d pages -> %s" % (npages, pdf))


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("all", "book"):
        build_book()
    if what in ("all", "cards"):
        if os.path.exists(os.path.join(ROOT, "cards", "cards.md")):
            build_cards()
