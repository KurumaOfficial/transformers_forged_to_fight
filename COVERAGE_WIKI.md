# COVERAGE_WIKI

## Fandom

- Enumerated pages: **3613** (non-File **817** + File **2796**).
- Saved with full revision history + HTML: **822** = **817 non-File + 5 File**.
  This confirms the [DERIVED] hypothesis: all non-File pages are saved.
- Saved File descriptions (latest revision): **2796/2796** in
  `archive/wiki/raw/fandom/file_descriptions/`.
- Revisions stored: **8985** (Fandom+TFWiki full-history pages); HTML snapshots: **830**.
- allredirects=20, allcategories=80, allimages=2752.
- Image binaries downloaded: **523/2752** (maps, missions, UI, tables first;
  portraits/icons last). 403s are recorded; 24 total errors.
- Manifest entries: **4983**; state: `archive/wiki/state.json`.

## TFWiki (mirror)

- Whole wiki reports 139066 pages; only FTF-related pages were taken.
- Saved: **8** pages with full history + HTML:
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

## Backup

- ZIP: `archive/TFTF_wiki_archive_2026-10-23.zip`
- Size: `27,355,942` bytes
- SHA256: `7220eabce902e552ed2bc6d86ca9d55477baeede6802ab9fd656306682be1aaf`
- Contains the whole `archive/wiki` tree (raw revisions, HTML, File
  descriptions, 523 image binaries, state, manifest, meta). `data/wiki/*.json`
  and docs are outside this zip.
