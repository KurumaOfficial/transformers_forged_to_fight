# Starscream fallback (Step 4.1)

## Finding

`[RUN]` Starscream is **not in the 9.2.0 install**:

- `assets/characters/toc.txt` lists remote paths
  `bundles/characters/merged/starscream_gs` and `starscream_gs_lw`, but no
  `starscream_gs.assetbundle` exists in `assets/assetpack/` or
  `assets/*_odr/`.
- `server/data/bcg_login_data.json` has no `blueprints`/`characters`/`heroes`
  entry for Starscream, and the catalog has no `starscream_gs` blueprint.
- Localization has only `ID_LOADING_TIPS_STARSCREAMFIGHT`,
  `ID_STARSCREAM_RANGED`, `ID_STARSCREAM_RANGEDSP1`,
  `ID_STARSCREAM_RANGEDSTUN`; no playable bio `ID_CHARACTER_BIOS_STARS_GS`.
- Wiki has a Starscream page (Tactician, Decepticon, 2–4 stars) but no client
  pack; `data/wiki/bot_matrix_full.json` lists it under "wiki pages without a
  9.2.0 client pack".

Conclusion: **content outside this version** (possibly a later/never-shipped
pack), not a mapping error.

## Decision

Do **not** pretend Starscream is the original boss. For the 9 quests that need
a boss, add an explicit fallback in the data:

- `fallback_client_id`: `nemesisprime_gs_voyager2015` (Decepticon Tactician,
  9.2.0 pack)
- `fallback_label`: `[ASSUMED] not original`
- `fallback_reason`: same-faction/same-class Tactician fallback for data
  experiments only.

`data/boss_map.json`, `data/boss_gaps.json` and
`server/data/quest_list.json` (`bossFallback` key) carry the fallback. The
original `finalBoss` remains null for those 9 quests, so the client/UI can
still show the gap. `bossFallback` is not copied into `finalBoss` and must not
be reported as the retail boss.

## Quests

`story_act1_ch1_m2`, `story_act1_ch3_m5`, `story_act1_ch4_m4`,
`story_act2_ch1_m3`, `story_act2_ch2_m3`, `story_act2_ch3_m5`,
`story_act3_ch1_m6`, `story_act4_ch2_m5`, `awaken_ch2_m5`.

## 4.2/4.3

- The bio/pack/wiki matrix is in `docs/bot_matrix.md`; the 5 wiki pages without
  a 9.2.0 pack are Starscream, Chromia, Dead End, Optimus Prime (base page),
  Soundblaster/Tactician.
- `bumblebee_cin_dotm` (character id) now has a blueprint alias
  `bumblebee_cin_dotm_2`; 3 quests were corrected.
- `id_map.json` is unchanged for Starscream because there is no client id; the
  fallback is separate and labelled `[ASSUMED]`.
