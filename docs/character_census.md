# Character census (Step 1) - 61 client characters

Status: **complete for the retained 9.2.0 client assets.** Built with local
UnityPy 1.25.4 over `work/unpacked/assets`; no system tools and no client
patches. Machine-readable result: `data/client_character_census.json`.

## Counts `[STATIC]`

| item | count | evidence |
|---|---:|---|
| base character tokens | **61** | all `toc.txt` + 59 `*_odr` bundles + merged `characters.assetbundle` |
| character tokens incl. `_lw` | **122** | `work/census_raw.json` |
| `_lw` variants | **61** | one per base character |
| ODR bot bundles | **59** | `assetpack/<id>_odr/<id>.assetbundle` |
| merged-only prefabs | **2** | `optimusprime_gs_v, starscream_gs` in `characters.assetbundle` |
| effective catalog blueprints | **62** | `bcg_login_data.json` + `starscream_patch.json` |
| effective catalog characters | **61** | one stale `optimus_c_tf`, see gaps |
| effective roster | **60** | 59 original + Starscream patch |
| wiki pages matched | **41** | `data/wiki/bots.json` |
| move TextAssets | **923** | `assetpack/characters/moves.assetbundle` |
| boss quests with a client id | **90 / 90** | `data/boss_map.json` |

The old "59 bot packs" denominator was **undercounted by the two merged
prefabs** (`starscream_gs`, `optimusprime_gs_v`). The correct base count is
**61**, and the BOTS denominator must come from the catalog roster, not the
number of ODR directories.

## Token map

`loc_token` is the token used by `ID_CHARACTER_BIOS_<token>` and
`ID_SPECIAL_ATTACK_<token>_<n>`; it is not always the asset id. Portrait
tokens are lower-case and sometimes differ (`THUNDER_GS` portrait vs
`THUNDERCRACKER_GS` strings).

| # | client id | loc token | bio | spec | portrait | wiki page | class | catalog | boss quests |
|---:|---|---|---|---|---|---|---|---:|---:|
| 1 | `arcee_gs_deluxe2014` | `ARCEE_GS` | yes | yes | yes | Arcee | Warrior | yes | 2 |
| 2 | `barricade_cin_dotm` | `BARRI_C` | yes | yes | yes | Barricade | Scout | yes | 5 |
| 3 | `blaster_gs_leader2016` | `BLASTR_GS` | yes | yes | yes | Blaster |  | yes | 2 |
| 4 | `bludgeon_gs_rd20` | `BLUDGE_GS` | yes | yes | yes | Bludgeon | Warrior | yes | 4 |
| 5 | `bonecrusher_cin_rotf` | `BONEC_C` | yes | yes | yes | Bonecrusher | Warrior | yes | 5 |
| 6 | `bumblebee_cin_dotm` | `BUMBL_C` | yes | yes | yes | Bumblebee (DOTM) |  | yes | 0 |
| 7 | `bumblebee_gs_kabam` | `BUMBL_GS` | yes | yes | yes | Bumblebee | Scout | yes | 0 |
| 8 | `cheetor_bw_transmetal` | `CHEETOR_BW` | yes | yes | yes | Cheetor |  | yes | 2 |
| 9 | `cliffjumper_gs_kabam` | `CLIFFJUMP_GS` | yes | yes | yes | Cliffjumper | Demolitions | yes | 0 |
| 10 | `cyclonus_gs_uw06` | `CYCLON_GS` | yes | yes | yes | Cyclonus |  | yes | 0 |
| 11 | `dinobot_bw_kabam` | `DINOB_BW` | yes | yes | yes | Dinobot |  | yes | 0 |
| 12 | `dirge_gs_deluxe2008` | `DIRGE_GS` | **no** | **no** | yes | Dirge |  | yes | 0 |
| 13 | `drift_cin_aoe` | `DRIFT_C` | yes | yes | yes | Drift | Warrior | yes | 0 |
| 14 | `galvatron_gs_voyager2016` | `GALVATRON_GS` | yes | yes | yes | Galvatron | Demolitions | yes | 0 |
| 15 | `grimlock_gs_mp08` | `GRIML_GS` | yes | yes | yes | Grimlock |  | yes | 2 |
| 16 | `grindor_cin_rotf` | `GRIND_C_ROTF` | yes | yes | yes | Grindor |  | yes | 2 |
| 17 | `hotrod_cin_tlk` | `HOTRO_C` | yes | yes | yes | Hot Rod | Warrior | yes | 1 |
| 18 | `hound_cin_tlk` | `HOUND_C` | yes | yes | yes | Hound | Warrior | yes | 1 |
| 19 | `ironhide_cin_rotf` | `IRONH_C_ROTF` | yes | yes | yes | Ironhide (ROTF) | Demolitions | yes | 3 |
| 20 | `ironhide_gs_kabam` | `IRONH_GS` | **no** | **no** | yes | Ironhide | Brawler | yes | 0 |
| 21 | `jazz_gs_twm05` | `JAZZ_GS` | yes | yes | yes | Jazz | Scout | yes | 0 |
| 22 | `jetfire_gs_leader2014` | `JETFIRE_GS` | yes | yes | yes | Jetfire | Tech | yes | 2 |
| 23 | `kickback_gs_kabam` | `KICKB_GS` | yes | yes | yes | Kickback |  | yes | 1 |
| 24 | `megatron_cin_rotf` | `MEGAT_C` | yes | yes | yes | Megatron (ROTF) | Demolitions | yes | 3 |
| 25 | `megatron_gs_leader2015` | `MEGAT_GS` | yes | yes | yes | Megatron | Tactician | yes | 1 |
| 26 | `megatronus_gs_kabam` | `MEGATRO_GS` | yes | yes | yes | Megatronus |  | yes | 4 |
| 27 | `mirage_gs_deluxe2016` | `MIRAG_GS` | yes | yes | yes | Mirage | Tech | yes | 4 |
| 28 | `mixmaster_cin_rotf` | `MIXMA_C_ROTF` | yes | yes | yes | Mixmaster | Demolitions | yes | 1 |
| 29 | `motormaster_gs_voyager2015` | `MOTORM_GS` | yes | yes | yes | Motormaster | Brawler | yes | 5 |
| 30 | `necrotronus_gs_kabam` | `NECROTRO_GS` | yes | yes | yes | Necrotronus | Warrior | yes | 1 |
| 31 | `nemesisprime_gs_voyager2015` | `NEMESIS_GS` | yes | yes | yes | Nemesis Prime | Tactician | yes | 2 |
| 32 | `optimusprimal_bw_mp32` | `OPRIMAL_BW` | yes | yes | yes | Optimus Primal |  | yes | 0 |
| 33 | `optimusprime_cin_tf` | `OPTIMUS_C_TF` | yes | yes | yes | Optimus Prime (MV1) | Brawler | yes | 1 |
| 34 | `optimusprime_gs_v` | `OPTIMUS_GS` | yes | yes | yes | Optimus Prime | Tactician | **no** | 0 |
| 35 | `prowl_gs_deluxe2016` | `PROWL_GS` | yes | yes | yes | Prowl | Scout | yes | 1 |
| 36 | `ramjet_gs_deluxe2008` | `RAMJET_GS` | yes | yes | yes | Ramjet | Demolitions | yes | 0 |
| 37 | `ratchet_gs_kabam` | `RATCH_GS` | yes | yes | yes | Ratchet |  | yes | 1 |
| 38 | `rhinox_gs_voyager2014` | `RHINO_BW` | yes | yes | yes | Rhinox | Tech | yes | 3 |
| 39 | `rodimusprime_gs_mp09` | `RODIMUS_GS` | **no** | **no** | yes | Rodimus Prime | Tactician | yes | 0 |
| 40 | `scorponok_bw_kabam` | `SCORPO_BW` | yes | yes | yes | Scorponok | Warrior | yes | 0 |
| 41 | `sharkticon_gs_brawler` | `SHARK_BRAW` | yes | yes | yes | Sharkticon |  | yes | 1 |
| 42 | `sharkticon_gs_demolition` | `SHARK_DEMO` | yes | yes | yes | Sharkticon |  | yes | 2 |
| 43 | `sharkticon_gs_kabam` | `SHARK_GOLD` | yes | yes | yes | Sharkticon |  | yes | 0 |
| 44 | `sharkticon_gs_scout` | `SHARK_SCOU` | yes | yes | yes | Sharkticon |  | yes | 1 |
| 45 | `sharkticon_gs_tactician` | `SHARK_TACT` | yes | yes | yes | Sharkticon |  | yes | 0 |
| 46 | `sharkticon_gs_tech` | `SHARK_TECH` | yes | yes | yes | Sharkticon |  | yes | 0 |
| 47 | `sharkticon_gs_warrior` | `SHARK_WARR` | yes | yes | yes | Sharkticon |  | yes | 1 |
| 48 | `shockwave_gs` | `SHOCK_C` | yes | yes | yes | Shockwave | Tech | yes | 2 |
| 49 | `sideswipe_gs` | `SIDES_GS` | yes | yes | yes | Sideswipe | Scout | yes | 3 |
| 50 | `skywarp_gs_leader2015` | `SKYWARP_GS` | **no** | **no** | yes | Skywarp | Scout | yes | 0 |
| 51 | `slipstream_gs` | `SLIPSTREAM_GS` | **no** | **no** | yes | Slipstream | Scout | yes | 0 |
| 52 | `soundblaster_gs_mp13b` | `SOUNDBLAST_GS` | **no** | **no** | yes | Soundblaster | Demolitions | yes | 0 |
| 53 | `soundwave_gs` | `SOUND_GS` | yes | yes | yes | Soundwave |  | yes | 3 |
| 54 | `starscream_gs` | `STARS_GS` | yes | yes | yes | Starscream | Tactician | yes | 9 |
| 55 | `sunstreaker_gs_deluxe2008` | `SUNSTREAK_GS` | **no** | **no** | yes | Sunstreaker | Brawler | yes | 0 |
| 56 | `tantrum_gs_kabam` | `TANTRUM_GS` | yes | yes | yes | Tantrum | Brawler | yes | 1 |
| 57 | `thundercracker_gs_leader2015` | `THUNDERCRACKER_GS` | yes | yes | yes | Thundercracker | Brawler | yes | 2 |
| 58 | `ultramagnus_gs_leader` | `ULTRAM_GS` | yes | yes | yes | Ultra Magnus | Tactician | yes | 1 |
| 59 | `waspinator_gs_deluxe` | `WASP_BW` | yes | yes | yes | Waspinator | Demolitions | yes | 1 |
| 60 | `wheeljack_gs_mp20` | `WHEELJ_GS` | yes | yes | yes | Wheeljack | Tech | yes | 0 |
| 61 | `windblade_gs` | `WINDB_GS` | yes | yes | yes | Windblade | Warrior | yes | 0 |

Full per-character data (prefab path, bundle, move names, animation clips,
portrait paths, bio/spec keys) is in `data/client_character_census.json`.

## Characters without client name/description strings `[STATIC]`

These have a character token and move data, but the localization dump has
no `ID_SPECIAL_ATTACK_<token>_*` and no `ID_CHARACTER_BIOS_<token>`:

- `dirge_gs_deluxe2008` / `DIRGE_GS` - portrait and moves exist, no strings.
- `ironhide_gs_kabam` / `IRONH_GS` - portrait and moves exist, no strings.
- `rodimusprime_gs_mp09` / `RODIMUS_GS` - portrait and moves exist, no strings.
- `skywarp_gs_leader2015` / `SKYWARP_GS` - portrait and moves exist, no strings.
- `slipstream_gs` / `SLIPSTREAM_GS` - portrait and moves exist, no strings.
- `soundblaster_gs_mp13b` / `SOUNDBLAST_GS` - portrait and moves exist, no strings.
- `sunstreaker_gs_deluxe2008` / `SUNSTREAK_GS` - portrait and moves exist, no strings.

Consequence: the UI would show the `MS_` missing-string marker for their
special attacks/bio unless a server localization table is added. This is a
client data gap, not a key-name mistake. Do not invent strings as retail.

## Wikipedia-only pages

| page | status | evidence |
|---|---|---|
| Chromia | **not in 9.2.0 client** | wiki release 2023-05-10; no `CHROMIA`/`CHROM` token, filename or bundle match |
| Dead End | **not in 9.2.0 client** | wiki release 2023-05-10; no `DEADEND`/`DEAD END` token, filename or bundle match |
| Optimus Prime | **found** | `optimusprime_gs_v` / `OPTIMUS_GS` merged prefab; wiki Tactician, rank/level 1/1 6240/444; absent from the 59-pack catalog |
| Soundblaster/Tactician | **partial** | client has `soundblaster_gs_mp13b` (Demolitions) and `SOUNDBLAST_GS` portrait; no separate Tactician blueprint |
| Starscream | **found** | `starscream_gs` + `starscream_gs_lw` in `characters/toc.txt`; `Starscream_GS` in `characters.assetbundle`; wiki Tactician 5400/391/1354 |

## Catalog gaps and oddities

- `optimusprime_gs_v` (Tactician, 6240/444) is in the client and wiki but
  **absent from the 59-pack catalog**. The census adds it to
  `bot_catalog_real.json` and `id_map.json`; it still needs a catalog
  blueprint/roster entry (Step 2/3).
- `optimus_c_tf` exists in `characters` with only the `optimus_c_tf_t3`
  blueprint and no matching character bundle; portraits exist. It is a
  stale/duplicate entry. Do not delete it blindly; it may be referenced by
  an old roster row.
- `starscream_gs` is in the client and wiki; `starscream_patch.json` adds it
  to blueprints/characters/heroes/roster at load time.
- 13 non-shark client ids have wiki pages but no stat table in the saved
  page set; 7 sharkticon variants use NPC tokens. See
  `data/wiki/client_only.json`.

## BOTS grid implication

- Effective roster is 60 (59 original + Starscream). The client shows 59
  cards and does not show Starscream, so the grid is not simply
  `userData.heroes`; Step 2 must find the list source.
- After adding Optimus Prime (`optimusprime_gs_v`), the intended base roster
  is 61. The sweep denominator must be read from the effective catalog, not
  hard-coded to 59.

## Assets scanned

- `work/unpacked/assets/**/toc.txt`: 108 files, 122 merged character tokens.
- `work/unpacked/assets/assetpack/*_odr/*.assetbundle`: 59 bot bundles;
  main `characters.assetbundle` holds Starscream and Optimus GS.
- `assetpack/characters/moves.assetbundle`: 923 TextAssets; every one of the
  61 base characters has at least one special move.
- Portraits: 360 files, 161 tokens (including relics/UI);
  `work/localization_all.json`: 7869 keys, 89 bios, 65 special-attack tokens.

## Labels

- `[STATIC]` asset/toc/bundle/localization structure and paths.
- `[WIKI]` class/faction/release/stat rows.
- `[RUN]` only where the catalog was exercised live; the census itself is
  static.
