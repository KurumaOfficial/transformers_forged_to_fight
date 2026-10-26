"""Add an explicit Starscream fallback without pretending it is the original."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOSSMAP = ROOT / "data" / "boss_map.json"
GAPS = ROOT / "data" / "boss_gaps.json"
QL = ROOT / "server" / "data" / "quest_list.json"
FALLBACK = "nemesisprime_gs_voyager2015"  # Decepticon Tactician, 9.2.0 pack
REASON = ("[ASSUMED] Starscream has no 9.2.0 client pack; same-faction/"
          "same-class Tactician fallback for data experiments only; not the original boss")

bm = json.loads(BOSSMAP.read_text(encoding="utf-8"))
changed = 0
for qid, row in bm.items():
    if row.get("boss") == "Starscream" and not row.get("boss_client_id"):
        row["fallback_client_id"] = FALLBACK
        row["fallback_label"] = "[ASSUMED] not original"
        row["fallback_reason"] = REASON
        changed += 1
BOSSMAP.write_text(json.dumps(bm, ensure_ascii=False, indent=1), encoding="utf-8")

sets = json.loads(QL.read_text(encoding="utf-8"))
patched = 0
for qs in sets:
    for q in qs.get("availableQuests", []):
        qid = q.get("id")
        row = bm.get(qid) or {}
        if row.get("boss") == "Starscream" and not row.get("boss_client_id"):
            q["bossFallback"] = {"id": FALLBACK, "label": "[ASSUMED] not original"}
            patched += 1
QL.write_text(json.dumps(sets, ensure_ascii=False, indent=1), encoding="utf-8")

gaps = json.loads(GAPS.read_text(encoding="utf-8"))
for g in gaps:
    row = bm.get(g["qid"]) or {}
    if row.get("fallback_client_id"):
        g["fallback_client_id"] = row["fallback_client_id"]
        g["fallback_label"] = "[ASSUMED] not original"
GAPS.write_text(json.dumps(gaps, ensure_ascii=False, indent=1), encoding="utf-8")
print("fallback entries", changed, "quest_list", patched)
