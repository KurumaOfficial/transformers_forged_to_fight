import json
from pathlib import Path
root = Path(r".")
idm = json.loads((root / "data/wiki/id_map.json").read_text(encoding="utf-8"))
bots = json.loads((root / "data/wiki/bots.json").read_text(encoding="utf-8"))["bots"]
pages = json.loads((root / "data/wiki/pages.json").read_text(encoding="utf-8"))["pages"]
matched = {r["client_id"]: r for r in idm.get("matched", [])}
rows = []
for cid, r in sorted(matched.items()):
    page = r.get("wiki_page")
    prec = pages.get(page) if page else None
    bot = bots.get(page) if page else None
    if bot is None and page:
        bot = bots.get(page.split(" (")[0])
    inf = (prec or {}).get("infobox") or (bot or {}).get("infobox", {})
    stars = (bot or {}).get("stars", {})
    shark = cid.startswith("sharkticon_")
    missing = []
    if not prec:
        missing.append("no parsed wiki page")
    for f in ("Class", "Faction", "Origin"):
        if not inf.get(f):
            missing.append(f"no wiki {f}")
    rows.append({
        "client_id": cid,
        "pack_dir": f"work/unpacked/assets/{cid}_odr",
        "wiki_page": page,
        "wiki_page_exists": r.get("wiki_page_exists"),
        "in_bots_stats": r.get("in_bots_stats"),
        "sharkticon_variant": shark,
        "class": inf.get("Class", ""),
        "faction": inf.get("Faction", ""),
        "generation": inf.get("Origin", ""),
        "release": inf.get("Release Date", ""),
        "stars": stars,
        "max_rating": {k: v.get("max_rating") for k, v in stars.items() if v.get("max_rating")},
        "sources": {
            "client_id": "[CLIENT]",
            "class_faction_generation": "[WIKI]" if inf else "",
            "stars": "[WIKI]" if stars else "",
        },
        "missing": missing,
    })
out = {
    "source": "client package dirs (9.2.0) + data/wiki/id_map.json + data/wiki/bots.json + data/wiki/pages.json",
    "note": "No fabricated class/faction/generation; empty strings + missing reasons where wiki data is absent. Sharkticon variant names are client IDs; class mapping is not asserted.",
    "count": len(rows),
    "rows": rows,
}
(root / "server/data/bot_catalog_real.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("rows", len(rows), "with_class", sum(bool(r["class"]) for r in rows), "with_stars", sum(bool(r["stars"]) for r in rows), "missing_page", sum(not r["wiki_page_exists"] for r in rows))
