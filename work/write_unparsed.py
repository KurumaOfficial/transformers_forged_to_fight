import json, os
ROOT = r"."
out = os.path.join(ROOT, "data", "wiki", "unparsed")
os.makedirs(out, exist_ok=True)
rows = [
    {"page": "Sharkticon", "reason": "generic NPC; no numeric stat/rank table in saved wikitext",
     "source": "Fandom", "revid": None},
    {"page": "Transformers: Forged to Fight Wiki:Layouts/Bot", "reason": "layout template, not game data",
     "source": "Fandom", "revid": None},
    {"page": "File:* (2796 pages)", "reason": "File description text saved; not parsed into game data",
     "source": "Fandom", "revid": None},
    {"page": "Template/Category/User/Talk/Message Wall/Thread", "reason": "archive metadata, not game data",
     "source": "Fandom", "revid": None},
]
json.dump({"note": "Content pages not represented as structured game data; raw files remain untouched.",
           "items": rows}, open(os.path.join(out, "pages.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
open(os.path.join(out, "README.md"), "w", encoding="utf-8").write(
    "# Unparsed data pages\n\n"
    "See `pages.json`. Raw wikitext is authoritative; values were not invented.\n")
print("ok")
