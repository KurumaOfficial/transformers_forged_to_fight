import json
from pathlib import Path
root = Path(r".")
idm = json.loads((root / "data/wiki/id_map.json").read_text(encoding="utf-8"))
matched = idm.get("matched", [])
client_without = []
shark = []
for row in matched:
    cid = row.get("client_id", "")
    if cid.startswith("sharkticon_"):
        shark.append(row)
    elif not row.get("in_bots_stats") or not row.get("wiki_page_exists", True):
        client_without.append(row)
wiki_only = idm.get("wiki_without_client", [])
out = {
    "source": "data/wiki/id_map.json + work/unpacked/assets (client 9.2.0); no invented stats",
    "client_only": [
        {
            "client_id": r["client_id"],
            "wiki_page": r.get("wiki_page"),
            "wiki_page_exists": r.get("wiki_page_exists", False),
            "pack_dir": f"work/unpacked/assets/{r['client_id']}_odr",
            "known_from_client": ["id from prefab/package directory"],
            "known_from_wiki": [],
            "missing_reason": "no stat page in the saved Fandom set" if not r.get("in_bots_stats") else "page exists but no parsed stat table",
            "tag": "[CLIENT]+[WIKI]",
        }
        for r in client_without
    ],
    "sharkticon_variants": [
        {
            "client_id": r["client_id"],
            "pack_dir": f"work/unpacked/assets/{r['client_id']}_odr",
            "known_from_client": ["variant package"],
            "known_from_wiki": [],
            "missing_reason": "no separate Sharkticon stat page in saved Fandom set",
            "tag": "[CLIENT]",
        }
        for r in shark
    ],
    "wiki_without_client": [
        {
            "wiki_page": p,
            "possible_status": "post-9.2.0 or variant not present as a separate pack",
            "client_match": None,
            "tag": "[WIKI]+[ASSUMED]",
        }
        for p in wiki_only
    ],
    "counts": {
        "client_only_non_shark": len(client_without),
        "sharkticon_variants": len(shark),
        "wiki_without_client": len(wiki_only),
    },
}
(root / "data/wiki/client_only.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(out["counts"], ensure_ascii=False))
print("client_only", [r["client_id"] for r in out["client_only"]])
print("wiki_only", wiki_only)
