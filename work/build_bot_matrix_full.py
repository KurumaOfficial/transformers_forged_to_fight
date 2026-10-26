"""3.1 three-list bot matrix: bio keys, client packs, wiki pages, quest roles."""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "server" / "data"
CAT = json.loads((DATA / "bot_catalog_real.json").read_text(encoding="utf-8"))["rows"]
BOTS = json.loads((ROOT / "data" / "wiki" / "bots.json").read_text(encoding="utf-8"))["bots"]
IDMAP = json.loads((ROOT / "data" / "wiki" / "id_map.json").read_text(encoding="utf-8"))
LOC = json.loads((ROOT / "work" / "localization_all.json").read_text(encoding="utf-8"))
BOSSMAP = json.loads((ROOT / "data" / "boss_map.json").read_text(encoding="utf-8"))
OUT = ROOT / "data" / "wiki" / "bot_matrix_full.json"

bio_keys = {k: v for k, v in LOC.items() if k.startswith("ID_CHARACTER_BIOS_")}
# Normalize a localization suffix such as BUMBLE_GS / BUMBL_GS.
def norm_key(s):
    return re.sub(r"[^A-Z0-9]", "", s.upper())


wiki_to_client = {}
for row in CAT:
    page = row.get("wiki_page")
    if page:
        wiki_to_client.setdefault(page, row["client_id"])
for m in IDMAP.get("matched", []):
    if m.get("wiki_page") and m.get("client_id"):
        wiki_to_client.setdefault(m["wiki_page"], m["client_id"])

# Best-effort bio match: wiki page/name tokens against the suffix.
def find_bio(row):
    name = (row.get("wiki_page") or row.get("name") or row["client_id"]).upper()
    tokens = [t for t in re.split(r"[^A-Z0-9]+", name) if t]
    cands = []
    for k in bio_keys:
        suffix = k[len("ID_CHARACTER_BIOS_"):]
        ns = norm_key(suffix)
        if tokens and norm_key(tokens[0])[:4] and norm_key(tokens[0])[:4] in ns:
            cands.append(k)
    return sorted(cands)

boss_counts = Counter()
boss_quests = defaultdict(list)
for qid, row in BOSSMAP.items():
    bid = row.get("boss_client_id")
    if bid:
        boss_counts[bid] += 1
        boss_quests[bid].append(qid)

rows = []
for row in CAT:
    cid = row["client_id"]
    page = row.get("wiki_page")
    b = BOTS.get(page) or {}
    bios = find_bio(row)
    has_stats = bool(b.get("stat_tables") or b.get("stars"))
    has_rank = bool(b.get("stat_tables"))
    has_abil = bool(b.get("abilities"))
    rows.append({
        "client_id": cid,
        "wiki_page": page,
        "has_client_pack": True,
        "has_wiki_page": bool(page and page in BOTS),
        "has_stats": has_stats,
        "has_rank_table": has_rank,
        "has_abilities": has_abil,
        "bio_keys": bios,
        "has_bio": bool(bios),
        "boss_count": boss_counts.get(cid, 0),
        "boss_quests": boss_quests.get(cid, []),
        "class": row.get("class"),
    })

wiki_pages = set(BOTS)
client_pages = {r["wiki_page"] for r in rows if r.get("wiki_page")}
unmapped_wiki = sorted(wiki_pages - client_pages)
bio_unused = sorted(set(bio_keys) - {k for r in rows for k in r["bio_keys"]})
client_without_page = [r["client_id"] for r in rows if not r["has_wiki_page"]]
client_without_stats = [r["client_id"] for r in rows if not r["has_stats"]]

out = {
    "source": "bot_catalog_real.json + bots.json + localization_all.json + boss_map.json",
    "client_bots": len(rows),
    "wiki_pages_with_stats": len(wiki_pages),
    "bio_keys": len(bio_keys),
    "unmapped_wiki_pages": unmapped_wiki,
    "unmatched_bio_keys": bio_unused,
    "client_without_wiki_page": client_without_page,
    "client_without_stats": client_without_stats,
    "rows": rows,
}
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("client", len(rows), "wiki", len(wiki_pages), "bios", len(bio_keys))
print("without wiki page", len(client_without_page), client_without_page)
print("without stats", len(client_without_stats))
print("unmapped wiki", len(unmapped_wiki), unmapped_wiki)
print("unmatched bios", len(bio_unused), bio_unused[:20])
print("boss coverage", sum(1 for r in rows if r["boss_count"]), "bots as bosses")
