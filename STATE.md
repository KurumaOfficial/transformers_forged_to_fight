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
