import glob, json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
for f in glob.glob(r".\archive\wiki\raw\fandom\revisions\0\*.json"):
    d = json.load(open(f, encoding="utf-8"))
    if d.get("title") == "Tutorial/Getting Started With the Game's Unity Files and Assets":
        t = d["revisions"][0]["slots"]["main"]["content"]
        print("FILE", f)
        print("REVID", d["revisions"][0].get("revid"), "TS", d["revisions"][0].get("timestamp"))
        print("LEN", len(t))
        print(t[:12000])
        break
else:
    print("not found")
