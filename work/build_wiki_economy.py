"""W2/W3/W4: consolidate existing wiki topic files into economy/classes/synergy JSON."""
import json
import re
from pathlib import Path

ROOT = Path(r"C:\Users\gameg\Desktop\TFTF")
TOP = ROOT / "data" / "wiki" / "topics"
OUT = ROOT / "data" / "wiki"


def load(name):
    p = TOP / f"{name}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"pages": {}}


def numeric_lines(text):
    if not text:
        return []
    out = []
    for line in text.splitlines():
        s = line.strip()
        if not s or len(s) > 300:
            continue
        if re.search(r"\d", s) and any(k in s.lower() for k in
                                      ("cost", "price", "gold", "crystal", "energon", "xp",
                                       "rank", "level", "%", "chance", "reward", "shard",
                                       "energy", "purchase", "buy", "amount")):
            out.append(s)
    return out[:40]


def side(page, key):
    v = page.get(key)
    if not isinstance(v, dict):
        return {"present": False, "content": None, "numeric_lines": []}
    content = v.get("raw_wikitext") or v.get("content")
    return {"present": True, "revid": v.get("revid"), "timestamp": v.get("timestamp"),
            "numeric_lines": numeric_lines(content)}


economy_topics = ["currencies", "forge", "progression", "crystals", "mods", "relics",
                  "arena", "events"]
economy = {"source": "data/wiki/topics/*.json (saved wikitext only)", "cutoff": "2023-01-13T23:59:59Z",
           "sections": {}, "gaps": []}
for t in economy_topics:
    d = load(t)
    pages = {}
    for name, page in (d.get("pages") or {}).items():
        pages[name] = {"url": page.get("url"),
                       "as_of_2023": side(page, "as_of_2023"),
                       "latest": side(page, "latest")}
    economy["sections"][t] = pages
    if not pages:
        economy["gaps"].append(f"{t}: no page set")
for t, pages in economy["sections"].items():
    if not pages:
        continue
    if not any(p["as_of_2023"]["present"] or p["latest"]["present"] for p in pages.values()):
        economy["gaps"].append(f"{t}: page set has no parsed content")
economy["gaps"].append("Numeric values are extracted as lines, not as a typed cost table; "
                       "many pages do not state exact costs.")
(OUT / "economy.json").write_text(json.dumps(economy, ensure_ascii=False, indent=1), encoding="utf-8")

# Classes / status effects
ct = load("class_triangle")
se = load("status_effects")
classes = {"source": "data/wiki/topics/class_triangle.json", "triangle": {}, "pages": {},
           "numeric_note": "The wiki pages give the triangle and qualitative bonuses; exact "
                           "damage multipliers are not stated in the saved text."}
for name, page in (ct.get("pages") or {}).items():
    text = ((page.get("as_of_2023") or {}).get("raw_wikitext") or
            (page.get("latest") or {}).get("raw_wikitext") or "")
    m = re.search(r"class_bonus\s*=\s*\[\[([^\]|]+)", text)
    w = re.search(r"weakness\s*=\s*\[\[([^\]|]+)", text)
    classes["triangle"][name] = {"bonus_against": m.group(1) if m else None,
                                 "weak_to": w.group(1) if w else None,
                                 "url": page.get("url")}
    classes["pages"][name] = {"as_of_2023": side(page, "as_of_2023"),
                              "latest": side(page, "latest")}
status = {"source": "data/wiki/topics/status_effects.json", "pages": {},
          "note": "Descriptions and any numeric lines from saved wikitext; no fabricated numbers."}
for name, page in (se.get("pages") or {}).items():
    status["pages"][name] = {"url": page.get("url"),
                             "as_of_2023": side(page, "as_of_2023"),
                             "latest": side(page, "latest")}
(OUT / "classes_status.json").write_text(json.dumps({"classes": classes, "status": status},
                                                    ensure_ascii=False, indent=1), encoding="utf-8")

# Synergies
vers = ROOT / "data" / "wiki" / "versions"
syn = {"source": "data/wiki/versions/Synergy*.json", "pages": {}, "gaps": []}
for p in [vers / "Synergy%20Bonus.json", vers / "Synergy.json"]:
    if not p.exists():
        continue
    d = json.loads(p.read_text(encoding="utf-8"))
    content = d.get("as_of_content") or ""
    syn["pages"][d.get("page")] = {
        "url": d.get("url"),
        "revid": d.get("as_of_revid"),
        "timestamp": d.get("as_of_timestamp"),
        "headings": re.findall(r"^==+\s*([^=]+?)\s*==+$", content, re.M),
        "numeric_lines": numeric_lines(content),
        "content": content,
    }
syn["gaps"].append("Per-bot synergy mapping/formulas are not in the saved two pages; "
                   "the client `synergyBonuses` arrays are empty in the stub.")
(OUT / "synergies.json").write_text(json.dumps(syn, ensure_ascii=False, indent=1), encoding="utf-8")

print("economy sections", list(economy["sections"]), "gaps", len(economy["gaps"]))
print("classes", len(classes["triangle"]), "status pages", len(status["pages"]))
print("synergy pages", list(syn["pages"]))
