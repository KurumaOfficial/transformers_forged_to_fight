"""Validate battle-facing enum/string selectors in the catalog and quest data."""
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = json.loads((ROOT / "server" / "data" / "bcg_login_data.json").read_text(encoding="utf-8"))
QL = json.loads((ROOT / "server" / "data" / "quest_list.json").read_text(encoding="utf-8"))
OUT = ROOT / "data" / "battle_enum_audit.json"

classes = {"braw", "tact", "scou", "demo", "warr", "tech", "generic", "superior",
           "basic", "alpha", "off", "def", "uti", "none"}
damage = set((CAT.get("damage_types") or {}).keys())
factions = {"Neutral", "Autobot", "Decepticon", "Maximal", "Predacon"}
entity_types = {"hero", "boss", "bot", "tower", "entity", ""}

bp_bad = defaultdict(list)
bp_values = defaultdict(Counter)
for bid, bp in (CAT.get("blueprints") or {}).items():
    for key in ("class", "hero_class", "cl", "entity_type", "type"):
        if key in bp:
            bp_values[key][str(bp[key])] += 1
    cls = str(bp.get("class") or bp.get("hero_class") or bp.get("cl") or "")
    if cls and not cls.isdigit() and cls not in classes:
        bp_bad["class"].append((bid, cls))
    for key in ("base_damage", "base_ranged_damage"):
        for v in bp.get(key) or []:
            if v not in damage:
                bp_bad[key].append((bid, v))

ch_bad = defaultdict(list)
ch_values = defaultdict(Counter)
for cid, ch in (CAT.get("characters") or {}).items():
    for key in ("faction", "subgroup", "generation", "ai_personality", "entity_type"):
        if key in ch:
            ch_values[key][str(ch[key])] += 1
    for key in ("base_damage", "base_ranged_damage"):
        for v in ch.get(key) or []:
            if v not in damage:
                ch_bad[key].append((cid, v))

quest_ai = defaultdict(Counter)
quest_bad = []
for qs in QL:
    for q in qs.get("availableQuests", []):
        for side, s in (q.get("scaledBossTable") or {}).items():
            for key in ("aiString", "aiPer", "type", "baseType", "key"):
                if key in s:
                    quest_ai[key][str(s[key])] += 1
            if s.get("aiString") not in (None, "", "default"):
                quest_bad.append((q.get("id"), side, "aiString", s.get("aiString")))
            if s.get("aiPer") not in (None, "", "default", "aggressive", "defensive", "balanced"):
                quest_bad.append((q.get("id"), side, "aiPer", s.get("aiPer")))

out = {
    "classes_allowed": sorted(classes),
    "damage_allowed": sorted(damage),
    "factions_allowed": sorted(factions),
    "entity_types_allowed": sorted(entity_types),
    "blueprint_values": {k: dict(v) for k, v in bp_values.items()},
    "character_values": {k: dict(v) for k, v in ch_values.items()},
    "quest_ai": {k: dict(v) for k, v in quest_ai.items()},
    "blueprint_bad": dict(bp_bad),
    "character_bad": dict(ch_bad),
    "quest_bad": quest_bad,
}
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({k: out[k] for k in ("blueprint_bad", "character_bad", "quest_bad")},
                 ensure_ascii=False, indent=1))
