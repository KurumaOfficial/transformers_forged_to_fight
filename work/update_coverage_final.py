import json, os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"."
W = os.path.join(ROOT, "archive", "wiki")
state = json.load(open(os.path.join(W, "state.json"), encoding="utf-8"))
state["file_descriptions"] = {
    "count": 2796,
    "path": "raw/fandom/file_descriptions/",
    "scope": "latest revision only (all File: pages); full history+HTML is saved for 822 pages",
}
json.dump(state, open(os.path.join(W, "state.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

import json as j
m = j.load(open(os.path.join(W, "manifest.json"), encoding="utf-8"))
e = j.load(open(os.path.join(W, "errors.json"), encoding="utf-8"))
s = state
fandom_saved = sum(1 for k in s["pages"] if k.startswith("fandom|"))
tf = sum(1 for k in s["pages"] if k.startswith("tfwiki|"))
files = len(s["files"])
text = f'''# COVERAGE_WIKI

## Fandom

- Enumerated pages: **3613** (non-File **817** + File **2796**).
- Saved with full revision history + HTML: **{fandom_saved}** = **817 non-File + 5 File**.
  This confirms the [DERIVED] hypothesis: all non-File pages are saved.
- Saved File descriptions (latest revision): **2796/2796** in
  `archive/wiki/raw/fandom/file_descriptions/`.
- Revisions stored: **8985** (Fandom+TFWiki full-history pages); HTML snapshots: **830**.
- allredirects=20, allcategories=80, allimages=2752.
- Image binaries downloaded: **{files}/2752** (maps, missions, UI, tables first;
  portraits/icons last). 403s are recorded; 24 total errors.
- Manifest entries: **{len(m)}**; state: `archive/wiki/state.json`.

## TFWiki (mirror)

- Whole wiki reports 139066 pages; only FTF-related pages were taken.
- Saved: **{tf}** pages with full history + HTML:
  `Forged to Fight`, `Transformers: Forged to Fight`, `Crossfire`,
  `Crossfire (Forged to Fight)`, `Generations`, `Prime Suspect`,
  `Magnus Opus`, `Crossfire (Prime)`.

## Extensions

- Fandom: Scribunto=yes, Cargo=no. `Module:` (ns 828) has 0 pages.
- TFWiki: Scribunto=no, Cargo=no.

## Parsed game data (`data/wiki/`)

- **44 bots** in `data/wiki/bots.json`, each with page/revid/url:
  infobox, star stats, rank/level tables, abilities, signature table,
  special attacks, synergy.
- **252 other content pages** in `data/wiki/pages.json` (generic sections + tables):
  classes, status effects, modules, relics, crystals, currencies, missions,
  events, story, arena, raids, away missions, etc.
- Every entry has source page/revid/url and `[WIKI]`.
- **2 content pages unparsed**:
  - `Sharkticon` — generic NPC, no numeric stat table;
  - `Transformers: Forged to Fight Wiki:Layouts/Bot` — layout template.
  See `data/wiki/unparsed/pages.json`.
- File/Template/Category/User/Talk/Message Wall/Thread pages are archived but
  not treated as game data; they are metadata.

## Not closed / caveats

- Images: 523/2752 binaries; remaining URLs are resumable. Some static.wikia
  403s remain; no bypass was used.
- Hidden base stats (crit, armor, block) are absent from many wiki bot pages;
  they are **not** invented. Only values present in tables/text are stored.
- Parser is regex-based; unusual tables may be partial. Raw wikitext remains
  authoritative and untouched.
- OneDrive collection link is auth-gated (`isAuthenticated:false`); not downloaded.
'''
open(os.path.join(ROOT, "COVERAGE_WIKI.md"), "w", encoding="utf-8").write(text)
print("coverage updated", fandom_saved, len(m), files, len(e))
