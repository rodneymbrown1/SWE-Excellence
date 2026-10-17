import sys, urllib.request
url, out = sys.argv[1], sys.argv[2]
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research fetch)"})
with urllib.request.urlopen(req, timeout=30) as r, open(out, "wb") as f:
    f.write(r.read())
