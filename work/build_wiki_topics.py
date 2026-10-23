import json
import re
from pathlib import Path

root = Path(r"C:\Users\gameg\Desktop\TFTF")
pages = json.loads((root / "data/wiki/pages.json").read_text(encoding="utf-8"))["pages"]
versions = {}
for p in (root / "data/wiki/versions").glob("*.json"):
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        versions[d["page"]] = d
    except Exception:
        pass
cutoff = "2023-01-13T23:59:59Z"
outdir = root / "data/wiki/topics"
outdir.mkdir(parents=True, exist_ok=True)

def rec(name):
    r = pages.get(name)
    if not r:
        return None
    src = r.get("source", {})
    v = versions.get(name, {})
    ts = src.get("timestamp", "")
    as_of = None
    if ts and ts <= cutoff:
        as_of = {"revid": src.get("revid"), "timestamp": ts, "parsed": r}
    elif v.get("as_of_content"):
        as_of = {"revid": v.get("as_of_revid"), "timestamp": v.get("as_of_timestamp"),
                 "raw_wikitext": v.get("as_of_content")}
    return {
        "page": name,
        "url": src.get("url"),
        "tag": "[WIKI]",
        "as_of_2023": as_of,
        "latest": {"revid": src.get("revid"), "timestamp": ts, "parsed": r},
        "created_after_cutoff": bool(v.get("created_after_cutoff")),
        "changed_since_cutoff": bool(v.get("changed")),
    }

def headings(name):
    r = pages.get(name) or {}
    return [s.get("heading") for s in r.get("sections", []) if s.get("heading")]

topics = {
    "missions_story": ["Story", "Story/Netflix", "Special Mission", "A Bad Name", "A Glass Darkly",
                        "A Lesson Learned in Time", "A Question of Loyalty", "A Shocking Farewell",
                        "A Tale of Two Stingers", "Awaken and Corrupt", "Bring the Noise"],
    "events": ["Special Mission", "Calendar", "Proving Grounds", "Showcase", "Release the Beast",
               "Screen Time", "Training Montage"],
    "arena": ["Arena", "Arena Chip"],
    "raids": ["Raid", "Raid Chip", "Raid Shield", "Gold Raid Trophy"],
    "away": ["Away Mission", "Alliance Mission", "Mobile Command"],
    "mods": ["Module", "Utility Module", "Mods"],
    "relics": [n for n in pages if re.search(r"(?i)relic", n)],
    "crystals": [n for n in pages if re.search(r"(?i)crystal", n)],
    "currencies": ["Gold", "Energon", "Allspark", "Arena Chip", "Bot Chip", "Shanix", "Z-Energon", "Spark"],
    "forge": [n for n in pages if re.search(r"(?i)forge", n)],
    "progression": ["Progression", "Masteries", "Bot Rank", "Rank", "Level", "Signature Ability"],
    "class_triangle": ["Brawler", "Scout", "Warrior", "Tactician", "Class", "Class Triangle", "Bot Class"],
    "status_effects": ["Acid", "Armor Break", "Armor Buff", "Bleed", "Burn", "Shock", "Stun", "Slow",
                        "Heal Block", "Power Gain", "Regeneration", "Shield", "Crit", "Evade", "Nullify"],
}
for topic, names in topics.items():
    selected = {}
    for n in names:
        r = rec(n)
        if r:
            selected[n] = r
    extra = {}
    if topic == "missions_story":
        extra["story_arc_headings"] = headings("Story")
        extra["netflix_story_headings"] = headings("Story/Netflix")
        extra["special_mission_headings"] = headings("Special Mission")
    if topic == "events":
        extra["special_mission_headings"] = headings("Special Mission")
    out = {
        "source": "Fandom pages parsed in data/wiki/pages.json; as_of/latest from data/wiki/versions/",
        "cutoff": cutoff,
        "topic": topic,
        "note": "Curated page set; values only from saved wikitext. as_of uses parsed page when revision <= cutoff, otherwise raw wikitext or null.",
        "page_count": len(selected),
        "pages": selected,
    }
    out.update(extra)
    (outdir / f"{topic}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(topic, len(selected))
