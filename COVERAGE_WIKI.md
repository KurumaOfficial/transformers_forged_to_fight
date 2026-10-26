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

- Image index: `data/wiki/image_index.json` (694 unique files / 698 manifest
  entries; 209 403 errors; categories maps_quests/items/ui/bots/other).
- Ability localization: `data/wiki/ability_localization_client.json` (3315
  D_STAT/ID_STAT entries from binary assets; language and bot mapping open).

## 2026-10-24 additions (W1–W3)

- W1: five stale-hash corrections explained; the current bytes match the
  corrected hashes. Two HTML files are redirect/other-page responses relative
  to their revision JSON (`Meet Your Makers`, `Nothing And Everything`); raw
  untouched. See `archive/wiki/MISMATCHES.md`.
- W2: five wiki-only pages analysed. Only `Optimus Prime` maps to a client
  pack (`optimusprime_cin_tf`, wiki title "Optimus Prime (MV1)").
  `Soundblaster/Tactician` is a class variant not in 9.2.0; Chromia, Dead End
  and Starscream have no 9.2.0 client pack. `data/wiki/id_map.json` updated.
- W3: `data/quests_real.json`: 66 Story missions in 4 acts from the archived
  Story page; 24 missions in `Awaken and Corrupt`; 3 each in three other act
  pages. 39 boss names matched to client ids with high confidence; 8
  ambiguous, 7 none, 12 missing. Quest 1.1 = "A Beast to Start" / Rhinox.
- Not done: W4 re-run after id_map update; W5 image retry (209 HTTP 403).

## 2026-10-24 (v4.3)

- `docs/interfaces.md` generated from the live registry: 78 interfaces,
  tags, implementations, persistent, screen/subsystem, stub status.
- `IAdsProvider` is the only persistent (tform) interface; no ad-network
  HTTP request observed.
- `work/check_all.ps1` prints `target_checks` and `known_issues`/xfail status.
- `MASTER_PROMPT.md` updated to v4.3 with current facts and queue.

## 2026-10-25 W-track status

- W1: 2 priority images recovered with Referer/UA (stop on 403/429); 34
  priority images remain 403 or have no manifest URL.
- W2: `data/wiki/economy.json` with `as_of_2023`/`latest` sides and numeric
  lines; `docs/wiki_economy_gaps.md` lists missing exact costs.
- W3: `data/wiki/classes_status.json` (5 class pages + 8 status pages);
  exact damage multipliers are not in the saved text.
- W4: `data/wiki/synergies.json` from the two saved synergy pages; per-bot
  formulas are not available.
- W5: `archive/TFTF_wiki_archive_2026-10-25_195954.zip`, 32,506,584 bytes,
  SHA-256 `4a0aa74133eb80ba067e7a541195bb38d28d4b7db96138ab1f1924a1bb22cc9b`.

## 2026-10-25 W/Q/R status

- Q3: 70/90 boss ids after id_map resolution; 20 gaps: 8 Starscream (no
  9.2.0 pack), 12 Act 4 chapter I/II missions with no boss name/table.
- Q1/Q2: dynamic routes + validated 9-tile map template; smoke PASS.
- R1: `data/wiki/stat_coverage.json`; 37 table/WIKI, 22 ASSUMED with 25%
  class-median prior.
- R2: `data/wiki/rating_rows.json`; linear fits RMSE 873 (table) / 425 (stars),
  no integer-exact solution.
- R3/R4: `spec/ability_schema.md`, `data/wiki/ability_pilot.json`; raw
  `M1_SPECIAL_ATTACK_*` is not a retained localization key.
- W1: 2/36 priority images; 34 still blocked.

## 2026-10-26 Q3/R2/battle

- Q3: `bumblebee_cin_dotm` -> `_2` for 3 quests; Act 4 I/II bosses from the
  `Awaken and Corrupt` wiki revision (Bonecrusher, Jetfire, Bumblebee DOTM,
  Blaster, Shockwave, Megatronus, Cheetor, Soundwave, Megatron,
  Thundercracker, Megatronus; Starscream unavailable).
- Boss gaps now 9, all Starscream (no 9.2.0 pack).
- R2.1 formula decoded; server-side `rating_hp/rating_attack` still missing.
- Battle init NRE fixed; combat loop next.

- 3.1: 59 client packs / 44 wiki pages / 89 bios; 36 quest bosses; 5 extra wiki
  pages (Starscream, Chromia, Dead End, Optimus Prime, Soundblaster/Tactician);
  20 variant-mapping gaps. `docs/bot_matrix.md`.
- 6.1: 90/90 maps valid on the 3x3 rule; `docs/map_validity.md`.
- 6.3: economy report flags 37 pages with no numeric table
  (`docs/economy_report.md`).
- 9.1/9.4: cleanup runbook and hook audit written; no execution.

- 2026-10-26 nightly: check_all PASS; full smoke status FAIL (full-mode
  measurement, fast smoke PASS); BOTS sweep 12/59 (pagination missing). Old
  verdict PASS was exit-code-only; corrected script prints FAIL/PARTIAL.

- 2026-10-26 v4.7: BaseRangedDamageType record/evidence; ODR blocker static
  and live (no downloads/manifest, no /odr request, PlayCore missing);
  R2 LP infeasible + parser audit; R1 star anchors; Starscream fallback;
  59-page sweep script; MASTER v4.7.

- S1: **59/59** across 5 BOTS pages; 0 info errors, 0 NRE; popup_error is a
  transition-frame metric. `docs/sweep_diagnosis.md`.

- Nightly 21:19: **PASS** (check_all PASS, smoke PASS, BOTS 59/59).
