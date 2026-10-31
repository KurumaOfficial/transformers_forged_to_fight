import json
p = r".\archive\wiki\meta\author_collection.json"
d = json.load(open(p, encoding="utf-8"))
d["evidence"] = "external link on User:KRBrickBot; the main page links to the Tutorial page, which links to this user page"
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok")
