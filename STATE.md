# STATE вЂ” Transformers: Forged to Fight 9.2.0 offline revival

Updated: 2026-10-22 19:05 UTC (local ~22:05 22.10.2026)

## 0. What this file is
Checkpoint against context loss. Only verified facts are recorded.
Tags: [RUN] executed and observed, [STATIC] read in code/data, [DERIVED],
[ASSUMED] guess.

## 1. Environment (verified this session)
- Project root: `C:\Users\gameg\Desktop\TFTF`
- Emulator `TFTF_AVD` (Pixel 4, API 30, x86_64) running; adb device `emulator-5554`
- `adb reverse tcp:8080 tcp:8080` set; stub server on `127.0.0.1:8080`
- App `com.kabam.bigrobot` 9.2.0 installed
- Original APK SHA-256: `77D2E9DD...68173763CB`; patched APK in
  `work/patched_build/tftf_patched_v9.2.0.apk`
- Note: `adb root` restarts adbd and clears `adb reverse`; re-add it.
- Note: server reads JSON per request; Python code changes need a server restart.

## 2. Verified milestones this session
1. **Roster fixed.** BOTS screen opens without the `SetFeaturedHeroData` NRE and
   shows Bumblebee 100; `EDIT SQUAD` shows `TOTAL 100`. Evidence:
   `work/r13.png`, `work/r38.png`, `work/run_logcat_8.txt`.
2. **Quest detail + START.** Quest 1.1 shows Bumblebee, `TOTAL 100`,
   `RECOMMENDED 100-200`, START active. [RUN] `work/r38.png`.
3. **Quest begin + map.** START calls `POST /quests/quest-begin/story_act1_ch1_m1`
   and the 3Г—3 map loads with the bot on the start tile. [RUN] `work/r47.png`,
   `work/r51.png`; requests 18:20.
4. **Movement request observed.** Tapping a tile sends
   `POST /quests/quest-movedir/story_act1_ch1_m1/1/0`. [RUN] requests 18:22,
   18:31.
5. **Quit quest** sends `POST /quests/quest-quit/story_act1_ch1_m1`. [RUN]
   18:31.

## 3. Key wire schema (verified)
### 3.1 BCG userData
`/bcg/getLoginData.result.userData` must be the wrapper:
`{userData:{blueprintsMax,teamSizeMax,teamCountMax}, updates:{heroes[],savedTeams[],activeTeams[],inventory{f,bp,max}}, deletes:{}}`.
- `heroes[]` item keys: `entity_type` (must be `"bot"`), `bid`, `rank`,
  `level`, `sig_lvl`, `required_xp`, `max_xp`, `stamina`, `stamina_ts`,
  `stamina_full_ts`, `stt`, `pvpb`, `exc`, optional `max_hp`, `attack`,
  `rating*`, `special_attacks`.
- `activeTeams` is a **dictionary keyed by `aid`** (`BCGUserActiveTeamDict`),
  not an array. Active team value:
  `{aid,type,modes,expire,heroes:{bid:details}}`; `heroes` is a dictionary
  parsed into `TeamHeroes` (`List<BCGHeroDetails>`).
  `savedTeams` schema remains less certain (`BCGUserSavedTeamDict` in the
  dump); do not assume an array.
- Catalog blueprints use key **`id`** (not `blueprint`); hero rank entries also
  use `id` + `rank`. `et` is the blueprint entity type.
- `/bcg/getBaseHeroData` request `{heroes:[{bid,rank,level,sig_lvl,flvl}],api,nonce}`;
  response is a **JSON array** of `BCGHeroDetails`.
- `/bcg/setSavedTeam` request `{teamID,heroes[]}`; response must be the full BCG
  catalog with `userData` set to the wrapper above.
- `featuredhero` must be in **`/account/data`** (not only `/auth/login`):
  `{cdn,orderType,heroes:[{id,gacha,gachaCTA,pvp,pvpCTA,questset,questsetCTA,
  store,storeCTA,synergies,abilities,image,images3}]}`.
- Details: `spec/bcg_userdata.md`.

### 3.2 Quests
- `POST /quests/quest-begin/{qid}` request:
  `{quitExisting,hash,api,setId,tm0..tm3}`.
  Response must be `{"activeQuests":{qid:{...,"teamData":<BCG wrapper>}}}`.
  `teamData` is passed to `BCGManager.UpdateUserData`. [RUN]
- Active map `grid` must be square `gridDimension Г— gridDimension`; a 3Г—1 row
  crashes `EB.Missions.Map.Deserialize` with ArgumentOutOfRangeException. [RUN]
- Map tiles must not contain invented `entities`; unknown boss ids crash
  `MapTile.Deserialize` with NullReferenceException. Removed for now. [RUN]
- `POST /quests/quest-movedir/{qid}/{dx}/{dy}` response currently
  `{progression:{version,currentPos,cleared,previouslyCleared,revealed},
  results:[],teamData:<wrapper>}`. The request is observed, but the bot does not
  visually move; client likely stays in pending progression. [RUN]
- Details: `spec/quest_protocol.md`.

## 4. Current blocker (next step)
Movement is **solved**: `/quests/quest-movedir` must return
`results:[{action:"moveto", moveto:{x,y}}]` plus `progression` and `teamData`.
The bot moved from (0,0) to (1,0); the HUD changed from 11% to 22% EXPLORED.
[RUN] `work/r75.png`, requests 18:55.

The next blocker is the **battle trigger**. A `battle` action with a minimal
`battleEnemy` did not call `/matches/activate-match`; no `/matches/*` request was
observed. `ActiveQuest.ActivateMatch` (`RVA 0x10A0038`) requires a `battleId` and
a hero and calls `MatchManager.ActivateMatch<QuestsMatchData>`. The normal trigger
is a battle tile/entity (`BCGEntity`) or `progression.currentBattleId`, not a
plain move. RAIDS is disabled by the client ("Raids are temporarily disabled."),
SPECIAL/ARENAS/ALLIANCE are level-locked. [RUN]

Battle tile static/runtime (2026-10-23):
- Exact NRE: `MapTile.Deserialize` reads `entities` via `Dot.Object`
  (`0x1485094`); `0x1485098 cbz x0,#0x1486508` jumps to the common throw
  block. A JSON array is not an `IDictionary`; `entities:{"enemy1":{...}}`
  fixed it.
- `MapTile` reads `builder.summary.bossTable` (`+0x28`/`+0x98`);
  `ActiveQuest..ctor` reads top-level `scaledBossTable` and passes it to
  `Quests.Builder..ctor` (`+0x18`).
- Factory by `baseType`: `bcg|boss|tower` -> `BCGEntity`; `building` ->
  `Building`; `generator` -> `Generator`; else generic `Entity`.
- Boss rendered (6★, 8888). [RUN] r86/r95/r117.
- `battle` action is the right trigger (`QuestActionResult..ctor
  0xEA28BC`); it opened the prefight screen. [RUN] battle3/pre2.
- `QuestUserInfo.team` is a JSON dictionary (`Dot.Object 0x103D5D8`):
  key = blueprint; value `hp` (float absolute), `pi`, `sig_lvl`,
  `stat_mods`, `sig_mods`. No level/rank/max in `QuestUserHero`.
- `TeamIsKnockedOut` (`0x1181DC8`): empty list -> true; any `HP>0` ->
  false. Memory after attempt 3: `battleId=battle1`, localPlayer exists,
  team count 0. [RUN] work/read_prefight_state.py.
- `BCGUserActiveTeamDict` is a dictionary; `BCGUserActiveTeam..ctor`
  (`0xA610F0`) reads `aid/type/modes/expire/heroes`; `heroes` is a
  dictionary parsed into `TeamHeroes` (`List<BCGHeroDetails>`).
- Sending `activeTeams` dictionary + `heroes` dictionary with
  `blueprint/rank/level/hp/max_hp` removed «ALL KNOCKED OUT», but the
  prefight team is still empty; «+»/FIGHT gives
  `PrefightScreenPresentation.GetNewScale(HeroData robot)` NRE.
  `/matches/activate-match` not called. [RUN] teamfix4/teamfix6.

Next: exact `BCGHeroDetails` element fields/keys and the id used by
`PrefightScreenData.GetCurrentTeam` (`BCGHelper.GetActiveTeam`).
No Frida/gadget/patches without consent.

## 4b. Wiki archive (Part B, 2026-10-23)

- Fandom: **3613** pages = **817 non-File + 2796 File**. All **817
  non-File** saved with full history + HTML; 5 File too; all **2796 File
  descriptions** saved (latest revision). [DERIVED] confirmed.
- TFWiki: **8** FTF pages full history + HTML.
- Images: **694/2752**; **209** errors (mostly 403,
  no bypass). Manifest **5154** entries; state resumable.
- Parsed: **44 bots** + **252 pages**; quality matrix
  `data/wiki/bot_matrix.json`; ID map `data/wiki/id_map.json` (59 client
  packs = 52 + 7 Sharkticon; 39 matched stat pages, 13 client without,
  44 wiki stat pages total); version sets
  `data/wiki/versions.json` (cutoff 2023-01-13; 96 changed, 11 created
  after).
- Unparsed: `data/wiki/unparsed/pages.json`.
- OneDrive author link auth-gated; not downloaded.

## 5. What is NOT verified / must not be claimed
- Battle did not start. No `match-*` request was observed.
- Roster stats, ranks, hero ids, quest names, map layout, rewards, account
  level/resources are [ASSUMED] / invented.
- Tutorials still all `"s": "completed"` (deliberate deviation).
- `quest-movedir` success is NOT confirmed; only the request is observed.
- FIDELITY.md legacy percentages are invalid.

## 6. Files changed this session
- `server/stub_server.py` — `/quests/quest-begin`, `/quests/quest-movedir`;
  `battle` action + `progression` experiment.
- `server/data/quest_begin_response.json`, `quest_detail.json` — entities
  dictionary; top-level `scaledBossTable`; boss on (1,0).
- `spec/quest_protocol.md` — §2f (exact NRE, boss table, factory) and §2g
  (`QuestActionResult`/battle schema/prefight).
- `LEDGER.md`, `FIDELITY.md`, `MASTER_PROMPT.md` — updated (v3.4).
- `OPEN_QUESTIONS.md` — battle blocker, OneDrive auth gate, archive gaps.
- `COVERAGE_WIKI.md`, `archive/wiki/*.py`, `archive/wiki/README.md`,
  `data/wiki/README.md` — archive, verification, parse.
- `data/wiki/bots.json` — 44 bots with page/revid/[WIKI].
- `data/wiki/pages.json` — 252 other content pages (classes, mods, relics,
  missions, events, ...), generic sections/tables.
- `data/wiki/bot_matrix.json`, `id_map.json`, `versions.json`,
  `versions/` — quality matrix, client↔wiki IDs, as_of/latest sets.
- `archive/wiki/raw/fandom/file_descriptions/` — 2796 File descriptions.
- `archive/TFTF_wiki_archive_2026-10-23.zip` — full archive backup.
- Work scripts: `disasm_calls.py`, `xref_bl.py`, `read_prefight_state.py`,
  `parse_bots.py`, `parse_pages.py`, `make_zip.py`.

## 7. Evidence index
- `work/r13.png` — BOTS roster.
- `work/r38.png` — quest detail with team, START active.
- `work/r86.png`, `work/r95.png`, `work/r117.png` — boss rendered (6★).
- `work/battle3.png`, `work/pre2.png`, `work/s5.png` — battle action opened
  prefight; empty team / knocked out.
- `work/battle6.png`, logcat 14:35/14:46 — `GetNewScale(HeroData robot)` NRE.
- `work/r119.png`, `server/requests.jsonl` 05:41:47Z — progression-only
  negative experiment.
- `work/read_prefight_state.py` — memory: currentBattleId=battle1,
  localPlayer exists, team List count 0.
- `archive/wiki/state.json`, `manifest.json`, `errors.json` — archive integrity.

## 8. Wiki backup zip (2026-10-23)

- `archive/TFTF_wiki_archive_2026-10-23.zip` (32,513,591 bytes)
- SHA256 `14b714b8e7e1409a2e74c32847ad78c7ee1e4a72cde3debfe97c2892da029c17`
- Integrity re-pack `archive/TFTF_wiki_archive_2026-10-23_210335.zip` (32,504,603 bytes; SHA256 `0731484c7c26463482488ac08f52ee75881bea7c3910f7cf9f3758da1509d559`); manifest 5154/5154 verified after 5 stale-hash corrections.
- Contains `archive/wiki/` (raw + HTML + File descriptions + 694 images +
  state/manifest/meta). Parsed `data/wiki/` is outside the zip.


## 12. Verification / P0 A3, S1, S2 (2026-10-23)
- `work/smoke_test.py` — ADB-сценарий с 7 скриншотами; PASS.
- `work/golden_regression.py --record` — 9 эталонных запросов;
  `--check` PASS, `tests/golden/`.
- `PrefightScreenData.GetCurrentTeam` использует
  `ActiveQuest.mode`, а не qid/uniqueId; mode-клоны
  `aid:"story"` добавлены, но prefight пуст.
- `QuestUserInfo.team` — List<QuestUserHero>; JSON — dict;
  верхнеуровневый team quest-begin переведён в dict.
- `/matches/activate-match` по-прежнему не вызван.


## 13. P1/P2 data and docs (2026-10-23)
- W1 synergy 40/44; W3 topics in `data/wiki/topics/`;
  W4 `data/wiki/client_only.json`; W6 `archive/INTEGRITY.md`.
- C2 `spec/rating_formula.md`; C3 four verified tuning defaults;
  C4 only 8 D_STAT keys found; C5 `server/data/bot_catalog_real.json`.
- C1 OpenAPI remains partial; C4 full localization blocked.

### 14. C4/W5/I1 updates (2026-10-23)
- `data/wiki/ability_localization_client.json`: 3315 D_STAT/ID_STAT entries.
- `data/wiki/image_index.json`: 694 unique images / 698 manifest entries;
  209 403 errors.
- `server/data/autorefresh_metadata.json` used by `/autorefresh/*`; golden
  regression PASS after restart.
- A3: 10 variants; activeTeams must be a list for login (v07 proved).

## 15. 2026-10-24: exact prefight blocker is the provider, not the team

- [RUN] The live prefight (TFTF_AVD, 2280x1080) shows `SELECT YOUR BOT`,
  empty slot, `FIGHT!`. Tapping FIGHT logs
  `NullReferenceException` at `PreFightScreen.OnFight`, not
  `PrefightScreenPresentation.GetNewScale`.
- [STATIC] `PreFightScreen.OnFight` (`0xE397BC`) first does
  `x20 = [this+0x98]` (`_model`, `IPrefightDataProvider`), `cbz` -> throw.
  The model is **null**; the rest of the method never runs.
- [STATIC] `_model` is assigned in `PreFightScreen.CacheReferences`
  (`0xE38E4C`) at `0xE38F08`:
  `x0 = [0x2BE2870]` (the `Get<IPrefightDataProvider>` generic method
  instantiation) -> `InterfaceInjector.Get<IPrefightDataProvider>`
  (`0x11E7640`) -> store at `this+0x98`.
- [RUN] Read-only probe (`work/read_injector.py`, `work/read_tag.py`,
  correct libil2cpp base `rw_start - 0x2AA7000`):
  - `_currentTag = "tform"`, `_hasBeenInitialized = 1`
  - `_gameInterfaces` count **78**
  - `_persistentInterfaces` count **1** =
    `IAdsProvider -> TFormIronSourceAdsModel`
  - 78 interface entries: entry 0 has tags `["tform","default"]`; all
    other 77 entries have only `["default"]`. Under the live tag `tform`
    only entry 0 resolves.
  - The tag is already `tform` on HomeFlow after a cold login, so it is
    not caused by the quest map. This is the current top hypothesis for
    the null provider; it is not yet proven that the prefight interface
    is one of the 77 default-only entries.
- [RUN] Team data is **not** the blocker any more. With the current
  `bcg_login_data.json` / movedir response:
  - `BCGManager.UserData.activeTeams` has `story_act1_ch1_m1`, `story`,
    `story_act_1`, each with `TeamHeroes count=1`
  - `QuestsManager` active quest mode `story`
  - `progression.localPlayer.team` is a `List` with **count 1**
  - `localPlayer.strongestHero = bumblebee_cin_dotm`
  - prefight UI is still empty because `PreFightScreen._model` is null.
- [RUN] `work/smoke_test.py` was run this session and returned FAIL only
  because the fixed sleeps are too short on the current cold boot
  (screenshot 02 was still the title screen). The flow itself reaches the
  prefight manually. This is a test-harness timing bug, not a server
  regression. The script needs screen polling (P0 S).
- [RUN] `work/golden_regression.py` (default check mode) reports 9 checks,
  2 shape changes: `/quests/quest-list` (we added the correct
  `showUI`/`group`/`recommendMinLevel` keys) and
  `/quests/quest-movedir/...` (current battle-action stub). Re-record
  after the P0 S flow is stable.
- [STATIC] `QuestActionResult..ctor` reads `data["action"]` as an
  **IDictionary** (`0xEA2BA4`), then looks up `moveto`/`battle`/... inside
  it. The working wire shape is
  `{"action":{"moveto":{"x":1,"y":0}}}` (nested), not
  `{"action":"moveto","moveto":{...}}`. The LEDGER 9 shorthand was
  imprecise; the stub already sends the nested shape.

## 16. 2026-10-24: P0 S smoke harness and golden

- `work/smoke_test.py` rewritten:
  - fast (default) and `--full` modes;
  - waits for PLAY NOW via a green-button detector and for the login/home
    requests (`/quests/quest-list` or `/base/active`) instead of a fixed
    38 s boot sleep;
  - steps: title, home, FIGHT, STORY, quest, quest detail, EDIT SQUAD,
    map, battle tile, `+`, FIGHT click, BOTS, bot popup, bot INFO;
  - memory probe now runs `read_bcg_memory.py` and the corrected
    `read_prefight_state.py`; team count is parsed from the List layout.
- [RUN] Full run: `status=PASS`, `quest_begin=true`, `movedir=true`,
  `prefight_detected=true`, `nre_prefight_model=true`,
  `memory_team_count=1`, `/bugs` triggered by the FIGHT click.
  Screenshots: `tests/smoke/05b_edit_squad.png`,
  `tests/smoke/07_battle_tile.png`, `tests/smoke/09_fight_click.png`,
  `tests/smoke/10_bot_details.png`, `tests/smoke/10b_bot_info.png`.
- [RUN] BOTS screen: Bumblebee, TOTAL 100; bot popup has UPGRADE/INFO;
  INFO screen shows `LEVEL 1/10`, `RANK 1/5`, `ATK 120`,
  `ABILITIES: NO ABILITIES`, SPECIAL ATTACKS list, Synergy Bonuses.
  This confirms the catalog is accepted and that abilities are the next
  data gap (P1 R3/R4).
- [RUN] EDIT SQUAD opens from quest detail, shows TOTAL 100 and the
  Bumblebee slot, ACCEPT returns to quest detail.
- [RUN] `work/golden_regression.py --record` then default check:
  9/9 PASS. Re-record was required by the quest-list key correction
  (`showUI`, `group`, `recommendMinLevel`) and the current movedir
  battle-action stub.
- `resume.ps1` added: checks adb device, `adb reverse`, starts the stub
  server if needed, verifies the installed package and APK hash, then
  optionally runs smoke/golden.

## 17. 2026-10-24: R1 full roster (59 client bot packs)

- `work/build_full_catalog.py` adds **all 59 client bot packs** to
  `server/data/bcg_login_data.json`:
  - 57 new bots + the existing Bumblebee (`bumblebee_cin_dotm_2`) and
    Optimus (`optimus_c_tf_t3`);
  - `blueprints`, `heroes` rank entries (1..max_rank), `characters`,
    `userData.heroes`, `userData.entities.bot`, `updates.heroes`;
  - all six `heroClasses` with the wiki class triangle
    (Brawler>Warrior>Scout>Tech>Demolition>Tactician>Brawler;
    four edges [WIKI], Tech/Demolition [DERIVED]);
  - Autobot/Decepticon/Maximal/Predacon synergies; Sharkticon variants
    use their per-variant class and no faction synergy.
- **Source rule:** class/faction/generation from
  `server/data/bot_catalog_real.json` ([CLIENT] ids + [WIKI]); star-1
  HP/ATK/rating only for the 12 bots that have a parsed wiki star table;
  the other 47 use `[ASSUMED]` 1000 HP / 120 ATK / 100 rating. The
  catalog is explicitly marked as a test grant (original server returns
  only owned bots).
- [RUN] `smoke_test.py --full`: BOTS shows the full roster (Windblade,
  Wheeljack, Waspinator, Ultra Magnus, Thundercracker, Tantrum, ...),
  Windblade popup and INFO screen open with `LEVEL 1/10`, `RANK 1/5`,
  `ATK 826`, `102`, `ABILITIES: NO ABILITIES`, SPECIAL ATTACKS, Synergy
  Bonuses. No NRE. Evidence: `tests/smoke/09_bots.png`,
  `tests/smoke/10_bot_details.png`, `tests/smoke/10b_bot_info.png`.
- Team size set to **1** (`teamSizeMax`) to match the synthetic 1.1
  quest and avoid the client's "ADD MORE BOTS?" auto-fill prompt. The
  START prompt is still handled by the smoke when it appears.
- [RUN] Full smoke PASS: `quest_begin=true`, `movedir=true`,
  `prefight_detected=true`, `nre_prefight_model=true`,
  `memory_team_count=1`; golden 9/9 PASS after re-record.
- R2/R3/R4 remain open:
  - the BOTS card shows **300** for Windblade while the wiki star-1 max
    rating is **264** -> the client's `CalculateModifiedHeroRating`
    inputs are still not matched (R2);
  - ABILITIES shows `NO ABILITIES`; SPECIAL ATTACKS show raw
    `M1_SPECIAL_ATTACK_NAMEID_*` keys, not localized names (R3/R4);
  - Synergy Bonuses box is empty for Windblade despite the Autobot
    synergy entry (R4).

## 8. C4/W1/W2/W3 (2026-10-24)

- C4 7869 vs 7994: a broad `"k"` scan finds 7996 keys, of which 127 are
  AI/tuning config (not localization). 7869 is the localization-only
  count. 3315 D_STAT/ID_STAT is exact (8 D_STAT + 3307 ID_STAT); 3332 is
  legacy and not reproducible. [RUN]
- W1: five stale hashes corrected; current bytes match. Two HTML files
  are redirect/other-page responses relative to their revision JSON
  (`Meet Your Makers`, `Nothing And Everything`); raw untouched.
  `archive/wiki/MISMATCHES.md`, `archive/CHANGELOG.md`. [WIKI]
- W2: five wiki-only pages analysed. Optimus Prime -> `optimusprime_cin_tf`
  (wiki title "Optimus Prime (MV1)"); Soundblaster/Tactician is a class
  variant absent from 9.2.0; Chromia/Dead End/Starscream have no 9.2.0
  client pack. `data/wiki/id_map.json` updated. [CLIENT]+[WIKI]
- W3: `data/quests_real.json` from the archived Story page + eight act
  pages: 66 Story missions in 4 acts, 24 in Awaken and Corrupt, 3 each in
  three other act pages. 39 boss names matched to client ids with high
  confidence; 8 ambiguous, 7 none, 12 missing boss strings. Quest 1.1 is
  now "A Beast to Start" with boss Rhinox; map layout/rewards remain
  [ASSUMED]. [WIKI]+[RUN] quest title screenshot.

Final full-smoke note (2026-10-24): repeated after W3; still PASS. The
post-flow BOTS sub-run hit Home due to a scene-load race, so Windblade INFO
evidence is `work/final_windblade.jpg` (earlier run), not the latest
`tests/smoke/10b_bot_info.png`.

R5 addendum (2026-10-24): top-left account icon -> KABAM ACCOUNT? ->
LOGIN OPTIONS (KABAM/GOOGLE PLAY), with `/invites/privacy` and
`/benchmark/performance`; not the commander profile. CRYSTALS opens empty,
OBJECTIVES opens `[0/0] COMPLETE`, STORE is level-locked.

## 18. 2026-10-24: A1–A4 registry result

`docs/prefight_flow.md` added. Key: `IPrefightDataProvider` is injector entry
69, default-only (`PrefightScreenData`); live tag `tform`; `Get<T>` has a
default fallback, so the null points to a type-identity/ContainsKey or
call-site-interface mismatch. `IAdsProvider` is the only tform entry. BOTS is
not an injector consumer. No provider error in logcat before the NRE.

## 19. 2026-10-24: runtime prefight dump attempt

Read-only attempts to locate the live `PreFightScreen` instance failed:
`PreFightScreen_TypeInfo` and `WindowManager_TypeInfo` are metadata usage
tokens (`0x2000...`), not class pointers; the class struct is in a
metadata-heap mapping and a full scan timed out. `CacheReferences` is called
from `SetupWindow`; provider entry 69 is default-only. No Frida. See
`OPEN_QUESTIONS.md` §11.

## 20. 2026-10-24: I1/I2/S2/T5

- `docs/interfaces.md`: all 78 InterfaceInjector entries with tags,
  implementations, persistent flag, screen/subsystem and stub status.
  `IPrefightDataProvider` entry 69 (default-only) is the only FIGHT blocker.
- I2: `IAdsProvider` is the only persistent interface
  (`TFormIronSourceAdsModel`). Only `/autorefresh/ads/refresh` observed; no
  ad-network request; native IronSource not initialized by the stub.
- S2: `check_all.ps1` now prints `target_checks` and each `known_issues`
  entry, plus whether all xfails are resolved.
- T5: `MASTER_PROMPT.md` is v4.3 with current facts and the full queue.

## 21. 2026-10-25: prefight unblocked, battle-init blocker

**Corrected fact:** `PreFightScreen._model` is **not** null. A live dump via
`WindowManager.Instance.windowStacks` shows `_config`, `_presentationSCI`,
`_model` (`PrefightScreenData`) and `_presentation` all non-null. The earlier
null claim came from the failed object lookup, not from the object.

Root cause of the OnFight NRE: `PrefightScreenData.InitEnemy` reads
`QuestBoss.character`, which is `Entity.key` (`0xEA469C` -> `+0x30`). Our
`scaledBossTable.enemy1` had `key = "enemy1"` and the blueprint only in
`characters`. The BCG lookup for `enemy1` returned nothing, `_enemy` stayed
null, `GetHeroDataForSide(1)` returned null and `OnFight` NRE'd.

Data fix (no client patch): `key` is now the first `characters` entry
(`rhinox_gs_voyager2014`) in `quest_begin_response.json` and
`quest_detail.json`. Result: Bumblebee vs Rhinox, 1,050/1,050 HP, FIGHT
enabled. Pressing FIGHT sends `POST /matches/activate-match/quests_fight`
(body captured in `docs/evidence/a9/activate_match_request.json`).

**New blocker:** the fight scene loads and then
`BattleArbiterInitState.InitPlayer` NREs; no `/matches/match-loaded` follows.
Live `FightFlow.FightInitInfo` has both fighters non-null and both blueprints
non-null; enemy `FighterData.TeamData` is null, player's is non-null. This is
separate from the prefight provider and needs another pass.

Movement protocol: one `quest-movedir` request per move; `moveto` and
`battle` are actions in the response, not separate requests. With
`moveto` only, moving to the final tile does not open prefight; a client-side
boss-tile tap sends nothing. The server decides when to include `battle`.

## 2026-10-25 (v4.4 queue work)

- Prefight: live dump proves `_model` non-null; data root cause was
  `scaledBossTable.enemy1.key="enemy1"` instead of the boss blueprint. Fixed
  in `quest_begin_response.json`/`quest_detail.json`; FIGHT now sends
  `/matches/activate-match/quests_fight`.
- A5: Settings/Goals/Upgrade work with default-only providers under `tform`;
  profile popup is not reachable.
- A6: one `quest-movedir` request; `moveto`/`battle` are response actions.
- Step 4: debug/dev classes are scene components or dead code; no data-only
  activation, no extra requests.
- R1 v2: dot-thousands parser fix; rank/level effects are collinear; 47 bots
  without tables remain `[ASSUMED]`.
- S1: 12/59 BOTS cards opened (popup + INFO), no NRE; abilities still empty and
  special names raw.
- Step 6.2: `docs/screens.md` + `data/screens.json` list 180 Window classes.
- Q1/Q2/Q3: `server/data/quest_list.json` now has 66 Story + 24 Awaken quests
  with deterministic 3x3 maps and wiki boss ids.
- W1: 2 priority images recovered, 34 blocked by 403/no manifest URL; W5 zip
  `2026-10-25_195954` with hashes.
- T2: SQLite persistence module + 5 tests; T4 Netflix plan written.

## 22. 2026-10-25 session state

- Prefight provider: fixed by enemy-key data; live dump proves `_model`,
  `_config`, `_presentationSCI`, `_presentation` all non-null.
- FIGHT sends `/matches/activate-match/quests_fight`; new NRE in
  `BattleArbiterInitState.InitPlayer`; no match-loaded/resolve.
- Default-only screens under `tform`: Settings/Goals/Upgrade work; Profile
  popup not reachable.
- Movement: one movedir request; battle is a server response action.
- Quest list: 90 missions (66 Story + 24 Awaken), deterministic maps, boss map.
- BOTS: 12/59 popup+INFO opened without NRE; abilities empty/specials raw.
- R1 v2: parser fixed, rank/level collinear, 47 bots `[ASSUMED]`.
- W1: 2 priority images recovered, 34 blocked; W5 zip repacked.
- T2 SQLite module + 5 tests; tutorial switch; Netflix plan.
- Golden 9/9 PASS, unit tests 19/19 PASS (server running).
- Emulator became unstable (headless QEMU stalls/crashes); further live work
  needs a fresh stable boot.

## 2. 2026-10-25 Q1 dynamic quests

`/quests/quest-detail/{qid}`, `/quests/quest-begin/{qid}` and movedir now
build from `quest_list.json` for any of the 90 missions (name, act/chapter/
mission, map, boss id). Verified by HTTP for 1.1 (Rhinox) and 1.4.2
(Sideswipe); movedir returns the right boss key and map. `quest_detail.json`
and `quest_begin_response.json` remain templates/fallbacks.

## 3. 2026-10-25 stability and dynamic quests

- Windowed `angle_indirect` stayed alive through repeated restarts; headless
  QEMU was the unstable mode.
- `work/emulator_watchdog.py` checks/restarts the AVD, restores adb reverse,
  installs the APK if missing, launches, and supports snapshots. Smoke and
  run_variant call it before launching.
- Q1/Q2: detail/begin/movedir are dynamic for all 90 missions; the map uses
  the validated 9-tile template with a per-qid hash. Full smoke PASS.

## 4. 2026-10-25 hygiene, schema, coverage

- Git dangling audit: 839 MB APK / 155 MB cmdline-tools / 11 MB Il2CppDumper
  unreachable blobs match local originals; 337 MB invalid temp; nothing
  deleted. Pre-commit hook installed (source `work/git-hooks/pre-commit`).
- Battle: ModelID key `m`; tags `t`; next `PlayerAttributes.Init` HashSet NRE.
- Quest routing split: `server/routes/quests.py`; detail/begin/movedir dynamic
  for 90 missions. 70/90 boss ids; `data/boss_gaps.json` 20 gaps.
- R1 coverage: 37 WIKI / 22 ASSUMED (`data/wiki/stat_coverage.json`).
- R2 rows: `data/wiki/rating_rows.json` (236 table rows / 142 star rows);
  fits still partial.
- Specs: `spec/bcg_schema_full.md`, `spec/ability_schema.md`.
- Nightly/backup scripts; README_RESUME updated.

## 2026-10-26 battle init fixed

- Root cause: `DamageType..ctor` tail-calls `HashSet<string>..ctor` with
  `Blueprint.BaseRangedDamageType`; the list was null. `Tags` was a red herring.
- Fix: non-null `base_damage`/`base_ranged_damage`/`baseRangedDamageType` in all
  blueprints and characters; `bumblebee_cin_dotm` blueprint alias.
- `[RUN]` No NRE; `BattleArbiterMainState`, `_fighters` length 2, player
  hit-react vs enemy attack. Player HP 1.0 / HPMax 1050, enemy 1000; hit-react
  loop does not finish. No match-loaded/resolve-match for quest fight.
- Q3: Act 4 I/II bosses from wiki; 11 new ids, 9 gaps left (all Starscream).
- R2.1: client formula decoded; weights 0.2 max-HP / 1.0 attack; CeilToInt;
  `spec/rating_formula.md` + 6 tests.
- Smoke now records `battle_checks` and open xfails.
- Next: keep the battle open, record death/resolve/rewards, fix the hit-react
  loop; then Q4/Q5 and S1.

- **ODR blocker:** live WindowManager shows `FuseLoadingScreen`,
  `FullScreenBlocker`, `FuseODRBlocker` above `HudScreen`; Play Asset Delivery
  service is absent (`com.android.vending` not found). Battle logic runs behind
  the loading screen but input is blocked. This is now the main playable-battle
  blocker; see `docs/battle_started.md`.
- 3.1 bot matrix: `docs/bot_matrix.md`, `data/wiki/bot_matrix_full.json`
  (59 client packs, 44 wiki pages, 89 bios, 36 quest bosses, 5 extra wiki pages,
  20 variant-mapping gaps).

- 3.1 matrix: `docs/bot_matrix.md`, `data/wiki/bot_matrix_full.json`.
- 6.1 map validity: `docs/map_validity.md`, `data/map_validation.json`
  (90 maps, 0 errors).
- 6.3 economy: `docs/economy_report.md` (37 pages with no numeric table).
- 9.1/9.4: `docs/git_cleanup_runbook.md`, `docs/hook_audit.md`.
- R2.2/2.3: `data/wiki/rating_fit_v2.json`; raw HP/ATK fits RMSE 873-926,
  LOBO 750, no integer-exact formula; 4 outliers flagged.

- **FINAL 2026-10-26:** battle init NRE fixed; ODR/Play Asset Delivery blocks
  playable combat. Report: `report/FINAL_2026-10-26.md`.
- 4.x/8.2: `docs/ability_pilot_wiring.md`, `docs/wiki_revision_diff.md`.

- **Nightly actual:** check_all PASS (golden 9/9, fast smoke PASS, unit 25/25);
  full smoke FAIL by status (full-mode measurement loses quest checks); BOTS
  sweep 12/59 (no pagination). Old nightly printed PASS by exit code; fixed
  `work/nightly.ps1` now prints FAIL/PARTIAL. `docs/nightly_2026-10-26.md`.

## 2026-10-26 v4.7 addendum

- BaseRangedDamageType record: `docs/battle_init_fix.md`; evidence
  `docs/evidence/battle_init/`. Character field +0x48 is the getter source.
- ODR: `docs/odr_flow.md`; blocker Open, 0 downloads, no manifest, no /odr
  requests, PlayCore service missing. Artifact `work/dump_odr_blocker.py`.
- R2 LP: `data/wiki/rating_lp.json` infeasible; parser audit 20 pages, 0
  numeric misparses (`docs/parser_audit.md`).
- R1: `docs/stat_coverage.md`; 2 star-3 anchors, 20 class-median.
- Starscream: `docs/starscream_fallback.md`; 9 gaps, `[ASSUMED]` fallback.
- S1: `work/sweep_bots59.py` added; current BOTS remains 12/59 and blocked.
- MASTER_PROMPT v4.7.

- **S1 59/59:** `work/sweep_bots59.py` swept all 5 pages (59 cards):
  `info_error=0`, `nre=0`; `popup_error=59` is the old transition-frame metric,
  not an NRE. `tests/sweep/sweep_59.json`, `docs/sweep_diagnosis.md`.
  `nightly.ps1` now uses `sweep_bots59.py` and fast quest smoke by default;
  `-Full` keeps the full-mode experiment.

- **Nightly 21:19 PASS:** `nightly_2026-10-26_211947.log`; check_all PASS,
  smoke PASS (activate_match true), BOTS 59/59. Supersedes the 19:48 run.
