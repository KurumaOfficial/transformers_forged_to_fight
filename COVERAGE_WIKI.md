# COVERAGE_WIKI

## Fandom archive

- Enumerated: **3613** = **817 non-File + 2796 File**.
- Full history + HTML: **822** = **817 non-File + 5 File**.
  The [DERIVED] hypothesis is confirmed: every non-File page is saved.
- File descriptions (latest revision): **2796/2796** in
  `archive/wiki/raw/fandom/file_descriptions/`.
- Revisions stored: **8985**; HTML snapshots: **830**.
- allredirects=20, allcategories=80, allimages=2752.
- Image binaries: **694/2752**; **209** errors
  (mostly static.wikia 403, no bypass). Remaining URLs are resumable.
- Manifest: **5154** entries; state: `archive/wiki/state.json`.

## TFWiki mirror

- 8 FTF pages with full history + HTML: `Forged to Fight`,
  `Transformers: Forged to Fight`, `Crossfire`,
  `Crossfire (Forged to Fight)`, `Generations`, `Prime Suspect`,
  `Magnus Opus`, `Crossfire (Prime)`.

## Extensions

- Fandom: Scribunto=yes, Cargo=no; `Module:` (ns 828) = 0 pages.
- TFWiki: Scribunto=no, Cargo=no.

## Parsed game data

- **44 bots** — `data/wiki/bots.json`: infobox, star HP/Attack/rating,
  rank/level tables, abilities, signature tables, special attacks,
  synergy; source page/revid/url/[WIKI].
- **252 pages** — `data/wiki/pages.json`: classes, status effects, mods,
  relics, crystals, currencies, missions, events, story, arena, raids,
  away missions; generic sections/tables with source.
- **Quality matrix** - `data/wiki/bot_matrix.json`: 44
  bots; counts: {"star_health_attack": 43, "rank_level_table": 38, "level_values": 38, "abilities": 38, "ability_rank_table": 37, "signature": 40, "signature_table": 39, "special_attacks": 41, "synergy": 40}.
  Missing lists are in `matrix["missing"]`. Synergy parser now accepts
  `===Synergy Bonuses===` and `Common Synergies`; remaining 4 pages have no
  parseable synergy section (Chromia, Cliffjumper, Ironhide, Soundblaster). [WIKI]
- **ID map** — `data/wiki/id_map.json`: **59** client packs = **52** bots + **7** Sharkticon variants. **39** non-Sharkticon bots have a wiki stat page; **13** client bots have no stat page; all 7 Sharkticon variants have no separate stat page. Wiki stat pages: **44** = 39 matched + 5 wiki-only (Chromia, Dead End, Optimus Prime, Soundblaster/Tactician, Starscream).
- **Version sets** — `data/wiki/versions.json` + `versions/<page>.json`:
  cutoff **2023-01-13T23:59:59Z**; 296 pages analyzed;
  **96** changed; **11**
  created after cutoff: Acid, Bots Than Should Be A Different Bot Class Type, Bots That Don't Act Like Their Bot Class Type, Dead End, Progression, Proving Grounds, Showcase, Soundblaster, Story/Netflix, Transformers: Forged to Fight (Netflix), Tutorial/Getting Started With the Game's Unity Files and Assets.
- **Unparsed** — `data/wiki/unparsed/pages.json`: Sharkticon (no numeric
  table), layout template, and metadata namespaces. File descriptions are
  archived but not parsed as game data.

## Caveats

- Hidden base stats (crit/armor/block) are often absent from wiki tables;
  they are not invented.
- Regex parser may miss unusual tables; raw wikitext is authoritative.
- OneDrive collection is auth-gated (`isAuthenticated:false`); not downloaded.
- Backup ZIP path/hash are below; regenerate after future downloads.

## Backup

- ZIP: `archive/TFTF_wiki_archive_2026-10-23.zip`
- SHA256: `14b714b8e7e1409a2e74c32847ad78c7ee1e4a72cde3debfe97c2892da029c17`
- Integrity re-pack: `archive/TFTF_wiki_archive_2026-10-23_210335.zip`
  (32,504,603 bytes; SHA256 `0731484c7c26463482488ac08f52ee75881bea7c3910f7cf9f3758da1509d559`).
  Manifest 5154/5154 verified after five stale-hash corrections; see
  `archive/INTEGRITY.md`.


## Structured topic sets (W3)

`data/wiki/topics/` — curated page sets with separate `as_of_2023` and
`latest` records and source URLs:

- `missions_story.json` (11 pages + story/netflix/special-mission headings)
- `events.json` (7 pages + special-mission headings)
- `arena.json` (2), `raids.json` (4), `away.json` (3), `mods.json` (2),
  `relics.json` (14), `crystals.json` (2), `currencies.json` (6),
  `forge.json` (7), `progression.json` (3), `class_triangle.json` (5),
  `status_effects.json` (8).

These are page-level structured records, not yet a complete numeric economy
table; fields absent from the saved wikitext stay absent. [WIKI]

## Client-only / wiki-only (W4)

`data/wiki/client_only.json`: 13 client packs without a parsed wiki stat page,
7 Sharkticon variants, and 5 wiki-only pages (Chromia, Dead End, Optimus Prime,
Soundblaster/Tactician, Starscream). [CLIENT]+[WIKI]
