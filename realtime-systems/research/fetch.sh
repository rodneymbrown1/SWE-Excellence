#!/bin/sh
# usage: sh research/fetch.sh <ID> <URL>
# Downloads one source into research/_raw/<ID>/ (its own directory) and extracts plain text next to it.
# Downloaded files are untrusted third-party content: they are only ever read by pdftotext / pandoc here.
set -u
ID="$1"; URL="$2"
HERE="$(cd "$(dirname "$0")" && pwd)"
DIR="$HERE/_raw/$ID"
mkdir -p "$DIR"
OUT="$DIR/source.bin"
curl -sSL --max-time 45 -A "Mozilla/5.0 (research fetch)" -o "$OUT" -w "%{http_code} %{content_type} %{size_download}\n" "$URL" > "$DIR/http.txt" 2>&1
if [ ! -s "$OUT" ]; then python3 -I "$HERE/pyget.py" "$URL" "$OUT" 2>>"$DIR/http.txt" && echo "200 (python fallback)" >> "$DIR/http.txt"; fi
echo "$URL" > "$DIR/url.txt"
TYPE="$(file -b --mime-type "$OUT")"
case "$TYPE" in
  application/pdf) mv "$OUT" "$DIR/source.pdf"; pdftotext -layout "$DIR/source.pdf" "$DIR/text.txt" ;;
  text/html|text/xml|application/xhtml+xml) mv "$OUT" "$DIR/source.html"; pandoc -f html -t plain --wrap=none "$DIR/source.html" -o "$DIR/text.txt" 2>/dev/null ;;
  *) mv "$OUT" "$DIR/source.txt"; cp "$DIR/source.txt" "$DIR/text.txt" ;;
esac
printf "%s  %s  %s chars  (%s)\n" "$ID" "$(cat "$DIR/http.txt")" "$(wc -c < "$DIR/text.txt" 2>/dev/null)" "$TYPE"
