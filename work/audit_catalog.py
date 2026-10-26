"""Catalog completeness audit for battle fighters (1.3)."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = json.loads((ROOT / "server" / "data" / "bcg_login_data.json").read_text(encoding="utf-8"))
BOTS = json.loads((ROOT / "server" / "data" / "bot_catalog_real.json").read_text(encoding="utf-8"))["rows"]
TARGETS = ["bumblebee_cin_dotm_2", "rhinox_gs_voyager2014", "sideswipe_gs", "bumblebee_gs_kabam"]
OUT = ROOT / "data" / "catalog_completeness.json"


def keys_of(d):
    return set(d.keys()) if isinstance(d, dict) else set()


def union_keys(sec):
    out = set()
    for v in sec.values():
        if isinstance(v, dict):
            out |= set(v.keys())
    return out


def report(name, sec, targets):
    uni = union_keys(sec)
    rows = {}
    for t in targets:
        v = sec.get(t)
        if not isinstance(v, dict):
            rows[t] = {"present": False}
            continue
        missing = sorted(uni - set(v.keys()))
        rows[t] = {"present": True, "missing_vs_union": missing,
                   "keys": sorted(v.keys())}
    return {"section": name, "union_count": len(uni), "rows": rows}


bp = CAT.get("blueprints", {})
ch = CAT.get("characters", {})
heroes = CAT.get("heroes", {})
ud_heroes = {h.get("bid"): h for h in CAT.get("userData", {}).get("heroes", []) if isinstance(h, dict)}
teams = CAT.get("userData", {}).get("activeTeams", [])
team_heroes = {}
for t in teams if isinstance(teams, list) else []:
    hv = t.get("heroes")
    if isinstance(hv, dict):
        hv = list(hv.values())
    for h in hv or []:
        if isinstance(h, dict) and h.get("bid"):
            team_heroes[h["bid"]] = h

out = {
    "blueprints": report("blueprints", bp, TARGETS),
    "characters": report("characters", ch, TARGETS),
    "heroes_rank_tables": {},
    "userData_heroes": report("userData.heroes", ud_heroes, TARGETS),
    "activeTeam_heroes": report("activeTeams.heroes", team_heroes, TARGETS),
}
for t in TARGETS:
    v = heroes.get(t)
    out["heroes_rank_tables"][t] = {"present": isinstance(v, dict),
                                    "rank_keys": sorted(v.keys()) if isinstance(v, dict) else []}

# boss coverage
boss_ids = set()
ql = json.loads((ROOT / "server" / "data" / "quest_list.json").read_text(encoding="utf-8"))
for qs in ql:
    for q in qs.get("availableQuests", []):
        b = (q.get("finalBoss") or {}).get("id")
        if b:
            boss_ids.add(b)
out["boss_coverage"] = {
    "unique_boss_ids": len(boss_ids),
    "missing_blueprint": sorted(b for b in boss_ids if b not in bp),
    "missing_character": sorted(b for b in boss_ids if b not in ch),
    "missing_userData_hero": sorted(b for b in boss_ids if b not in ud_heroes),
    "missing_hero_rank_table": sorted(b for b in boss_ids if b not in heroes),
}
# activate-match response
act = json.loads((ROOT / "server" / "data" / "match_activate_response.json").read_text(encoding="utf-8"))
fd = act.get("fighterData") or {}
out["match_activate"] = {
    "top_keys": sorted(act.keys()),
    "fighter_keys": sorted(fd.keys()),
    "enemy_keys": sorted((fd.get("enemyFighter") or {}).keys()),
    "has_player": "playerFighter" in fd,
}

OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(out, ensure_ascii=False, indent=1))
