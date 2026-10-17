#!/usr/bin/env python3
"""Layout QA for the printed PDFs: finds pages with large blank areas and measures how full each chapter's last page is.

    python3 print/qa.py print/on-time-book.pdf

Reports (page numbers are PDF page numbers):
  GAP    a page that is not the last of its chapter but whose content stops before ~82% of the text area
  SHORT  the last page of a chapter that is less than 35% full
  A table of per-chapter page counts and last-page fill.
Also checks PDF accessibility basics via pdfinfo (tagged, title, page size).
"""
import re, subprocess, sys, tempfile, os
from PIL import Image

pdf = sys.argv[1]
DPI = 50
info = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
npages = int(re.search(r"Pages:\s+(\d+)", info).group(1))
print("pdfinfo:", ", ".join(l.strip() for l in info.splitlines() if l.split(":")[0] in ("Title", "Tagged", "Page size", "Pages", "Form")))
tmp = tempfile.mkdtemp()
subprocess.run(["pdftoppm", "-r", str(DPI), "-gray", "-png", pdf, os.path.join(tmp, "p")], check=True)
files = sorted(f for f in os.listdir(tmp) if f.endswith(".png"))
top, bottom = int(0.75 * DPI), int(10.1 * DPI)
fill, starts = {}, {}
for i, fn in enumerate(files, start=1):
    im = Image.open(os.path.join(tmp, fn)).convert("L")
    w, h = im.size
    px = im.load()
    last = top
    for y in range(min(bottom, h) - 1, top, -1):
        if any(px[x, y] < 200 for x in range(int(0.6 * DPI), w - int(0.6 * DPI))):
            last = y
            break
    fill[i] = max(0.0, min(1.0, (last - top) / float(bottom - top)))
for p in range(1, npages + 1):
    t = subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), "-layout", pdf, "-"], capture_output=True, text=True).stdout
    head = re.sub(r"\s+", "", t)[:120].upper()           # letter-spaced headings extract as "C H A P T E R": drop all spaces
    m = re.match(r"^(?:(?:PART[^·]*·[^·]*|APPENDICES)·)?(CHAPTER\d+|SECTION\d+|LAB[A-Z]?\d+|APPENDIX[A-Z])", head)
    if m and p > 2:
        starts[p] = m.group(1).upper()
order = sorted(starts)
print("\nchapter starts found:", len(order))
issues = 0
print("\n%-14s %6s %6s  %s" % ("unit", "first", "pages", "last-page fill"))
for k, s in enumerate(order):
    end = (order[k + 1] - 1) if k + 1 < len(order) else npages
    n = end - s + 1
    lf = fill[end]
    flag = "SHORT" if (lf < 0.35 and n > 0) else ""
    print("%-14s %6d %6d  %3d%%  %s" % (starts[s], s, n, lf * 100, flag))
    issues += bool(flag)
    for p in range(s, end):
        if fill[p] < 0.82:
            print("   GAP  page %d is only %d%% full (not the end of the unit)" % (p, fill[p] * 100))
            issues += 1
print("\n%d layout issues" % issues)
