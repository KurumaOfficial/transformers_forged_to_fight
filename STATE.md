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
- `savedTeams` and `activeTeams` are **arrays**. Active team:
  `{aid,type,modes,expire,heroes:{bid:details}}`. Saved team:
  `{sid,heroes:[details]}`.
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
  (`0x1485094`); `0x1485098 cbz x0,#0x1486508` jumps to the common
  null-reference throw block. A JSON array is not an `IDictionary`;
  `entities:{"enemy1":{...}}` fixed it.
- `MapTile` reads `builder.summary.bossTable` (`builder+0x28`,
  `summary+0x98`). `ActiveQuest..ctor` reads top-level `scaledBossTable`
  (`0xC39038/0xC39044`) and passes it to `Quests.Builder..ctor`
  (`0xC393E4`, `0xEF2D04`, field `+0x18`).
- Factory by `baseType`: `bcg|boss|tower` -> `BCGEntity`; `building` ->
  `Building`; `generator` -> `Generator`; else generic `Entity`.
  `characters` is `Dot.StringList` -> `List<string>`.
- Boss rendered (6★, 8888). [RUN] r86/r95/r117.
- **`battle` action is the right trigger.** `QuestActionResult..ctor`
  (`0xEA28BC`) reads `data["action"]` as IDictionary; `battle` fields:
  `x`, `y`, `isFinalBoss`, `battleEnemy` (id + BCGEntity/QuestBoss
  fields), optional `battleTower`. Action types 0..11 documented in
  `spec/quest_protocol.md` §2g.
- Live: after `quest-movedir/1/0`, the client opened the **prefight
  screen** “SELECT YOUR BOT” from the battle action. [RUN] battle3/pre2/s5.
- But local `team` is empty: `localPlayer.team` is a `List` with count 0
  in memory, even after sending `team` as a dictionary. Tapping “+”/FIGHT
  crashes in `PrefightScreenPresentation.GetNewScale(HeroData robot)` ->
  `NullReferenceException`; after base-blueprint change the screen says
  “YOUR BOTS ARE ALL KNOCKED OUT”. `/matches/activate-match` still not
  called. [RUN] work/read_prefight_state.py, logcat 14:35/14:46.
- `ActiveQuest.ActivateMatch` (`0x10A0038`) has no direct BL (0 hits);
  called via UI/delegate. It requires non-empty `progression.localPlayer.
  battleId` and `hero` (`No battle id!`/`No hero!`).
- Memory after response: version 3, currentPos (1,0), currentBattleId
  `battle1`, `localPlayer` exists, `localPlayer.team` count 0.
- Asset/portrait: `bumblebee_cin_dotm_2` accepted by roster; base asset
  pack is `bumblebee_cin_dotm`; prefight still loads `portrait_unknown.png`.

Next: fix the `team`/`QuestUserHero` container (dictionary shape and
required `hp`/`pi`/`sig_lvl`/`mods`), then press FIGHT and capture
`/matches/activate-match`. Do not use Frida/gadget/patches without consent.

## 4b. Wiki archive (Part B, 2026-10-23)

- Fandom: **3613** pages = **817 non-File + 2796 File**. All **817
  non-File** saved with full history + HTML; 5 File too; all **2796 File
  descriptions** saved (latest revision). [DERIVED] confirmed.
- TFWiki: **8** FTF pages full history + HTML.
- Images: **694/2752**; **209** errors (mostly 403,
  no bypass). Manifest **5154** entries; state resumable.
- Parsed: **44 bots** + **252 pages**; quality matrix
  `data/wiki/bot_matrix.json`; ID map `data/wiki/id_map.json` (59 client
  packs = 52 + 7 Sharkticon; 44 wiki stat pages); version sets
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

- `archive/TFTF_wiki_archive_2026-10-23.zip` (32,513,587 bytes)
- SHA256 `040255c1d5714b4510493e87de4e323674864f5d54436c776d190c12285d4e18`
- Contains `archive/wiki/` (raw + HTML + File descriptions + 694 images +
  state/manifest/meta). Parsed `data/wiki/` is outside the zip.
