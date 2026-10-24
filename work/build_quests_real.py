"""Parse real story mission names/bosses from the saved wiki pages.

Only names and boss strings present in the archived wikitext are emitted.
Rewards/recommended levels are kept as raw text or null; nothing is invented.
"""
import json
import re
from pathlib import Path

ROOT = Path(r"C:\Users\gameg\Desktop\TFTF")
TOPIC = ROOT / "data" / "wiki" / "topics" / "missions_story.json"
CATALOG = ROOT / "server" / "data" / "bot_catalog_real.json"
OUT = ROOT / "data" / "quests_real.json"
CUTOFF = "2023-01-13T23:59:59Z"


def norm(s):
    s = (s or "").lower()
    s = re.sub(r"\([^)]*\)", "", s)
    s = re.sub(r"^(dark of the moon|revenge of the fallen|age of extinction|the last knight)\s+", "", s)
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    return s


def build_boss_map():
    rows = json.loads(CATALOG.read_text(encoding="utf-8"))["rows"]
    by = {}
    for r in rows:
        cid = r["client_id"]
        for key in {norm(r.get("wiki_page")), norm(cid), norm(cid.split("_")[0])}:
            if key:
                by.setdefault(key, []).append(cid)
    # explicit wiki variants
    explicit = {
        "dark of the moon barricade": "barricade_cin_dotm",
        "revenge of the fallen ironhide": "ironhide_cin_rotf",
        "bumblebee dotm": "bumblebee_cin_dotm",
        "dark of the moon bumblebee": "bumblebee_cin_dotm",
        "revenge of the fallen ironhide": "ironhide_cin_rotf",
        "demolitions sharkticon": "sharkticon_gs_demolition",
        "optimus prime mv1": "optimusprime_cin_tf",
        "sharkticon scout": "sharkticon_gs_scout",
        "sharkticon brawler": "sharkticon_gs_brawler",
        "sharkticon warrior": "sharkticon_gs_warrior",
        "sharkticon tech": "sharkticon_gs_tech",
        "sharkticon tactician": "sharkticon_gs_tactician",
        "sharkticon demolition": "sharkticon_gs_demolition",
    }
    for k, v in explicit.items():
        by.setdefault(k, []).append(v)
    return by


def match_boss(name, boss_map):
    key = norm(name)
    ids = boss_map.get(key) or []
    # try suffix tokens (e.g. "Revenge of the Fallen Bonecrusher")
    if not ids:
        for k, v in boss_map.items():
            if key.endswith(k) or k.endswith(key):
                ids = v
                break
    uniq = sorted(set(ids))
    return (uniq[0] if len(uniq) == 1 else None), ("high" if len(uniq) == 1 else ("ambiguous" if uniq else "none"))


def parse_overview(page):
    acts = []
    cur_act = None
    cur_ch = None
    for sec in ((page or {}).get("parsed") or {}).get("sections", []):
        h = sec.get("heading", "").strip()
        m = re.match(r"Act\s+(\d+)\s*[:\-]\s*(.+)", h, re.I)
        if m:
            cur_act = {"act": int(m.group(1)), "name": m.group(2).strip(), "chapters": []}
            acts.append(cur_act); cur_ch = None
            continue
        m = re.match(r"Chapter\s+([0-9IVX]+)\s*[:\-]\s*(.+)", h, re.I)
        if m and cur_act is not None:
            cur_ch = {"chapter": m.group(1), "name": m.group(2).strip(), "missions": []}
            cur_act["chapters"].append(cur_ch)
        text = sec.get("text") or ""
        if cur_ch is not None and text:
            lines = [ln.rstrip() for ln in text.splitlines()]
            mission = None
            for ln in lines:
                if ln.startswith("#*Boss:"):
                    boss = ln.split(":", 1)[1].strip()
                    if mission is not None:
                        mission["boss"] = boss
                    continue
                if ln.startswith("#*"):
                    continue
                if ln.startswith("#"):
                    name = ln.lstrip("#").strip()
                    if name:
                        mission = {"name": name, "boss": None}
                        cur_ch["missions"].append(mission)
    return acts


def parse_act_page(page):
    chapters = []
    cur_ch = None
    for sec in ((page or {}).get("parsed") or {}).get("sections", []):
        h = sec.get("heading", "").strip()
        m = re.match(r"Chapter\s+([0-9IVX]+)\s*[:\-]\s*(.*)", h, re.I)
        if m:
            cur_ch = {"chapter": m.group(1), "name": (m.group(2) or "").strip(), "missions": []}
            chapters.append(cur_ch)
            continue
        m = re.match(r"Mission\s+(\d+)\s*[:\-]\s*(.*)", h, re.I)
        text = sec.get("text") or ""
        if m and cur_ch is not None:
            boss = None
            mb = re.search(r"(?im)^\s*\*?\s*Boss\s*:\s*(.+?)\s*$", text)
            if mb:
                boss = mb.group(1).strip()
            cur_ch["missions"].append({"index": int(m.group(1)), "name": (m.group(2) or "").strip(), "boss": boss})
    return chapters


def main():
    d = json.loads(TOPIC.read_text(encoding="utf-8"))
    boss_map = build_boss_map()
    pages = d.get("pages") or {}
    versions = {}
    for ver in ("as_of_2023", "latest"):
        page_out = {}
        story = pages.get("Story", {}).get(ver) or {}
        story_acts = parse_overview(story)
        for a in story_acts:
            for ch in a["chapters"]:
                for m in ch["missions"]:
                    if m.get("boss"):
                        m["boss_client_id"], m["boss_match"] = match_boss(m["boss"], boss_map)
        page_out["story_acts"] = story_acts
        page_out["story_page"] = {"revid": story.get("revid"), "timestamp": story.get("timestamp")}
        extra = {}
        for name, p in pages.items():
            if name in ("Story", "Story/Netflix"):
                continue
            verp = p.get(ver)
            if not verp:
                continue
            chs = parse_act_page(verp)
            for ch in chs:
                for m in ch["missions"]:
                    if m.get("boss"):
                        m["boss_client_id"], m["boss_match"] = match_boss(m["boss"], boss_map)
            if chs:
                extra[name] = {"revid": verp.get("revid"), "chapters": chs}
        page_out["other_act_pages"] = extra
        versions[ver] = page_out
    out = {
        "source": "data/wiki/topics/missions_story.json (archived Fandom wikitext)",
        "cutoff": CUTOFF,
        "note": "Only mission names and boss strings present in wikitext; rewards/recommended levels are null unless explicitly present. Boss client ids are best-effort matches to bot_catalog_real.json.",
        "as_of_2023": versions["as_of_2023"],
        "latest": versions["latest"],
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    n = sum(len(ch["missions"]) for a in out["latest"]["story_acts"] for ch in a["chapters"])
    print("wrote", OUT, "story missions", n, "acts", len(out["latest"]["story_acts"]),
          "other pages", len(out["latest"]["other_act_pages"]))
    for a in out["latest"]["story_acts"][:1]:
        for ch in a["chapters"][:1]:
            print(a["act"], a["name"], ch["chapter"], ch["name"], ch["missions"])


if __name__ == "__main__":
    main()
