import glob, json, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
for f in glob.glob(r".\archive\wiki\raw\fandom\revisions\0\*.json"):
    try:
        d = json.load(open(f, encoding="utf-8"))
        t = d["revisions"][0]["slots"]["main"]["content"]
    except Exception:
        continue
    m = re.search(r"(?im)^(={2,4})\s*([^=\n]*synerg[^=\n]*)\s*\1\s*$", t)
    if m:
        i = m.start()
        print("PAGE", d.get("title"), "HEADING", repr(m.group(0)))
        print(t[i:i+500].replace("\n", " | ")[:500])
        break
