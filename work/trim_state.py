import json
p = r".\archive\wiki\state.json"
s = json.load(open(p, encoding="utf-8"))
for k in ["allredirects_tfwiki", "allcategories_tfwiki", "allimages_tfwiki"]:
    v = s.get("lists", {}).get(k)
    if v:
        n = len(v.get("items", []))
        s["lists"][k] = {"items": [], "continue": None,
                         "count": n,
                         "note": "full list kept in meta/*.json; trimmed from git state"}
json.dump(s, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("trimmed")
