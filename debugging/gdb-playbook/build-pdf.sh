#!/bin/sh
# Rebuild gdb-playbook.pdf (US Letter, 0.6in margins) with headless Chrome. Needs network once for Google Fonts.
set -e
cd "$(dirname "$0")"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
"$CHROME" --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=15000 \
  --print-to-pdf="$PWD/gdb-playbook.pdf" "file://$PWD/gdb-playbook-print.html" 2>/dev/null
echo "wrote $PWD/gdb-playbook.pdf"
