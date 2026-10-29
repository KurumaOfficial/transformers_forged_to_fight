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
| 39 | Normal player can kill the enemy without test data | **open** | Normal run got enemy to 124.25 HP; win required the test-only `weak_enemy` flag. Controls/positioning still need practice. |

## 2026-10-29 late correction: stat/localization keys exist

| # | Claim | Status | Evidence |
|---:|---|---|---|
| 40 | There are no original `ID_STAT_*`/`D_STAT`/special-attack keys | **corrected** | `work/localization_all.json`: 3307 `ID_STAT_*`, 8 `D_STAT*`, 390 `ID_SPECIAL_ATTACK_*` (65 bot/move tokens). They are localization keys, not numeric definitions. `spec/buff_catalog.md`. |
| 41 | Windblade special-attack names exist | **corrected** | No `ID_SPECIAL_ATTACK_WINDBLADE_*`; live raw `MS_ID_SPECIAL_ATTACK_WINDBLADE_0..2`. |
| 42 | The localization table can be extended from the server | **open** | Not proven; need Xlate/snapshot/override analysis and a live test. |

| 39 | Normal player can kill the enemy without test data | **confirmed [RUN]** | `battle_step.py` normal win: player HP 300.2, enemy HP 0, player damage 1069.5. `resolve_win_normal.json`. |
