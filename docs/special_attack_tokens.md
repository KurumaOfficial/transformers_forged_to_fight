# Special-attack and bio localization tokens (Step 3)

Status: **static key/token map complete; on-screen verification is blocked by
the BOTS card/user-data binding gap (see `docs/bots_grid.md`).**

## Key builder `[STATIC]`

`BCGHelper.GetSpecialAttackNameLocString` (`0xC1B154`) and
`GetSpecialAttackDescriptionLocString` (`0xC1B21C`):

1. take the blueprint id string;
2. `LastIndexOf("_")`;
3. `Substring(0, index)` and `ToUpperInvariant()`;
4. concatenate `ID_SPECIAL_ATTACK_` (or `ID_SPECIAL_ATTACK_DESCRIPTION_`)
   + token + `_` + attack index.

So a blueprint id must be **`<loc_token>_<suffix>`** to produce
`ID_SPECIAL_ATTACK_<loc_token>_<n>`. Example: `windb_gs_2` ->
`ID_SPECIAL_ATTACK_WINDB_GS_0`. The current catalog uses asset ids such as
`windblade_gs`, which produce `ID_SPECIAL_ATTACK_WINDBLADE_0` and miss the
retained strings.

## Token table

| client id | loc token | special names | bio | note |
|---|---|---|---|---|
| `arcee_gs_deluxe2014` | `ARCEE_GS` | yes | yes |  |
| `barricade_cin_dotm` | `BARRI_C` | yes | yes |  |
| `blaster_gs_leader2016` | `BLASTR_GS` | yes | yes |  |
| `bludgeon_gs_rd20` | `BLUDGE_GS` | yes | yes |  |
| `bonecrusher_cin_rotf` | `BONEC_C` | yes | yes |  |
| `bumblebee_cin_dotm` | `BUMBL_C` | yes | yes |  |
| `bumblebee_gs_kabam` | `BUMBL_GS` | yes | yes |  |
| `cheetor_bw_transmetal` | `CHEETOR_BW` | yes | yes |  |
| `cliffjumper_gs_kabam` | `CLIFFJUMP_GS` | yes | yes |  |
| `cyclonus_gs_uw06` | `CYCLON_GS` | yes | yes |  |
| `dinobot_bw_kabam` | `DINOB_BW` | yes | yes |  |
| `dirge_gs_deluxe2008` | `DIRGE_GS` | **no** | **no** | missing client strings |
| `drift_cin_aoe` | `DRIFT_C` | yes | yes |  |
| `galvatron_gs_voyager2016` | `GALVATRON_GS` | yes | yes |  |
| `grimlock_gs_mp08` | `GRIML_GS` | yes | yes |  |
| `grindor_cin_rotf` | `GRIND_C_ROTF` | yes | yes |  |
| `hotrod_cin_tlk` | `HOTRO_C` | yes | yes |  |
| `hound_cin_tlk` | `HOUND_C` | yes | yes |  |
| `ironhide_cin_rotf` | `IRONH_C_ROTF` | yes | yes |  |
| `ironhide_gs_kabam` | `IRONH_GS` | **no** | **no** | missing client strings |
| `jazz_gs_twm05` | `JAZZ_GS` | yes | yes |  |
| `jetfire_gs_leader2014` | `JETFIRE_GS` | yes | yes |  |
| `kickback_gs_kabam` | `KICKB_GS` | yes | yes |  |
| `megatron_cin_rotf` | `MEGAT_C` | yes | yes |  |
| `megatron_gs_leader2015` | `MEGAT_GS` | yes | yes |  |
| `megatronus_gs_kabam` | `MEGATRO_GS` | yes | yes |  |
| `mirage_gs_deluxe2016` | `MIRAG_GS` | yes | yes |  |
| `mixmaster_cin_rotf` | `MIXMA_C_ROTF` | yes | yes |  |
| `motormaster_gs_voyager2015` | `MOTORM_GS` | yes | yes |  |
| `necrotronus_gs_kabam` | `NECROTRO_GS` | yes | yes |  |
| `nemesisprime_gs_voyager2015` | `NEMESIS_GS` | yes | yes |  |
| `optimusprimal_bw_mp32` | `OPRIMAL_BW` | yes | yes |  |
| `optimusprime_cin_tf` | `OPTIMUS_C_TF` | yes | yes |  |
| `optimusprime_gs_v` | `OPTIMUS_GS` | yes | yes |  |
| `prowl_gs_deluxe2016` | `PROWL_GS` | yes | yes |  |
| `ramjet_gs_deluxe2008` | `RAMJET_GS` | yes | yes |  |
| `ratchet_gs_kabam` | `RATCH_GS` | yes | yes |  |
| `rhinox_gs_voyager2014` | `RHINO_BW` | yes | yes |  |
| `rodimusprime_gs_mp09` | `RODIMUS_GS` | **no** | **no** | missing client strings |
| `scorponok_bw_kabam` | `SCORPO_BW` | yes | yes |  |
| `sharkticon_gs_brawler` | `SHARK_BRAW` | yes | yes |  |
| `sharkticon_gs_demolition` | `SHARK_DEMO` | yes | yes |  |
| `sharkticon_gs_kabam` | `SHARK_GOLD` | yes | yes |  |
| `sharkticon_gs_scout` | `SHARK_SCOU` | yes | yes |  |
| `sharkticon_gs_tactician` | `SHARK_TACT` | yes | yes |  |
| `sharkticon_gs_tech` | `SHARK_TECH` | yes | yes |  |
| `sharkticon_gs_warrior` | `SHARK_WARR` | yes | yes |  |
| `shockwave_gs` | `SHOCK_C` | yes | yes |  |
| `sideswipe_gs` | `SIDES_GS` | yes | yes |  |
| `skywarp_gs_leader2015` | `SKYWARP_GS` | **no** | **no** | missing client strings |
| `slipstream_gs` | `SLIPSTREAM_GS` | **no** | **no** | missing client strings |
| `soundblaster_gs_mp13b` | `SOUNDBLAST_GS` | **no** | **no** | missing client strings |
| `soundwave_gs` | `SOUND_GS` | yes | yes |  |
| `starscream_gs` | `STARS_GS` | yes | yes |  |
| `sunstreaker_gs_deluxe2008` | `SUNSTREAK_GS` | **no** | **no** | missing client strings |
| `tantrum_gs_kabam` | `TANTRUM_GS` | yes | yes |  |
| `thundercracker_gs_leader2015` | `THUNDERCRACKER_GS` | yes | yes |  |
| `ultramagnus_gs_leader` | `ULTRAM_GS` | yes | yes |  |
| `waspinator_gs_deluxe` | `WASP_BW` | yes | yes |  |
| `wheeljack_gs_mp20` | `WHEELJ_GS` | yes | yes |  |
| `windblade_gs` | `WINDB_GS` | yes | yes |  |

## Bots with no client strings (7) `[STATIC]`

These have a token, portrait and move data, but no
`ID_SPECIAL_ATTACK_<token>_*` and no `ID_CHARACTER_BIOS_<token>` in the
localization dump:

- `dirge_gs_deluxe2008` / `DIRGE_GS`
- `ironhide_gs_kabam` / `IRONH_GS`
- `rodimusprime_gs_mp09` / `RODIMUS_GS`
- `skywarp_gs_leader2015` / `SKYWARP_GS`
- `slipstream_gs` / `SLIPSTREAM_GS`
- `soundblaster_gs_mp13b` / `SOUNDBLAST_GS`
- `sunstreaker_gs_deluxe2008` / `SUNSTREAK_GS`

Do not invent retail strings for these. A server localization table could
fill them as `[ASSUMED]`, but the client's `LocalizationManager` reads
`LoginManager._loginData`, which is empty in the current flow (see
`docs/level_lock.md`).

## Token aliases found

- Bumblebee G1: `BUMBL_GS` (spec/bio) plus alternate `BUMBLE_GS` bio.
- Dinobot: `DINOB_BW` (bio) and `DINOB_GS` (some spec keys).
- Mixmaster: `MIXMA_C_ROTF` and `MIXMA_GS`.
- Thundercracker: portrait token `thunder_gs`, strings token
  `THUNDERCRACKER_GS`.
- Cyclonus: portrait typo `clyclon_gs` plus `cyclon_gs`.
- Sharkticons: `SHARK_*` plus `NPC_SHARK_*`; `SHARK_GOLD2` has no
  catalog id (candidate unused/event variant).

## What is not proven

- The exact UI request for each screen after the card is selected; the
  current INFO/UPGRADE screen shows 0 HP/0 ATK, so the abilities panel was
  not reachable for a clean screenshot.
- A server `loc`/`XlateManager` override accepted by the client.
