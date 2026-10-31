import json, os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"."
W = os.path.join(ROOT, "archive", "wiki")
state = json.load(open(os.path.join(W, "state.json"), encoding="utf-8"))
bots = json.load(open(os.path.join(ROOT, "data", "wiki", "bots.json"), encoding="utf-8"))["bots"]
pages = json.load(open(os.path.join(ROOT, "data", "wiki", "pages.json"), encoding="utf-8"))["pages"]
parsed = set(bots) | set(pages)
rows = []
for key, v in sorted(state["pages"].items()):
    wiki, title = key.split("|", 1)
    if wiki == "fandom" and title in parsed:
        continue
    if wiki == "fandom" and v.get("ns") == 0:
        reason = "content page not in data/wiki (see data/wiki/unparsed)"
    elif wiki == "fandom" and v.get("ns") == 6:
        reason = "File description archived; not game-data parsed"
    else:
        reason = "metadata/reference page, not game-data target"
    rows.append({"wiki": wiki, "title": title, "ns": v.get("ns"), "reason": reason})
out = os.path.join(W, "unparsed")
os.makedirs(out, exist_ok=True)
json.dump({"note": "Saved pages not represented in data/wiki; raw remains authoritative.",
           "parsed_pages": len(parsed), "items": rows},
          open(os.path.join(out, "pages.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("unparsed", len(rows), "parsed", len(parsed))
