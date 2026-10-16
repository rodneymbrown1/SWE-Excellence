#!/bin/sh
# Rebuild fire-handbook-hp.pdf from fire-handbook-hp.html using headless Chrome (needs network once for Google Fonts).
# usage: ./build-pdf.sh
set -e
cd "$(dirname "$0")"
TMP="$(mktemp -d)"
{ printf '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>'
  cat fire-handbook-hp.html
  printf '</body></html>'; } > "$TMP/index.html"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
"$CHROME" --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=15000 \
  --print-to-pdf="$PWD/fire-handbook-hp.pdf" "file://$TMP/index.html" 2>/dev/null
rm -rf "$TMP"
echo "wrote $PWD/fire-handbook-hp.pdf"
