import json, glob, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
fs = glob.glob(r".\archive\wiki\raw\fandom\revisions\0\*.json")
n = 0
names = []
for f in fs:
    d = json.load(open(f, encoding="utf-8"))
    c = d["revisions"][0]["slots"]["main"]["content"]
    if "Infobox_character" in c and ("==Stats==" in c or "==Max Stats==" in c):
        n += 1
        names.append(d["title"])
print(n)
print(names)
