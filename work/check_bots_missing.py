import json, glob
b = json.load(open(r".\data\wiki\bots.json", encoding="utf-8"))["bots"]
titles = []
for f in glob.glob(r".\archive\wiki\raw\fandom\revisions\0\*.json"):
    d = json.load(open(f, encoding="utf-8"))
    c = d["revisions"][0]["slots"]["main"]["content"]
    if "Infobox_character" in c and ("==Stats==" in c or "==Max Stats==" in c):
        titles.append(d["title"])
print("missing", [t for t in titles if t not in b])
print("bots", len(b), "candidates", len(titles))
