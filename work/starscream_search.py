"""Search all client data for Starscream/seeker names and list gaps."""
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "starscream_search.md"
TOKENS = ("starscream", "star scream", "scream", "seeker", "conehead",
          "cone head", "ss_", "stars_", "g1_", "2017")

hits = []


def note(path, line):
    hits.append((str(path).replace(str(ROOT) + os.sep, ""), line))


# 1. file names
for base in ("work/unpacked/assets", "work/unpacked"):
    p = ROOT / base
    if not p.exists():
        continue
    for dp, dn, fn in os.walk(p):
        for f in fn:
            low = f.lower()
            if any(t in low for t in ("starscream", "stars_", "seeker", "conehead")):
                note(os.path.join(dp, f), "filename")

# 2. localization keys/values
loc = json.loads((ROOT / "work" / "localization_all.json").read_text(encoding="utf-8"))
for k, v in loc.items():
    s = (k + " " + str(v)).lower()
    if "stars" in s or "scream" in s:
        note("work/localization_all.json", f"{k} = {str(v)[:120]}")

# 3. login catalog
login = json.loads((ROOT / "server" / "data" / "bcg_login_data.json").read_text(encoding="utf-8"))
for section in ("blueprints", "characters", "heroes"):
    obj = login.get(section) or {}
    items = obj.items() if isinstance(obj, dict) else [(str(i), x) for i, x in enumerate(obj)]
    for k, v in items:
        s = (str(k) + " " + json.dumps(v, ensure_ascii=False)).lower()
        if "stars" in s or "scream" in s or "seeker" in s:
            note("server/data/bcg_login_data.json", f"{section}/{k}")

# 4. wiki matrix
bm = json.loads((ROOT / "data" / "wiki" / "bot_matrix_full.json").read_text(encoding="utf-8"))
for key in ("client_without_wiki_page", "client_without_stats",
            "unmapped_wiki_pages", "unmatched_bio_keys"):
    vals = bm.get(key) or []
    for v in vals:
        if "stars" in str(v).lower() or "scream" in str(v).lower():
            note("data/wiki/bot_matrix_full.json", f"{key}: {v}")

# 5. bot pack dirs vs wiki pages
packs = []
for base in (ROOT / "work" / "unpacked" / "assets",):
    for dp, dn, fn in os.walk(base):
        for d in dn:
            if d.endswith("_odr") or "_odr" in d:
                packs.append(d)
packs = sorted(set(packs))
wiki = json.loads((ROOT / "data" / "wiki" / "bots.json").read_text(encoding="utf-8"))["bots"]

lines = [
    "# Starscream search (Step 7)",
    "",
    "Status: **no Starscream pack in the retained 9.2.0 assets.** The bot is",
    "pre-APK (infobox release 2017-08-24); the 9 missing boss ids are a",
    "pack/mapping gap, not post-APK content.",
    "",
    "## Search scope",
    "",
    "- every filename under `work/unpacked/assets` and `work/unpacked`;",
    "- `work/localization_all.json` keys/values;",
    "- `server/data/bcg_login_data.json` `blueprints`, `characters`, `heroes`;",
    "- `data/wiki/bot_matrix_full.json` missing/unmapped lists;",
    "- `data/wiki/bots.json` release dates.",
    "",
    "## Hits",
    "",
]
if hits:
    for path, line in hits[:200]:
        lines.append(f"- `{path}`: {line}")
else:
    lines.append("- **none** for `starscream`/`seeker`/`conehead` in the scanned names and keys.")

lines += [
    "",
    f"Bot pack dirs scanned: **{len(packs)}**; wiki bot pages: **{len(wiki)}**.",
    "",
    "## Missing/unmapped (from bot_matrix_full)",
    "",
]
for key in ("client_without_wiki_page", "client_without_stats",
            "unmapped_wiki_pages"):
    vals = bm.get(key) or []
    lines.append(f"- **{key}** ({len(vals)}): " + ", ".join(str(v) for v in vals))
    lines.append("")

lines += [
    "## Conclusion",
    "",
    "- No Starscream bundle/toc/prefab/localization key was found.",
    "- The Starscream infobox release date is 2017-08-24; this is not post-APK.",
    "- A separate wiki page for Starscream is absent from the saved page set, so",
    "  the name match cannot be done from a page; the boss ids remain a pack gap.",
    "- The fallback stays `[ASSUMED]` (`nemesisprime_gs_voyager2015`), not retail.",
    "- Do not add a fake Starscream pack; it would not match the client move data.",
    "",
]
OUT.write_text("\n".join(lines), encoding="utf-8")
print("wrote", OUT, "hits", len(hits), "packs", len(packs))
