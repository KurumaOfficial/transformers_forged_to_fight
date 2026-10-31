import json, os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"."
p = os.path.join(ROOT, "data", "wiki", "bots.json")
d = json.load(open(p, encoding="utf-8"))
bots = d["bots"]
fields = {
    "star_health_attack": lambda b: bool(b.get("stars")),
    "rank_level_table": lambda b: any(
        any("rank" in (c or "").lower() or "level" in (c or "").lower() for c in (t[0] if t else []))
        for t in b.get("stat_tables", [])
    ),
    "level_values": lambda b: any(
        len(t) > 1 and any("level" in (c or "").lower() for c in (t[0] if t else []))
        for t in b.get("stat_tables", [])
    ),
    "abilities": lambda b: bool(b.get("abilities", {}).get("pairs") or b.get("abilities", {}).get("list")),
    "ability_rank_table": lambda b: bool(b.get("abilities", {}).get("tables")),
    "signature": lambda b: bool(b.get("signature", {}).get("name") or b.get("signature", {}).get("tables")),
    "signature_table": lambda b: bool(b.get("signature", {}).get("tables")),
    "special_attacks": lambda b: bool(b.get("special_attack_pairs") or b.get("special_attacks")),
    "synergy": lambda b: bool(b.get("synergy")),
}
rows = []
counts = {k: 0 for k in fields}
missing = {k: [] for k in fields}
for title, b in sorted(bots.items()):
    row = {"bot": title, "revid": b.get("source", {}).get("revid")}
    for k, fn in fields.items():
        v = bool(fn(b))
        row[k] = v
        if v:
            counts[k] += 1
        else:
            missing[k].append(title)
    rows.append(row)
out = {
    "source": "data/wiki/bots.json",
    "total_bots": len(rows),
    "counts": counts,
    "rows": rows,
    "missing": missing,
    "note": "A field is true only if the saved wikitext had a non-empty value; missing cells were not invented.",
}
json.dump(out, open(os.path.join(ROOT, "data", "wiki", "bot_matrix.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({"total": len(rows), "counts": counts}, ensure_ascii=False, indent=1))
for k in fields:
    print(k, "missing", len(missing[k]), missing[k][:12])
