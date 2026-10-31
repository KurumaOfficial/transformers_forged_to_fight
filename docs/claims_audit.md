# Claims audit (Step 0)

Status of important claims made during the project. A claim is "confirmed"
only when the linked evidence still holds; "corrected" means the original
statement was wrong or too strong; "open" means it is not proven and needs a
specific check.

Labels: `[RUN]` executed/observed, `[STATIC]` code/data, `[DERIVED]` computed,
`[ASSUMED]` guess. Sources: `[CLIENT]`, `[WIKI]`, `[RUN]`.

| # | Claim | Date | Status | Evidence / what was checked | Needed if open |
|---:|---|---|---|---|---|
| 1 | Prefight `_model` is null and `PreFightScreen.OnFight` throws NRE | 2026-10-24 | **corrected** | Earlier `latest.json` had `nre_prefight_model=true`; after team/active-team fixes, `[RUN]` smoke has `nre_prefight_model=false` and reaches `activate-match`. `tests/smoke/latest.json`, `docs/battle_started.md` | — |
| 2 | The quest team wire format is an array / a plain list | 2026-10-24 | **corrected** | `[STATIC]` `QuestUserInfo.team` is a dictionary (`Dot.Object 0x103D5D8`); `activeTeams` is a dictionary keyed by `aid`; `teamData` is a BCG wrapper. `spec/quest_protocol.md`, `spec/bcg_userdata.md` | — |
| 3 | `FuseODRBlocker` blocks battle input | 2026-10-26 | **corrected** | The battle is visible and swipes increment HITS while the blocker object still exists with 0 downloads. `[RUN]` `work/f1.png`, `work/b2.png`; `docs/odr_report.md` 2026-10-29 | — |
| 4 | The ODR blocker is an arena/tag/bundle problem | 2026-10-26 | **corrected** | Arena `karnak` valid; `sideswipe_gs.assetbundle` present; blocker was global on `HeroesScreen`; PlayCore `com.android.vending` missing. `[RUN]`/`[STATIC]` `docs/odr_flow.md` | — |
| 5 | Normal `ODRManager.Initialize` starts `InitAndGetManifest` | 2026-10-26 | **corrected** | Normal Initialize does not call it; `EnsureManifest -> WaitForTOC -> ODRAPI.GetManifest` is lazy. `[STATIC]` `docs/odr_flow.md` | — |
| 6 | There are no original client Buff/statMod ids or triggers | 2026-10-26 | **open** | Client metadata has many `ID_STAT_*`/`D_STAT` keys and type factories, but no per-bot catalog was found yet. `[STATIC]` `stringliteral.json`; `docs/ability_blocker.md` | Step 2: enumerate `ID_STAT_*`, factories, assets; map wiki effects |
| 7 | The battle is fully client-side | 2026-10-26 | **partially confirmed** | Combat, hit/damage, death are local; only activate/resolve are server calls. `[STATIC]` `MatchManager`, `BattleArbiter`; `[RUN]` only activate observed | Confirm post-battle server keys after damage works |
| 8 | `Tags` caused `PlayerAttributes.Init` NRE | 2026-10-26 | **corrected** | Root cause was `BaseRangedDamageType`; `Tags` at `+0xB8` was a red herring. `[STATIC]` `docs/battle_init_fix.md` | — |
| 9 | Hidden stats are recalculated from catalog/growth tables | 2026-10-26 | **corrected** | Player quest stats come from the quest team / activeTeam payload; rank/growth extras are not copied by `0xA60FC8/0xA61018`. `[STATIC]`+`[RUN]` `spec/attribute_pipeline.md` | Per-bot values from wiki/retail |
| 10 | `getBaseHeroData` drives the player's battle attributes | 2026-10-26 | **corrected** | No player `getBaseHeroData` request; only enemy requests. Player HP/ratings came from active-team details. `[RUN]` `server/requests.jsonl` | — |
| 11 | Player `/bcg/getBaseHeroData` flat Armor/Crit/Block/Mana are applied | 2026-10-26 | **corrected** | They were inert; adding them to the quest team payload made them live (50/0.1/1.5/0.5/1.0). `[RUN]` `work/dump_fighter_attrs.py` | — |
| 12 | HP=1.0 means the server max HP was not applied | 2026-10-26 | **corrected** | HP is a current/sentinel field; `HPMax` 1050 was applied. `[RUN]` `docs/battle_memory_values.md` | — |
| 13 | Rating is a function of HP and Attack only | 2026-10-26 | **corrected** | Client formula includes weights, extra, mod; LP is infeasible on raw HP/ATK. `[STATIC]`+`[DERIVED]` `spec/rating_formula.md`, `data/rating_lp.json` | Retail `HeroRatingHP/Attack` split |
| 14 | `match-loaded` is required for a quest fight | 2026-10-26 | **open** | Never observed for `quests_fight`; whether PvP-only is unknown. `[RUN]` `server/requests.jsonl`; `spec/match_protocol.md` | Observe a working quest resolve or PvP capture |
| 15 | `FuseODRBlocker` state 4/Open is a permanent global blocker | 2026-10-26 | **corrected** | Object is open with 0 downloads, but no overlay covers `BattleArbiterMainState`; input works. `[RUN]` `docs/odr_report.md` | — |
| 16 | Starscream is in 9.2.0 | 2026-10-26 | **corrected** | No 9.2.0 pack; 9 boss gaps; fallback only `[ASSUMED]` `nemesisprime_gs_voyager2015`. `[RUN]`/`[STATIC]` `docs/starscream_fallback.md` | Later APK/pack |
| 17 | S1 is 12/59 | 2026-10-24 | **corrected** | `sweep_bots59.py` now 59/59, 0 `info_error`, 0 NRE. `[RUN]` `tests/sweep/sweep_59.json`, `docs/sweep_diagnosis.md` | — |
| 18 | 90/90 maps pass the 3x3 rule | 2026-10-26 | **confirmed** | `data/map_validation.json`, `docs/map_validity.md`; 0 failures | — |
| 19 | Special-attack key is `M1_SPECIAL_ATTACK_<BOT>.<n>` | 2026-10-26 | **partially corrected** | Windblade shows raw `MS_ID_SPECIAL_ATTACK_WINDBLADE_0..2`; another bot used `M1_SPECIAL_ATTACK_*`. `[RUN]` `tests/smoke/10b_bot_info.png`; `docs/special_attack_localization.md` | Per-bot move/loc table |
| 20 | `class_power=0` is the zero-damage cause | 2026-10-29 | **open / disproved as sole cause** | Live ClassPower is 1.0 after adding `class_power`, but `_attack.Get()` is still 0 and Damage 0. `[RUN]` `work/dump_pa_fighters.py` | Step 1: safe-value init/commit |
| 21 | Only `basic_melee` is needed in `attackValues` | 2026-10-29 | **corrected** | `AttackLevel` maps to `Light/Medium/Heavy/...`; `BCGAttackValue` reads literal `attack_percent`. `[STATIC]`+`[RUN]` `spec/attribute_pipeline.md` | Retail percentages |
| 22 | Content-timeline timestamps are first releases | 2026-10-26 | **corrected** | They are saved wiki revision timestamps; 131 post-APK, 53 after close. `[WIKI]`/`[DERIVED]` `docs/content_timeline.md` | First-revision history |
| 23 | The rating split in `data/rating_table.json` is retail | 2026-10-26 | **corrected** | Equivalent proportional `[DERIVED]` split reproduces the client formula; not original. `[DERIVED]` `spec/rating_formula.md` | Original server split |
| 24 | A Play Store image would fix ODR | 2026-10-26 | **open / untested** | Permission empty; only plan. PlayCore may still need an account/licence. `[ASSUMED]` `docs/playstore_image_plan.md` | User permission + AVD test |
| 25 | The 34 wiki images are available via Wayback | 2026-10-26 | **open** | Three attempts returned 404/503. `[RUN]` `docs/wiki_images_wayback.md` | Another source |
| 26 | No client code/data was patched and no Frida/gadget used | 2026-10-29 | **confirmed** | All changes are server data/routes/docs; probes are read-only `/proc/pid/mem`. `[RUN]` git log; `docs/hook_audit.md` | — |
| 27 | ODR manifest is not requested because the bundle exists | 2026-10-26 | **open** | Lazy path not started; exact trigger unproven. `[STATIC]` `docs/odr_flow.md` | Runtime caller/debug trace (not allowed without consent) |
| 28 | The `setSavedTeam`/quest `teamData` wrapper format is correct | 2026-10-24 | **confirmed** | `[RUN]` team/active-team fix reaches prefight and activate-match; `spec/bcg_userdata.md` | — |
| 29 | `Damage=0` is caused by ODR | 2026-10-29 | **corrected** | ODR overlay is not covering Main; `_attack.Get()=0` while display 115. `[RUN]` `docs/odr_report.md`, `spec/attribute_pipeline.md` | Step 1 |
| 30 | `HitResultFlags=129` means block/miss/invulnerable | 2026-10-29 | **open / needs enum decode** | 129 = 0x81 = `Hit` (1) + `LastHit` (128); block/miss/invulnerable bits are not set. `[STATIC]` `dump.cs` | Confirm in Step 1.6 |

## Open items that matter now

1. **#6** buff/statMod catalog — Step 2.
2. **#14** match-loaded — only after a working resolve.
3. **#20/#29** zero damage — Step 1; highest priority.
4. **#24** Play Store image — not allowed, plan only.
5. **#27** manifest trigger — no debugger allowed; static only.

## Rule for new claims

Every new `[RUN]`/`[STATIC]` claim must link a file in `docs/`, `spec/`,
`tests/`, or `work/`; otherwise it stays `[ASSUMED]`.

## 2026-10-29 late corrections (damage)

| # | Claim | Status | Evidence / needed |
|---:|---|---|---|
| 31 | `PlayerAttributes._attack.Get()` is 0 while `_value` is 115 | **corrected** | The safe value is **115**; the earlier read treated an IL2CPP byte[] data pointer as a pointer, but elements are inline at `+0x20`. `work/dump_defense.py` shows hash OK, safe=115. |
| 32 | Zero damage is a client stat commit issue | **corrected** | Zero was `ArmorRatingConstant=0`; `GetArmorDR` gave 100% reduction. `docs/damage_pipeline.md`. |
| 33 | `TuningGameplay` defaults are 0 | **corrected** | Code defaults are 300/200/111; they are overwritten by `TuningGameplay.OnConfigChanged` with the `bcg-combat` config. Missing config left 0. |
| 34 | A `bcg-combat` config with `armor_break=200` fixes damage | **confirmed [RUN]** | Live `ArmorRatingConstant=200`; player hit 80.5 raw, 64.4 after armor; enemy HP dropped. |
| 35 | Death/K.O. -> resolve -> map works | **confirmed [RUN]** | Loss and win both sent `/matches/resolve-match/quests_fight` and returned to map; `docs/evidence/post_battle_2026-10-29/`. |
| 36 | Rewards/results screen works after a win | **open** | Win returned to map without rewards/cleared tile; current `match_resolve_response.json` lacks the accepted progression/async payload. |
| 37 | ODR blocks combat input | **corrected** | Battle visible/controllable; resolve observed. |
| 38 | `attackValues`/`attack_percent` are needed for basic damage | **confirmed [RUN]** | `DamageRating=0.7`; raw damage 80.5. |
| 39a | Normal player can kill the enemy without test data (earlier note) | **superseded** | See row 39 at the end of the late-corrections table; the normal win was later confirmed. |

## 2026-10-29 late correction: stat/localization keys exist

| # | Claim | Status | Evidence |
|---:|---|---|---|
| 40 | There are no original `ID_STAT_*`/`D_STAT`/special-attack keys | **corrected** | `work/localization_all.json`: 3307 `ID_STAT_*`, 8 `D_STAT*`, 390 `ID_SPECIAL_ATTACK_*` (65 bot/move tokens). They are localization keys, not numeric definitions. `spec/buff_catalog.md`. |
| 41 | Windblade special-attack names exist | **corrected** | No `ID_SPECIAL_ATTACK_WINDBLADE_*`; live raw `MS_ID_SPECIAL_ATTACK_WINDBLADE_0..2`. |
| 42 | The localization table can be extended from the server | **open** | Not proven; need Xlate/snapshot/override analysis and a live test. |

| 39 | Normal player can kill the enemy without test data | **confirmed [RUN]** | `battle_step.py` normal win: player HP 300.2, enemy HP 0, player damage 1069.5. `resolve_win_normal.json`. |

## 2026-10-30 late corrections (localization, UI, routing)

| # | Claim | Date | Status | Evidence / what was checked | Needed if open |
|---:|---|---|---|---|---|
| 43 | `LocalizationManager.Async` handles `loc-cache-update` | 2026-10-30 | **confirmed [STATIC]** | `0x127A050` compares the lowercased message with metadata string index 18474 (`loc-cache-update`); calls `loadLocData` (`0x1279C8C`). | — |
| 44 | The server can override localization via `loc-cache-update` | 2026-10-30 | **corrected / negative [RUN]** | Sent the async with components `localization`, `LocalizationManager`, `localizationmanager`, `loc`; BOTS label unchanged, no loc error. | Exact async component registration or a working Xlate2 category |
| 45 | `Xlate2` downloads `xlate2Resources` from `/cdn` | 2026-10-30 | **open / negative [RUN]** | `XlateManager.Connect` (`0x1593888`) calls `updateStringsFromCDN`; changing `xlate2Resources` to a direct array produced no `/cdn`/`xlate` request. Reverted. | Xlate2 enable flag and exact resource URL |
| 46 | BCG builders can be extracted without wire changes | 2026-10-30 | **confirmed offline [RUN]** | `server/routes/bcg.py`; `work/test_bcg_split.py` PASS (HP 1050, ATK 115, rating 162, weak enemy, wrapper). | Live smoke after server restart |
| 47 | Windblade UI stats match the wiki | 2026-10-30 | **partially confirmed [RUN]/[WIKI]** | HP 826 and ATK 102 match the star-1 infobox; rating 300 vs wiki 264. | Retail rating split |
| 48 | The catalog stats/ratings are retail | 2026-10-30 | **corrected** | Bumblebee/Sideswipe live 1050/115 vs wiki 1/1 4860/444 and 5160/520; `docs/rating_ui_check.md`. | Retail per-bot rank/level/star tables |
| 49 | Adding `user.levelrewards` unlocks the home LVL / STORE | 2026-10-30 | **negative [RUN]** | Tried top-level and under `user`, with `level`/`Level`, after full restart; home stayed `LVL 0`, STORE stayed locked. Live `LoginManager._loginData` is an empty Hashtable (count 0), so the field never reaches `LevelRewardsManager`. Reverted. `docs/level_lock.md`. | Trigger the level-rewards fetch or find who populates `_loginData` |
| 50 | The BCG route split preserves the wire | 2026-10-30 | **confirmed [RUN]** | `server/routes/bcg.py`; offline regression PASS and fast smoke PASS after server restart. | Full routing split still inline |

## 2026-10-30 v4.11 Step 0 corrections

| # | Claim | Status | Evidence |
|---:|---|---|---|
| 51 | Zero damage is caused by a client safe-value/commit bug | **corrected** | `TuningGameplay.ArmorRatingConstant` was 0 because `missionsconfig.configs["bcg-combat"]` was missing; `GetArmorDR` gave 100% reduction. Adding `armor_break=200` fixed damage. `[RUN]` `docs/damage_fix.md`, `docs/damage_pipeline.md`. |
| 52 | `PlayerAttributes._attack.Get()` is 0 while `_value` is 115 | **corrected** | The safe value is 115, hash OK. The earlier 0 was an IL2CPP `byte[]` decoding error: elements are inline at `+0x20`. `[RUN]` `work/dump_defense.py`, `docs/damage_fix.md`. |
| 53 | `FuseODRBlocker` blocks battle input | **corrected** | Battle is visible and controllable; the blocker object exists with 0 downloads but does not cover the HUD. `[RUN]` `docs/odr_report.md`, `work/f1.png`. |
| 54 | Starscream is post-APK content | **corrected** | Infobox release date `August 24, 2017`; the bot is pre-APK. The 9 missing boss ids/pack are a mapping/pack gap, not a release-date gap. `[WIKI]` `docs/content_release_dates.md`, `data/wiki/bots.json`. |

## 2026-10-30 v4.11 late corrections

| # | Claim | Status | Evidence |
|---:|---|---|---|
| 55 | The BOTS sweep visited 59/59 bots | **corrected / invalid metric** | sweep_bots59.py uses horizontal swipes; screenshots 	ests/sweep/page_01..04.png show the same first 12 cards (Windblade..Tantrum) on every page. The 59/59 info_error=0 rows are not proof of visiting 59 distinct bots. Use vertical scroll and rerun. |
| 56 | Starscream is absent from the client pack | **corrected** | work/unpacked/assets/characters/toc.txt lists starscream_gs; characters.assetbundle contains Starscream_GS; localization has ID_SPECIAL_ATTACK_STARS_GS_*; wiki page 5400/391/1354. Catalog patch added. |

## 2026-10-30 v4.12 Step 0 corrections

| # | Claim | Status | Evidence |
|---:|---|---|---|
| 57 | Starscream is absent in 9.2.0 | **corrected** | 61-base census: `starscream_gs` + `_lw` in `characters/toc.txt`, `Starscream_GS` in `characters.assetbundle`, `ID_SPECIAL_ATTACK_STARS_GS_0..2`, wiki 5400/391/1354. `[STATIC]` `data/client_character_census.json`, `docs/character_census.md`. |
| 58 | The client has 59 bot packages | **corrected / undercounted** | 59 ODR bundles + 2 merged prefabs (`starscream_gs`, `optimusprime_gs_v`) = **61 base characters**; 122 tokens with `_lw`; 108 TOCs, 102 assetbundles, 93 `_odr` dirs. `[STATIC]` `work/census_raw.json`, `work/bundle_inventory.json`. |
| 59 | BOTS 59/59 is the coverage denominator | **corrected** | 59 is the visible card count, not the catalog size: 61 characters, 60 effective roster, 61 after adding Optimus GS. The sweep denominator must come from the effective catalog/roster, and the report must list seen/missing ids. `[STATIC]` `docs/character_census.md`; `[RUN]` vertical sweep 59 cards. |
| 60 | Post-battle rewards cannot be applied / only result response | **corrected route** | `QuestsManager.Async` (`0xD65038`) lowercases the message, matches **`match-resolved`** (`0xD65338`), reads payload `qid`/`battleId`, calls `QuestProgression.UpdateMatchAttributes` / `UpdateCurrentFightId`, then `ProcessActionResultsAndProgression(quest, payload)` (`0xD65CA8`). The async payload, not the resolve result, carries progression/results/teamData. `[STATIC]` `work/quests_async.txt`, `work/find_async_slots.py`. |
| 61 | Windblade has no special-attack strings | **corrected** | Keys exist under the shortened token **`WINDB_GS`**: `ID_SPECIAL_ATTACK_WINDB_GS_0..2` and descriptions, `ID_CHARACTER_BIOS_WINDB_GS`; portrait `portrait_windb_gs_large.png`; moves `move_windblade_special_01/02`. The full-name key `WINDBLADE` is what the current catalog id produces. `[STATIC]` `work/localization_all.json`, census row `windblade_gs`. |

## 2026-10-31 v4.13 Step 0 corrections

| # | Claim | Status | Evidence |
|---:|---|---|---|
| 62 | The blueprint id must be the short loc token (`windb_gs_5`) | **disproved for the grid** | Renaming `windblade_gs` -> `windb_gs_5` removed the Windblade BOTS card entirely; restoring the asset id returned it. The loc token is a separate character field, not the blueprint key. `[RUN]` `docs/blueprint_ids.md`, `docs/evidence/blueprint_pilot/`. |
| 63 | Rewards are not applied because only the resolve result route was used | **partially corrected / still open** | Async `match-resolved` keys are confirmed (`qid`, `battleId`, `results`, `progression`, `teamData`, `version`), but three reward payload shapes still show empty REWARDS and 22%. The remaining cause is `Action.firstCompletionRewards`/active-quest refresh, not the route alone. `[RUN]` `docs/post_battle_flow.md`. |
| 64 | The 300 card rating and 0 HP/ATK are caused by the blueprint id | **not confirmed** | After restoring the asset key and setting the character token, the card still shows 300 and INFO still 0/0. The blueprint rename only removed the card. `[RUN]` `docs/blueprint_ids.md`. |
