"""Fill the 12 Act 4 chapter I/II boss names from the wiki revision (3.3)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "server" / "data"
BOSSES = {
    "story_act4_ch1_m1": ("Bonecrusher", "bonecrusher_cin_rotf"),
    "story_act4_ch1_m2": ("Jetfire", "jetfire_gs_leader2014"),
    "story_act4_ch1_m3": ("Bumblebee (DOTM)", "bumblebee_cin_dotm_2"),
    "story_act4_ch1_m4": ("Blaster", "blaster_gs_leader2016"),
    "story_act4_ch1_m5": ("Shockwave", "shockwave_gs"),
    "story_act4_ch1_m6": ("Megatronus", "megatronus_gs_kabam"),
    "story_act4_ch2_m1": ("Cheetor", "cheetor_bw_transmetal"),
    "story_act4_ch2_m2": ("Soundwave", "soundwave_gs"),
    "story_act4_ch2_m3": ("Megatron", "megatron_gs_leader2015"),
    "story_act4_ch2_m4": ("Thundercracker", "thundercracker_gs_leader2015"),
    "story_act4_ch2_m5": ("Starscream", None),
    "story_act4_ch2_m6": ("Megatronus", "megatronus_gs_kabam"),
}
BOSSMAP = ROOT / "data" / "boss_map.json"
QL = DATA / "quest_list.json"
REAL = ROOT / "data" / "quests_real.json"
GAPS = ROOT / "data" / "boss_gaps.json"

bossmap = json.loads(BOSSMAP.read_text(encoding="utf-8"))
for qid, (name, cid) in BOSSES.items():
    row = bossmap.setdefault(qid, {})
    row["name"] = row.get("name") or name
    row["boss"] = name
    row["boss_client_id"] = cid
    row["match"] = "wiki_act4"
    row["reason"] = ("[WIKI] Awaken and Corrupt revision: " + name +
                     ("; no 9.2.0 pack" if cid is None else ""))
BOSSMAP.write_text(json.dumps(bossmap, ensure_ascii=False, indent=1), encoding="utf-8")

sets = json.loads(QL.read_text(encoding="utf-8"))
patched = 0
for s in sets:
    for q in s.get("availableQuests", []):
        qid = q.get("id")
        if qid in BOSSES:
            name, cid = BOSSES[qid]
            q["boss"] = name
            q["bossName"] = name
            if cid:
                q["finalBoss"] = {"id": cid, "level": 1, "rank": 1}
                patched += 1
QL.write_text(json.dumps(sets, ensure_ascii=False, indent=1), encoding="utf-8")

real = json.loads(REAL.read_text(encoding="utf-8"))
for act in real.get("latest", {}).get("story_acts", []):
    if act.get("act") != 4:
        continue
    for ch in act.get("chapters", []):
        for m in ch.get("missions", []):
            idx = m.get("index")
            if not idx:
                continue
            qid = f"story_act4_ch{ch.get('chapter')}_m{idx}".replace("chI_", "ch1_").replace("chII_", "ch2_")
            if qid in BOSSES:
                m["boss"] = BOSSES[qid][0]
                m["boss_client_id"] = BOSSES[qid][1]
REAL.write_text(json.dumps(real, ensure_ascii=False, indent=1), encoding="utf-8")

gaps = []
for qid, row in bossmap.items():
    if not row.get("boss_client_id"):
        gaps.append({"qid": qid, "boss": row.get("boss"),
                     "boss_client_id": row.get("boss_client_id"),
                     "reason": row.get("reason")})
GAPS.write_text(json.dumps(gaps, ensure_ascii=False, indent=1), encoding="utf-8")

print("patched quest_list", patched, "gaps", len(gaps))
for g in gaps:
    print(g)
