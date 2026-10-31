import glob, json, re, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
c = Counter()
for f in glob.glob(r".\archive\wiki\raw\fandom\revisions\0\*.json"):
    try:
        d = json.load(open(f, encoding="utf-8"))
        t = d["revisions"][0]["slots"]["main"]["content"]
    except Exception:
        continue
    for m in re.finditer(r"(?im)^(={2,4})\s*([^=\n]*synerg[^=\n]*)\s*\1\s*$", t):
        c[m.group(2).strip()] += 1
for k, v in c.most_common():
    print(v, repr(k))
