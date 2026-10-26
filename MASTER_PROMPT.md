# MASTER_PROMPT v4.7 - current state and queue (2026-10-26)

Continue from this file if the chat is lost. Files beat this text:
`STATE.md`, `OPEN_QUESTIONS.md`, `LEDGER.md`, `report/FINAL_2026-10-26.md`,
`docs/prefight_flow.md`, `docs/interfaces.md`, `docs/screens.md`,
`docs/debug_modes.md`, `docs/protocol_coverage_2026-10-25.md`.

## 2026-10-26 v4.7 update (read this first)

- **Battle init NRE root cause:** `Blueprint.BaseRangedDamageType` (character
  field `BCGCharacterData +0x48`), not `Tags`. `DamageType..ctor` (`0xBB0B70`)
  tail-calls `HashSet<string>..ctor` (`0x12A9D94`). Fixed with non-null
  `base_damage`/`base_ranged_damage` in **characters** (blueprint keys alone do
  not feed the getter) and a `bumblebee_cin_dotm` blueprint alias. Full record:
  `docs/battle_init_fix.md`; evidence `docs/evidence/battle_init/`.
- **Battle reaches `BattleArbiterMainState`** with two `PlayerController`s;
  no `/matches/match-loaded` is sent for `quests_fight`; no resolve/rewards.
- **Global blocker:** `FuseODRBlocker` is Open even with 0 active/requested
  downloads and no pending WADs; `ODRManager` has no manifest
  (`_receivedDataFromServer=0`, `_initAndGetManifestComplete=0`), and PlayCore
  cannot bind to `com.android.vending` on the sideloaded emulator. No `/odr/*`
  request reaches the stub. See `docs/odr_flow.md`.
- **R2:** client formula exact; interval LP on raw HP/ATK is infeasible
  globally and per rank/level (`data/wiki/rating_lp.json`); 20-page parser
  audit has 0 numeric misparses. Need server rating split.
- **R1:** 37 WIKI/table, 22 ASSUMED; 2 anchored with star-3 + global ratio
  (10%), 20 class-median (25%). `docs/stat_coverage.md`.
- **Q3/4:** 81/90 boss ids; 9 Starscream gaps; explicit `[ASSUMED]`
  `nemesisprime_gs_voyager2015` fallback, never called the original.
  `docs/starscream_fallback.md`.
- **S1/nightly:** `work/sweep_bots59.py` reached **59/59** across 5 pages; 0
  info errors and 0 NRE. `popup_error` is a transition-frame metric, not an
  error. `nightly.ps1` uses the 59-card sweep and fast quest smoke by default;
  `-Full` keeps the full-mode experiment. Full-mode status remains a known gap.
- **Enums:** `spec/battle_enums.md`; damage strings `kinetic`/`energy`, class
  flags numeric, AI selectors `aiString`/`aiPer`, default behavior tree
  `Gameplay/AIBehavior/AIBehavior-Default`.
- **Open:** ODR/asset-pack init, Starscream pack, server rating split, 34 wiki
  images (Wayback 404/503 in tried variants), BOTS pagination/full smoke.
- No client patch/Frida; no push/gc/filter-repo/remote/config.

## 2026-10-26 battle init fixed (read this first)

- **`PlayerAttributes.Init` NRE resolved.** The null collection was
  `Blueprint.BaseRangedDamageType`; `DamageType..ctor` (`0xBB0B70`) tail-calls
  `HashSet<string>..ctor` (`0x12A9D94`), so the stack showed
  `HashSet..ctor <- PlayerAttributes.Init`. `Tags` was a red herring.
- Fix: non-null `base_damage` / `base_ranged_damage` /
  `baseRangedDamageType` in every blueprint and character, plus a
  `bumblebee_cin_dotm` blueprint alias. See `docs/battle_started.md`.
- `[RUN]` No NRE; `BattleArbiterMainState`, `_fighters[2]`, player
  `PlayerHitReactState`, enemy `PlayerAttackState`. Player HP 1.0 (HPMax 1050),
  enemy 1000; the hit-react loop does not finish, so no death/resolve/rewards.
- `/matches/match-loaded` is not sent for `quests_fight`; whether it is
  PvP-only is open.
- Q3: Act 4 I/II bosses filled from the wiki; 81/90 boss ids, 9 Starscream
  gaps. R2.1 client formula decoded (`spec/rating_formula.md`).
- Smoke now records `battle_checks` and open xfails for `match_loaded`,
  `fight_started`, `resolve_match`, `returned_to_map`.

## 2026-10-25 breakthrough (read this first)

- **Prefight is unblocked.** The live `PreFightScreen` has non-null
  `_config`, `_presentationSCI`, `_model` (`PrefightScreenData`) and
  `_presentation`. The earlier “`_model` is null” claim was a failed object
  lookup, not the object.
- Root cause of the old `OnFight` NRE: `PrefightScreenData.InitEnemy` uses
  `QuestBoss.character`, which is `Entity.key` (`0xEA469C`). Our
  `scaledBossTable.enemy1` had `key="enemy1"` instead of the blueprint
  (`rhinox_gs_voyager2014`), so the enemy lookup failed and `_enemy` stayed
  null. **Data fix** in `server/data/quest_begin_response.json` and
  `quest_detail.json`; no client patch.
- FIGHT is now enabled and sends
  `POST /matches/activate-match/quests_fight` with
  `{"hero":"bumblebee_cin_dotm_2","qid":"story_act1_ch1_m1","battleId":"battle1"}`.
- **New battle blocker:** `BattleArbiterInitState.InitPlayer` NRE after the
  fight scene loads; no `/matches/match-loaded`. Live `FightFlow.FightInitInfo`
  has both fighters and blueprints non-null; enemy `TeamData` is null.

## 2026-10-25 late session (v4.4 update)

- **Git audit done; no push/remote changes since the user's instruction.**
  History never contained APK, unpacked assets, libil2cpp, dump.cs, il2cpp
  dumps, zip, keystore or private keys. The remote does contain binary
  screenshots, wiki metadata/data and the personal path `C:\Users\gameg`; see
  `docs/git_audit.md` and `docs/git_cleanup_plan.md`. Local `/objects` has
  ~1.5 GiB of unreachable ZIP/PE residue; do not prune without a mirror backup.
- **Battle chain moved forward:** the `InitPlayer` NRE was caused by an empty
  `FighterData.Blueprint.ModelID` (the character prefab load returned null).
  `get_ModelID` reads `_characterData.ModelID`; the parser uses
  `JSONPaths.m` = `"m"`. Adding `"m"` plus `map_asset` to blueprints/characters
  fixed it. Adding `t`/`tags` made live `Blueprint.Tags` non-null (count 2).
  The next exception is `ArgumentNullException` from
  `PlayerAttributes.Init`'s `HashSet<string>` (`collection`); the only field is
  `BlueprintTags`, live non-null, so the exact null instance still needs a
  breakpoint. No match-loaded yet. See `docs/battle_init_progress.md`.
- **Q1 dynamic:** detail/begin/movedir now build from `quest_list.json` for all
  90 missions; verified 1.1 (Rhinox) and 1.4.2 (Sideswipe) by HTTP.
- **R1 LOBO:** moving a bot out of the fit gives 14.3% HP / 16.4% Attack mean
  error without a base anchor; with one anchor row it is 4.1% / 2.8%.
  Therefore the 47/59 bots without a known level-1 row cannot be derived at
  7–8%; `data/wiki/derived_level1.json` has 37 table-anchored bots as
  `[DERIVED]`, the rest stay `[ASSUMED]`.
- **Emulator:** windowed `angle_indirect` stayed alive through repeated
  restarts; headless QEMU was unstable. The watchdog is the next stability
  step.

- A5: Settings/Goals/Upgrade work with default-only providers under `tform`;
  Profile popup is not reachable from the home UI.
- A6: one `quest-movedir` request per move; `moveto`/`battle` are response
  actions. `moveto` only moves; a final-tile tap sends nothing; server decides
  when to include `battle`.
- S1 partial: 12/59 BOTS cards opened (popup + INFO), no NRE.
- Q1/Q2/Q3: quest-list now has 66 Story + 24 Awaken missions with deterministic
  3x3 maps and wiki boss ids; detail/begin/movedir still use static m1 data.
- T2: SQLite module + 5 tests, opt-in `TFTF_DB`; T4 plan written.
- R1 v2: parser fixed; rank/level effects are collinear; 47 no-table bots stay
  `[ASSUMED]`. R2 remains partial. R3/R4 data still empty/raw.
- W1: 2 priority images recovered; 34 blocked by 403/no URL. W5 repacked.

## 2026-10-25 hygiene / stability / schema additions

- **Git hygiene:** `docs/git_dangling.md` identifies the 1.5 GiB of unreachable
  objects: exact APK (839 MB), cmdline-tools zip (155 MB), Il2CppDumper zip
  (11 MB), SDK tool PE/ZIP blobs, and one 337 MB invalid temp. Originals exist
  on disk; nothing deleted. `.git/hooks/pre-commit` (source
  `work/git-hooks/pre-commit`) blocks binaries, >1 MiB files, unpacked
  assets, keys and `C:/Users/` in added text. **No push/gc/filter-repo.**
- **Stability:** windowed `angle_indirect` stable; watchdog + snapshot
  `tftf_home`; smoke/run_variant integration. Full smoke PASS.
- **Battle:** ModelID key is `m`; `map_asset`; `t`/`tags` make live
  `Blueprint.Tags` non-null. Next: `PlayerAttributes.Init` HashSet
  `ArgumentNullException`; `spec/bcg_schema_full.md` has the field/RVA table.
- **Quests:** `server/routes/quests.py` split out; detail/begin/movedir are
  dynamic for 90 missions; maps use the validated 9-tile template; 70/90 boss
  ids, 20 gaps in `data/boss_gaps.json`.
- **R1/R2:** `data/wiki/stat_coverage.json` (37 WIKI, 22 ASSUMED);
  `rating_rows.json` (236 stat rows, 142 star rows); fits are partial.
- **R3/R4:** `spec/ability_schema.md`, `data/wiki/ability_pilot.json`; raw
  `M1_SPECIAL_ATTACK_*` is not a retained localization key.
- **T1:** quest routing split done; T2/T3 done; `work/nightly.ps1`,
  `work/backup.ps1`, updated `README_RESUME.md`.

## What is proven now (v4.4)

- Client is original 9.2.0 (endpoint patched/re-signed only). SHA-256
  `77d2e9dd…63cb`. No Frida, gadget, client patch, block bypass or OneDrive.
- Login, 59-bot roster/BOTS, quest list/detail/begin/movedir, prefight and
  FIGHT → activate-match work. Full smoke was PASS before the emulator became
  unstable; golden 9/9 PASS; unit tests 19/19 PASS.
- **Battle blocker:** `BattleArbiterInitState.InitPlayer` NRE; no
  match-loaded/resolve; combat does not start. Team is **not** the blocker.

- `InterfaceInjector` live: tag `tform`, 78 entries, persistent 1
  (`IAdsProvider -> TFormIronSourceAdsModel`).
  - **Entry 69 `IPrefightDataProvider` = `default -> PrefightScreenData` only.**
  - `Get<T>` (`0x11E7640`) has a default fallback (`0x11E7988`), then
    `Activator.CreateInstance` (`0x11E79E8`).
  - The default fallback works: `_model` is non-null live and FIGHT activates
    a match. The old defect was the enemy key, not `Get<T>`.
- `CacheReferences` is called from `PreFightScreen.SetupWindow`; it has no
  early exit before `Get<IPrefightDataProvider>`.
  `Gameboard.OpenPreFightScreen` does not create/register a provider;
  `PrefightScreenData..ctor` is created by the injector.
- `PreFightScreen` was found live through `WindowManager.Instance.windowStacks`;
  `_config`, `_presentationSCI`, `_model` and `_presentation` are non-null.
  `_model._enemy` was null until `scaledBossTable.enemy1.key` was changed to
  the boss blueprint (`rhinox_gs_voyager2014`).
- `docs/interfaces.md`: all 78 interfaces; entry 69 works; the next blocker is
  `BattleArbiterInitState.InitPlayer`.
- S1: smoke has `known_issues`/`target_checks`/`xfail_open`.
- S2: old golden tagged `golden-baseline-2026-10-23`; diffs and reasons in
  `tests/golden/`.
- S4: `work/check_all.ps1` prints xfail status and target checks.
- 59 bots: 12 with wiki star-1 stats, 47 `[ASSUMED]`; abilities/special names
  are raw IDs; rating formula unresolved.
- W3: `data/quests_real.json` real mission names; quest 1.1 "A Beast to Start"
  (Rhinox); map/rewards `[ASSUMED]`.
- C4: 7869 localization is correct; 3315 stat strings exact (3332 legacy,
  17 unaccounted).

## Queue status v4.4

**P0 A:** A1 **done**; A2 **done**; A3 **done**; A4 **done**; A5 **done**; A6 **done**; A7 **done**; A8 **done**; A9 **partial/blocked** (activate-match captured; model-id/tags fixed; `PlayerAttributes.Init` HashSet NRE; no match-loaded); A10 plan only.
**P0 S:** S1 **partial** (12/59; emulator stability); S2 **done**.
**P1 I:** I1/I2 **done**.
**P1 R:** R1 **partial** (LOBO: 14.3%/16.4% without anchor, 4.1%/2.8% with one anchor; 37 table-anchored `[DERIVED]`, rest `[ASSUMED]`); R2 **partial** (fit, not formula); R3 **blocked** (no text source; raw ids); R4 **partial** (synergy data added, unverified; specials raw); R5 **done**; R6 **partial** (switch implemented, original flow unverified).
**P1 Q:** Q1/Q2/Q3 **done** (90 missions; detail/begin/movedir dynamic; maps/boss map); Q4/Q5 **blocked** (battle doesn't finish; static docs).
**P1 C:** C1 **partial**; C2 **partial**; C3 **partial** (4 verified); C4 **done**.
**P1 W:** W1 **partial** (2/36 priority recovered, 34 blocked); W2-W4 **partial** (extracts + gaps); W5 **done**.
**P2 T:** T1 **partial** (payloads dynamic, routing still central); T2 **done**; T3 **done**; T4 **done**; T5 **done**.
**Step 0:** git audit **done**; **no push/remote changes**; cleanup plan pending user decision.
**Step 1:** windowed `angle_indirect` stable so far; watchdog not yet written.

## Queue status v4.5

- Step 0: git audit + dangling audit + pre-commit hook done; no push.
- Step 1: watchdog/snapshot done; windowed angle stable; full smoke PASS.
- Step 2: ModelID/tags fixed; `PlayerAttributes.Init` HashSet NRE open.
- Step 3: blocked (no match-loaded).
- Step 4: R1 coverage 37 WIKI / 22 ASSUMED; LOBO errors recorded; R2 rows + partial fit.
- Step 5: S1 12/59; nightly/backup done; screens table exists.
- Step 6: Q1/Q2/Q3 done (70/90 boss ids); Q4/Q5 blocked.
- Step 7: C1/C2/C3 partial; sync/async catalog started.
- Step 8: W1 2/36; W2-W4 partial; W5 done.
- Step 9: T1 quest routing split done; T2/T3 done; backup done.
- Step 10: this file; STATE/FIDELITY/COVERAGE/OPEN_QUESTIONS updated.

## Next queue (v4.6)

1. Battle: breakpoint on `0xDAC198`/`HashSet..ctor`; then match-loaded/resolve.
2. S1 59/59; R3/R4; Q4/Q5 after battle.
3. C1/C2/C3 deeper; W2 exact economy; W1 remaining priority URLs.
4. Git cleanup only after user decision; never push/gc/filter-repo without consent.

## Rules

- Labels `[RUN]`, `[STATIC]`, `[DERIVED]`, `[ASSUMED]`; source tags
  `[CLIENT]`, `[WIKI]`, `[RUN]`.
- Three substantive attempts per experimental item, then `OPEN_QUESTIONS.md`
  and the next independent item.
- Commit and update `STATE.md` after each item.
- Do not modify the APK, raw wiki archive, or `server/data` without a ledger entry.
- Frida/gadget/client patches/block bypass/OneDrive: **no** without explicit
  user consent. Frida plan only.

---

# MASTER_PROMPT v4.1 — status addendum (2026-10-24)

The canonical task/plan is the user's **v4 master prompt** (2026-10-24). This
addendum supersedes the status text of the v3.x file below.

Read first: `STATE.md` (§15–17), `OPEN_QUESTIONS.md`, `report/FINAL_2026-10-24.md`,
`docs/memory_probe.md`, `docs/frida_plan.md`, `spec/match_protocol.md`.

Current facts:
- **Battle blocker is not the team.** `PreFightScreen._model` (`+0x98`) is
  null; FIGHT NREs in `PreFightScreen.OnFight` (`0xE397BC`). The model comes
  only from `InterfaceInjector.Get<IPrefightDataProvider>` (`0x11E7640`).
  Live injector: tag `tform`, 78 interfaces, 1 persistent (ads). Entry 0 has
  `tform`+`default`; all others `default`-only. Team probes show
  `TeamHeroes=1` and `localPlayer.team=1`.
- No `/matches/activate-match` observed. `spec/match_protocol.md` is a static
  skeleton; the response is `[ASSUMED]`.
- Smoke full PASS (`quest_begin`, `movedir`, prefight, model NRE, team=1);
  golden 9/9 PASS after re-record.
- 59 bots in BOTS; 12 have wiki star-1 stats, 47 are `[ASSUMED]`.
  Abilities/special names are raw IDs; rating formula is unresolved.
- W3: real story mission names in `data/quests_real.json`; 1.1 is
  "A Beast to Start" (Rhinox); map/rewards still `[ASSUMED]`.
- C4: 7869 localization is correct (7994 includes 127 tuning keys); 3315
  stat strings exact (3332 legacy, 17 unaccounted).
- A5/A6/A7: arena/special still locked; match skeleton/plan only; Frida not
  run and needs the user's decision (ARM64 root preferred).

Next queue: resolve the provider/injector, then capture activate-match and
implement the match flow; then R2–R6, C1/C3, W4/W5, I1/I2.

---

# MASTER_PROMPT v3 — Transformers: Forged to Fight offline revival

Version 3, 2026-10-22. Restored/updated copy. Canonical source: the user's
messages; if this file and the user's prompt disagree, ask the user.

## 0. How to read this
This project continues across sessions. Context has been lost twice. Everything
below is from reports. Files on disk are more important than this text: if
`STATE.md`, `spec/`, `report/` or the code disagree with this prompt, trust the
files and note the discrepancy. Communicate in Russian, simply.

## 1. Final goal
Recreate Transformers: Forged to Fight 9.2.0 (com.kabam.bigrobot) as close to 1:1
as possible with the original before shutdown: same client, same visuals, same
rules/numbers/content. Write our own backend that is indistinguishable to the
client from Kabam's servers. Personal use only: do not publish the APK, assets or
binaries.

Honesty principle: the client is unmodified (except endpointconfig URL and
re-signing), so the client side is exact. Server data originals are lost forever
(Kabam servers closed 2023-01-13; Netflix version closed 2026-05-08). Never
promise 100%. Measure how much data is real, reconstructed or invented.

## 2. Rules
- Tags: [RUN] executed and observed, [STATIC] read in code/data, [DERIVED],
  [ASSUMED]. Do not say "works" until it is visible in logs. Data sources:
  [CLIENT], [WIKI], [RUN], [ASSUMED].
- Do not modify the original APK. Edit copies only. Do not publish anything.
- Prefer experiments over reading. Show commands.
- Server data lives in replaceable files (`server/data/*.json`); code only reads
  them. Keep unsourced numbers separate and marked [ASSUMED].
- Maintain `LEDGER.md` (value -> source -> evidence -> confidence), `FIDELITY.md`
  (share of real/reconstructed/invented values per subsystem), and a table of
  negative results in LEDGER (variant -> result -> conclusion).
- Context-loss protection: `STATE.md` in the root (done, verified, open, next
  step). Update after each milestone and before any long action. Git commit after
  each milestone. `MASTER_PROMPT.md` lives in the root and is committed.
- Do not use Gummygamer/Transformers-Forged-To-Fight-Offline-Version; its data
  was rewritten by its author, not a Kabam dump.
- Do not install system software/drivers or anything requiring UAC/admin without
  consent. Everything else do yourself. Ask only if truly blocked.

## 3. Verified APK facts
- File `com.kabam.bigrobot_9.2.0-123129100_minAPI23(arm64-v8a,armeabi-v7a)(nodpi)_apkmirror.com.apk`,
  SHA-256 `77d2e9dd833c3789db541e04af08082547603b5815be28cf5f5d0c68173763cb`.
  Signed by Exploding Barrel Games Inc. (Kabam Vancouver), built by bundletool.
  Unity 2020.3.31f1, IL2CPP, metadata v27 unencrypted. 49 assemblies,
  13,493 classes, 89,278 methods.
- Assets fully in APK: 102 asset bundles (~714 MB, assets/assetpack), 108
  toc.txt (Play Asset Delivery manifests, 15 with empty "bundles"; 102 of 102
  claimed). 59 bot packs, 9 arenas, 337 portraits. The 15 packs without bundles
  are unverified. Content after 08.2022 (incl. Netflix) is absent.
- Combat engine is client-side (PlayerController, HitData, AIController,
  BehaviorTree), but numbers come from the server: BCGAttributeDataBase
  (AttackBase, HPMaxBase, Armor, CritChance, CritDamage, BlockProficiency,
  ManaGain, StunTime, etc.), TuningManager (/tuning), power rating coefficients.
  The client sends FightResultsData (IsWin, SuccessfulHits, HitsReceived,
  SuccessfulCombos, HighestCombo).
- Localization: 7,869 keys extracted to `work/localization_all.json` (a previous
  report said 7,994; the difference is unexplained). Real dialogues in
  `cutscenes_en`, 235 lines in `quests_en` (UI formats ACT {0}, Chapter {0}).
  Mission names like "Landing Site" were NOT found in localization; [ASSUMED].

## 4. Network and protection
- Kabam Sparx platform (EB.Sparx, EB.Net). HttpEndPoint -> EB.Net.WebRequest ->
  TcpClientBouncy -> native sockets; WebSocket; ENet (libenetlib.so); JSON.
- Server address: TextAsset endpointconfig in
  `assets/bin/Data/e1917cd7a6bdb4492a247b8f758df2ae` (Unity SerializedFile v22).
  Patch script `work/patch_apk_endpoint.py`; URL replaced with
  `http://127.0.0.1:8080` (fileSize, byte_size, string length recalculated).
  TLS does not start with http; no pinning bypass needed. Confirmed [RUN].
- libapkprotect.so is passive (checksum goes to /auth/login); re-signing does not
  crash the client. Signing: zipalign + uber-apk-signer v1.3.0 (v1/v2/v3), not
  jarsigner.
- Sparx response envelope: `{"ts","result","sync","async","error"}`
  (+fatal/retry).
- targetSdk 30, usesCleartextTraffic not set: http images via UnityWebRequest may
  be blocked; Sparx sockets are not affected.

## 5. Confirmed by run (2026-10-21, 44 requests)
- Boot sequence: POST /auth/init -> /auth/enumerate (result: [], empty array
  passes) -> /auth/prelogin (salt: "") -> /auth/login (auth.device: true) ->
  other login subsystems, quest-list, base/active, quest-progression ->
  HomeFlow (3D base) with active FIGHT button.
- /bcg/getBaseHeroData, /bcg/getUserData, /wallet/fetch are NOT requested on
  boot.
- PLAY NOW is the normal cold-start screen. `work/auto_play.py` finds the green
  button and taps it.
- Tutorials in /tutorial/get-login-data are "s":"completed": a deliberate
  deviation; the real flow still needs to be implemented.
- Quest protocol (`spec/quest_protocol.md`): summary keys act/chapter/mission
  (NOT actIndex etc.), showUI, group, recommendMinLevel; chapterCount is 1-based
  with a dummy zero element: [0,1] = one act, one chapter ([1] crashes
  BuildSummaryTable). availableQuests is an array of summaries. Call:
  POST /quests/quest-detail/{qid} body {"hash","nonce","api":11,"setId"}.
- Evidence: `work/stage1_logcat_full_final.txt`, `server/requests.jsonl`,
  `work/FINAL_hub.png`, `work/FINAL_story_chapters.png`,
  `work/stage2_quest_select.png`, `work/stage2_addbot.png`.
- Emulator abilist: x86_64,x86,arm64-v8a,armeabi-v7a,armeabi.
- Stub values (level, resources, quest-list content, 3x1 map, rewards,
  quest-detail) were INVENTED [ASSUMED].

## 6. Current state (v3, 2026-10-22)
The roster blocker is **solved**. The client reaches BOTS, EDIT SQUAD, quest
detail, START, `quest-begin`, the quest map, and a confirmed move.

### 6.1 Nine roster/map wire gotchas (details: spec/wire_gotchas.md)
1. `/bcg/getLoginData.result.userData` is the wrapper
   `{userData:{...}, updates:{heroes,savedTeams,activeTeams,inventory}, deletes:{}}`.
2. Hero `entity_type` must be `"bot"` (`GetHeroes` reads `entities["bot"]`).
3. `activeTeams` is a **dictionary keyed by `aid`** (`BCGUserActiveTeamDict`), not an array; active team = `{aid,type,modes,expire,heroes:{bid:details}}` (`heroes` is a dictionary). `savedTeams` uses `BCGUserSavedTeamDict` too; don't assume arrays.
4. Catalog blueprints use key **`id`**, not `blueprint`; rank entries also use `id` + `rank`.
5. `featuredhero` must be in **`/account/data`**, not only `/auth/login`.
6. `/bcg/getBaseHeroData` returns a **JSON array** of `BCGHeroDetails`.
7. `/bcg/setSavedTeam` returns the full BCG catalog + userData wrapper.
8. `/quests/quest-begin/{qid}` returns `{activeQuests:{qid:{...,teamData}}}`.
9. Active map `grid` is square `gridDimension × gridDimension`; no invented entities.

### 6.2 Movement (solved)
`/quests/quest-movedir/{qid}/{dx}/{dy}` must return
`results:[{action:"moveto", moveto:{x,y}}]` plus `progression` (version,
currentPos, cleared, previouslyCleared, revealed) and `teamData`. The bot moved
from (0,0) to (1,0), HUD 11% -> 22% EXPLORED. [RUN] work/r75.png.

### 6.3 Current blocker: battle trigger
A `battle` action with a minimal `battleEnemy` did not call
`/matches/activate-match`; no `/matches/*` request was observed.
`ActiveQuest.ActivateMatch` (`RVA 0x10A0038`) requires `battleId` + hero and calls
`MatchManager.ActivateMatch<QuestsMatchData>`. The normal trigger is a battle
tile/entity (`BCGEntity`) or `progression.currentBattleId`, not a plain move.
RAIDS is disabled by the client ("Raids are temporarily disabled.");
SPECIAL/ARENAS/ALLIANCE are level-locked. [RUN]

Next: build a valid battle action/entity (`BCGEntity.Deserialize 0xC17FEC`,
`QuestBoss` keys) or set `currentBattleId`/`currentFightId` + `localPlayer`; then
capture `/matches/activate-match`, `/matches/match-loaded`,
`/matches/resolve-match`.

### 6.4 Fidelity table (honest)
| Subsystem | Wire/schema | Data/values | Evidence |
|---|---|---|---|
| APK, assets, UI, render | 100% original | 100% original | client unchanged except endpoint + signature |
| Sparx auth/envelope | confirmed [CLIENT]+[RUN] | account/token [ASSUMED] | boots to hub |
| BCG catalog | keys confirmed [CLIENT] | stats/ranks/ids [ASSUMED] | 13 gotchas |
| BCG userData/roster | confirmed [RUN] | hero/stats [ASSUMED] | BOTS + EDIT SQUAD |
| Quest list/detail | keys confirmed [RUN] | content [ASSUMED] | 1.1 Landing Site invented |
| quest-begin/map | confirmed [RUN] | map 3x3 [ASSUMED] | map loads |
| quest-movedir | confirmed [RUN] | progression [ASSUMED] | move works |
| Combat (`/matches/*`) | not observed | no data | 0% confirmed |
| Economy/shop/PvP/alliances | not started | no data | outside slice |

The client side is original. The **server schemas** for roster, quest begin and
movement are confirmed by run; the **numbers** remain synthetic. Combat is not
confirmed.

## 7. Rejected / do not repeat
- "Combat is 100% client-side; only win confirmation was lost": false.
- Any "85-90%" or "50-55%" percentages: unjustified. Use FIDELITY.
- Endpoint lists built by string search: unreliable (garbage like /bin/bash).
  Build from calls in dump.cs/Ghidra and run logs.
- Hidden base stats (crit, armor, block) were not found in APK or wiki. Do not
  use invented "typical ranges" as facts.
- The 14 tests in tests/test_api_schemas.py and tests/test_spec_evidence.py only
  check stub-vs-SPEC consistency, not client compatibility.
- The old 6-phase plan omitted skill trees, mods/relics, objectives, events and
  leaderboards, login/level rewards, prizes, subscriptions, titles, AVA/AVE,
  shop/offers, factions, mail, chat, alliances. All are in scope.

## 8. External data sources
- Fandom wiki transformers-forged-to-fight.fandom.com: max HP/Attack by stars,
  ability percentages by rank, synergies, class triangle (Scout, Tech,
  Demolitions, Tactician, Brawler, Warrior), relic bonuses. Rank/level tables in
  HTML are empty: download raw wikitext and Module:/Data: pages via MediaWiki API
  on the user's PC. Values with source (page, revision), tag [WIKI]. Reference,
  not a full dataset.
- Other sources (videos, third-party caches, traffic captures): make a list of
  "what to bring" and which data it closes.

## 9. Environment (verify)
Windows 11 Home, AMD Ryzen. Root `C:\Users\gameg\Desktop\TFTF`: `work/`
(unpacked, il2cpp_dump\dump.cs, patched_build\tftf_patched_v9.2.0.apk,
uber-apk-signer.jar, android-sdk, patch_apk_endpoint.py,
verify_endpoint_patch.py, auto_play.py, localization_all.json), `server/`
(stub_server.py, requests.jsonl, bcg_login_data.json, data\), `spec/`
(openapi.json 3.0.3: 53 paths with x-evidence and x-client-behavior;
quest_protocol.md; bcg_userdata.md), `docs/` (protocol_coverage.md,
coverage_matrix.md), `tests/`, `report/`, STATE.md, LEDGER.md, FIDELITY.md.
Emulator TFTF_AVD (Pixel 4, Android 11 google_apis x86_64, 4 GB RAM, AEHD).
Run: `adb reverse tcp:8080 tcp:8080`; `python server\stub_server.py 8080`;
`adb install -r --no-incremental <apk>`; `python work\auto_play.py`.

## 10. First actions in a new session
a) Read STATE.md, LEDGER.md, FIDELITY.md, spec/*, tail requests.jsonl, git log.
   Summarize and check against this prompt.
b) Bring up the environment and repeat the run to the hub. Verify HomeFlow and
   attach fresh requests.jsonl + full logcat.

## 11. Plan
Step A (roster blocker): DONE on 2026-10-22. Roster works.
Step B (vertical slice): bot in EDIT SQUAD -> START -> quest-begin ->
activate-match -> match-loaded -> resolve-match. Record real request/response
bodies in requests.jsonl and SPEC with [RUN]. Goal: understand which server
fields actually enter combat formulas and which can be taken from the client or
wiki.
Step C: wiki parser (raw wikitext) can be written in parallel.
Step D (after A and B): extract real client data, inject localization into
quests, then backend for all systems (roster, combat, quests, crystals, economy
and progression, skills, mods/relics, base/raids, Away Teams, PvP, events,
objectives, rewards, shop, alliances/chat). Mark everything replaced by bots or
generation.
Step E: verification and metrics: autotests, [RUN] walkthrough checklist,
fidelity table per subsystem, frame comparison if videos are available. Result
in report2/.

Do not expand scope until Steps A and B are complete. After Step B, stop and show
the result and the updated fidelity table. If the session ends earlier, update
STATE.md and commit.


## 12. v3 changelog (2026-10-22)
- Roster solved: BOTS + EDIT SQUAD, 9 wire gotchas.
- Quest begin/map solved; movement solved with `action:"moveto"`.
- Current blocker: battle trigger (`/matches/activate-match`).
- Added `spec/wire_gotchas.md`, `report/stage2b_roster_and_quest_map.md`.
- Fidelity table updated (see 6.4).

## 13. v3.1 — боевой тайл (2026-10-22)
- `ActiveQuest..ctor` (`RVA 0xC38BC8`) reads `scaledBossTable` from the active quest.
- `MapTile.Deserialize` (`RVA 0x1484C04`) reads `entityType`, `boss` (bossTableId),
  `links`, `visibleLinks`, `bg`, `bt`, `ab`, `sockets`.
- `QuestBoss.Deserialize` (`RVA 0xEA3F60`) keys: `isFinalBoss,characters,rank,
  level,sig_lvl,flvl,aiType,aiString,aiPer,mapOverride,todIndex,...`.
- `Entity.Deserialize` (`RVA 0x1334A04`) keys: `uid,key,hi`.
- Three variants (boss table + entity; + uid/key/hi/type/baseType; +
  bg/bt/ab/sockets) still NRE in `MapTile.Deserialize`; `/matches/*` not called.
- Memory after normal move: `ActiveQuests=1`, `pendingProgressionCount=0`,
  `progression.version=2`, `currentPos=(1,0)`, `currentBattleId=null`.
- Next: dynamic tracing of `MapTile.Deserialize`/`QuestBoss.Deserialize` or a
  real `scaledBossTable`/tile entity sample. No Frida/gadget without consent.


## 14. v3.2 — боевой тайл и вики-архив (2026-10-23)
- Exact NRE: `MapTile.Deserialize` reads `entities` via `Dot.Object`
  (`0x1485094`); `0x1485098 cbz x0,#0x1486508` is the null-reference throw.
  `entities` is an `IDictionary` keyed by entity id, not an array.
- `MapTile` reads `builder.summary.bossTable` (`builder+0x28`,
  `summary+0x98`). `ActiveQuest..ctor` reads top-level `scaledBossTable`
  (`0xC39038/0xC39044`) and passes it to `Quests.Builder..ctor`
  (`0xC393E4`, `0xEF2D04`, field `+0x18`).
- Factory by `baseType`: `bcg|boss|tower` -> `BCGEntity`; `building` ->
  `Building`; `generator` -> `Generator`; otherwise generic `Entity`
  (`0xEF28CC`). `characters` is `Dot.StringList` -> `List<string>`.
- Boss rendered (6 stars, 8888). [RUN] `work/r86.png`, `work/r95.png`,
  `work/r117.png`. Asset scan (3201 files): no real sample, metadata only.
- Cheap experiment with `currentBattleId + localPlayer` in `progression`:
  negative; movedir was sent, bot stayed at 11%, `/matches/activate-match`
  was not called. [RUN] `work/r119.png`, 05:41:47Z.
- Wiki archive: Fandom content/HTML/full history partially saved (state for
  continuation), TFWiki FTF pages saved, author collection link recorded in
  `OPEN_QUESTIONS.md`. See `COVERAGE_WIKI.md`.


## 15. v3.3 — battle action, prefight, wiki parse (2026-10-23)
- `QuestActionResult..ctor` (`0xEA28BC`) reads `data["action"]` as an
  IDictionary. `battle` fields: `x`, `y`, `isFinalBoss`, `battleEnemy`
  (`id` + BCGEntity/QuestBoss), optional `battleTower`; types 0..11 are
  in `spec/quest_protocol.md` §2g.
- Live: `battle` action opened the **prefight** screen. [RUN]
  `work/battle3.png`, `work/pre2.png`.
- Blocker: `localPlayer.team` is a `List` with count 0; «+»/FIGHT gives
  `PrefightScreenPresentation.GetNewScale(HeroData robot)` NRE. No
  `/matches/activate-match`.
- Wiki: 3613 Fandom pages enumerated; 817 non-File pages saved with full
  history+HTML, 2796 File descriptions saved, 694 images downloaded (209 403 errors).
  44 bots + 252 pages parsed into `data/wiki/*.json` with [WIKI]/revid.
- Author OneDrive link is auth-gated; not downloaded.


## 16. v3.4 — team, prefight, wiki matrix (2026-10-23)
- `QuestUserInfo.team` is a JSON dictionary (`Dot.Object 0x103D5D8`);
  key = blueprint, value = `hp` (float, absolute), `pi`, `sig_lvl`,
  `stat_mods`, `sig_mods`. `QuestUserHero` has no level/rank/max_hp.
- `PlayerMarker.TeamIsKnockedOut` (`0x1181DC8`) returns true for count 0;
  hence "ALL KNOCKED OUT" with team count 0. Memory after attempt 3:
  `currentBattleId=battle1`, localPlayer exists, team count 0.
- `PreFightScreen.OnFight` (`0xE397BC`) -> `PrefightScreenData.OnFight`
  (`0xE3E778`); prefight HP comes from `TeamData.GetHP`.
- `battle` action opens prefight; `/matches/activate-match` still not
  called. Stub remains `[ASSUMED]`.
- Wiki: 3613 = 817 non-File + 2796 File; all non-File full history/HTML;
  all File descriptions; 694/2752 images; 44 bots + 252 pages parsed;
  matrix/ID map/version sets in `data/wiki/`.


## 17. v3.5 — activeTeams dict / prefight (2026-10-23)
- `BCGUserActiveTeamDict` is a dictionary keyed by activityID, not a list.
- `BCGUserActiveTeam..ctor` (`0xA610F0`) reads `aid`, `type`, `modes`,
  `expire`, `heroes`; `heroes` is a dictionary parsed into
  `TeamHeroes` (`List<BCGHeroDetails>`).
- `BCGHeroDetails` uses `blueprint`, `rank`, `level`, `sig_lvl`,
  `HPRating`, `HPMax`, `AttackRating`, `Attack`, `AttributeData`,
  `ForgeLevel`.
- Sending `activeTeams` dictionary + `heroes` dictionary with
  `blueprint/rank/level/hp/max_hp` removed "ALL KNOCKED OUT"; prefight
  still empty, plus/FIGHT gives `GetNewScale` NRE; no
  `/matches/activate-match`.

## 18. v3.5 status after P0/P1/P2 pass (2026-10-23)

- P0 A1/A2: `GetCurrentTeam` uses `ActiveQuest.mode` (`+0x18`), not qid;
  mode clones added, prefight still empty. `QuestUserInfo.team` is a
  `List<QuestUserHero>` internally; JSON input is a dictionary.
- P0 A3: `work/run_variant.py` + 6 variants; all same blocker.
- P0 A4/A5: plus/FIGHT still NRE; `/matches/activate-match` not called.
- P0 S1/S2: `work/smoke_test.py` PASS; `work/golden_regression.py` 9/9 PASS.
- P1 W1: synergy 40/44. W2 notes; W3 13 topic files; W4 client-only map;
  W6 manifest 5154/5154 verified, new zip sha `0731484c...`.
- P1 C2 rating partial; C3 four defaults; C4 8 D_STAT keys only;
  C5 catalog 59 packs (59 class, 39 stars).
- P2 I1 data layout doc; I2 persistence design; I3 this file.
- Blockers are recorded in `OPEN_QUESTIONS.md`; no Frida/gadget/patches.
