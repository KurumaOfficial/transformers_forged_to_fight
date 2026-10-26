# Bot matrix — 3.1 (2026-10-26)

Sources: `server/data/bot_catalog_real.json` (59 client packs),
`data/wiki/bots.json` (44 wiki stat pages), `work/localization_all.json`
(89 `ID_CHARACTER_BIOS_*` keys), `data/wiki/id_map.json`,
`data/boss_map.json` (90 quest entries). Full rows:
`data/wiki/bot_matrix_full.json`.

## Totals

| List | Count |
|---|---:|
| Client bot packs | **59** |
| Wiki pages with stats | **44** |
| `ID_CHARACTER_BIOS_*` keys | **89** |
| Client bots mapped to a wiki page | 39 |
| Client bots without a mapped wiki page | 20 |
| Wiki pages without a 9.2.0 client pack | 5 |
| Client bots used as quest bosses | 36 |
| Quest entries with a boss client id | 81/90 |

## Client bots without a mapped wiki page (20)

`blaster_gs_leader2016`, `bumblebee_cin_dotm`, `cheetor_bw_transmetal`,
`cyclonus_gs_uw06`, `dinobot_bw_kabam`, `dirge_gs_deluxe2008`,
`grimlock_gs_mp08`, `grindor_cin_rotf`, `kickback_gs_kabam`,
`megatronus_gs_kabam`, `optimusprimal_bw_mp32`, `ratchet_gs_kabam`,
`sharkticon_gs_brawler`, `sharkticon_gs_demolition`, `sharkticon_gs_kabam`,
`sharkticon_gs_scout`, `sharkticon_gs_tactician`, `sharkticon_gs_tech`,
`sharkticon_gs_warrior`, `soundwave_gs`.

Most of these are **variant/base-name** collisions (`Bumblebee (DOTM)` is
matched only manually; the five Sharkticon variants share one page) or have no
stat page. They are not evidence of a missing client pack: all 20 exist in the
59-pack catalog.

## Wiki pages without a client pack (5)

`Chromia`, `Dead End`, `Optimus Prime`, `Soundblaster/Tactician`,
`Starscream`.

- `Starscream` also has no 9.2.0 character ODR bundle: `characters/toc.txt`
  lists `starscream_gs`/`starscream_gs_lw` remote paths, but the APK contains no
  bundle, no blueprint/hero entry, and no character bio for the playable pack.
- `Chromia`, `Dead End`, `Optimus Prime` (base page) and
  `Soundblaster/Tactician` are wiki content outside the 9.2.0 catalog or
  sub-variants; no matching client id in `id_map`.
- `Optimus Prime` base page is mapped to `Optimus Prime (MV1)` for the client
  pack, so it is not a missing pack; it is a page-name split.

## Bio keys

89 keys total. 20 are **non-character/zone keys** (`ID_CHARACTER_BIOS_Z_*`,
`HQ1`, etc.) and were excluded from the character match. The remaining keys
match the client roster by name abbreviation; `STARS_GS` exists but has no
client pack, and `OPRIMAL_BW` has no 9.2.0 pack. The bio key is not a reliable
client id: it is an abbreviated localization key, not the blueprint id.

## Quest roles

36 distinct client bots appear as quest bosses (81/90 entries with an id).
The 9 remaining gaps are all Starscream. Full per-quest list:
`data/boss_map.json` and `data/wiki/bot_matrix_full.json` (`boss_quests`).

## Conclusions

- All 59 client packs have a blueprint; 37 have wiki stats, 22 are `[ASSUMED]`
  class-median priors (`data/wiki/stat_coverage.json`).
- The five extra wiki pages are content outside the 9.2.0 install (Starscream,
  Chromia, Dead End, Soundblaster/Tactician) or page-name variants (Optimus
  Prime).
- The 20 "without wiki page" client bots are variant/page-mapping gaps, not
  missing client content; their stats remain `[ASSUMED]` where no table exists.
