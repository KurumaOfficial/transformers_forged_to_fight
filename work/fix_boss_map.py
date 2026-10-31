"""Resolve missing boss ids from id_map and rebuild boss_map.json."""
import json
import re
from pathlib import Path

ROOT = Path(r".")
REAL = ROOT / "data" / "quests_real.json"
IDMAP = ROOT / "data" / "wiki" / "id_map.json"
OUT = ROOT / "data" / "boss_map.json"
GAPS = ROOT / "data" / "boss_gaps.json"
QL = ROOT / "server" / "data" / "quest_list.json"


def roman(v, default=1):
    s = str(v).strip().upper()
    table = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6}
    if s in table:
        return table[s]
    try:
        return int(s)
    except Exception:
        return default


def norm(s):
    s = s or ""
    for prefix in ("Revenge of the Fallen ", "Dark of the Moon ", "Tech ", "Fall of Cybertron "):
        if s.startswith(prefix):
            s = s[len(prefix):]
    return s.strip()


idmap = json.loads(IDMAP.read_text(encoding="utf-8")).get("matched", [])
by_page = {m["wiki_page"]: m for m in idmap if m.get("confidence", "").startswith("high")}


def resolve(name):
    if not name:
        return None, "no boss name on wiki"
    n = norm(name)
    for page, m in by_page.items():
        if page == n or page.startswith(n + " (") or n.startswith(page):
            return m["client_id"], f"id_map match: {page} ({m['confidence']})"
    low = n.lower()
    for page, m in by_page.items():
        if low in page.lower() or page.lower() in low:
            return m["client_id"], f"id_map fuzzy: {page} ({m['confidence']})"
    if "starscream" in low:
        return None, "Starscream has no 9.2.0 client pack (wiki-only variants)"
    return None, "no high-confidence client id"


real = json.loads(REAL.read_text(encoding="utf-8"))["latest"]
out = {}
gaps = []
def add(act, chapters, prefix):
    for ch in chapters:
        c = roman(ch.get("chapter", 1))
        for n, m in enumerate(ch.get("missions", []), 1):
            idx = int(m.get("index", n))
            qid = prefix.format(act=act, ch=c, m=idx)
            name = m.get("name") or ""
            boss = m.get("boss")
            cid = m.get("boss_client_id")
            reason = "wiki high-confidence id" if cid else ""
            if not cid:
                cid, reason = resolve(boss)
            out[qid] = {"name": name, "boss": boss, "boss_client_id": cid,
                        "match": m.get("boss_match"), "reason": reason}
            if not cid:
                gaps.append(out[qid] | {"qid": qid})

for a in real["story_acts"]:
    add(a["act"], a.get("chapters", []), "story_act" + str(a["act"]) + "_ch{ch}_m{m}")
aw = real["other_act_pages"].get("Awaken and Corrupt", {})
add(1, aw.get("chapters", []), "awaken_ch{ch}_m{m}")

OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
GAPS.write_text(json.dumps(gaps, ensure_ascii=False, indent=1), encoding="utf-8")

# patch quest_list finalBoss where it is null and boss_map has an id
if QL.exists():
    sets = json.loads(QL.read_text(encoding="utf-8"))
    patched = 0
    for s in sets:
        for q in s.get("availableQuests", []):
            if not q.get("finalBoss"):
                b = out.get(q["id"], {})
                if b.get("boss_client_id"):
                    q["finalBoss"] = {"id": b["boss_client_id"], "level": 1, "rank": 1}
                    patched += 1
    QL.write_text(json.dumps(sets, ensure_ascii=False, indent=1), encoding="utf-8")
    print("patched quest_list", patched)

print("boss entries", len(out), "with id", sum(1 for v in out.values() if v["boss_client_id"]),
      "gaps", len(gaps))
for g in gaps:
    print(g["qid"], g["boss"], g["reason"])
