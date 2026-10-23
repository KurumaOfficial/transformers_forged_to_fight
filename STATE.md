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
  null-reference throw block. A JSON array is not an `IDictionary`, so
  `Dot.Object` returns null. `entities:{"enemy1":{...}}` fixed it.
- `MapTile` reads `builder.summary.bossTable` (`builder+0x28`,
  `summary+0x98`). `ActiveQuest..ctor` reads top-level `scaledBossTable`
  (`0xC39038/0xC39044`) and passes it to `Quests.Builder..ctor`
  (`0xC393E4`, `0xEF2D04`, field `+0x18`). The table must be in the
  top-level active-quest object, not in `data`/`map`.
- Entity factory is selected by **baseType**: `bcg|boss|tower` ->
  `BCGEntity`; `building` -> `Building`; `generator` -> `Generator`;
  otherwise generic `Entity` (`0xEF28CC`, `0x149B5D4`, `0x149B800`).
- `characters` is `Dot.StringList` (`0x1464E0C`) -> `List<string>`.
  `bumblebee_cin_dotm_2` is the accepted roster id; the asset pack is
  `bumblebee_cin_dotm` (`work/unpacked/assets/.../toc.txt`).
- Boss rendered on the map (6 stars, 8888). [RUN] work/r86.png,
  work/r95.png, work/r117.png.
- Asset scan: 3201 files, no real `scaledBossTable` sample; only metadata.
- Cheap experiment: added `currentFightId`, `currentBattleId`,
  `currentBattleBossId`, `currentBattlePos`, `localPlayer` to the movedir
  response. Client sent `/quests/quest-movedir/.../1/0`, but the bot stayed
  at (0,0), HUD 11%; `/matches/activate-match` was not called. Negative:
  progression-only is insufficient. [RUN] work/r119.png, 05:41:47Z.
- Memory after a normal move (without entity): `ActiveQuests=1`,
  `pendingProgressionCount=0`, `progression.version=2`, `currentPos=(1,0)`,
  `currentBattleId=null`. [RUN] work/adb_legacy_quest.py.

Next: a `battle` action with a full `battleEnemy`/`battleId` (or another
explicit trigger) must be tried; do not guess beyond one variant without
user approval. No Frida/gadget without consent.

## 4b. Wiki archive (Part B, 2026-10-23)

- Fandom: **3613** pages enumerated in 35 namespaces; **822** saved with
  full revision history + rendered HTML (1782 manifest entries).
  allredirects=20, allcategories=80, allimages=2752.
- TFWiki mirror: **8** FTF pages saved (full history + HTML), selected by
  search; whole wiki reports 139066 pages but only FTF titles were taken.
- Image binaries downloaded: **118** of 2752; remaining URLs are in
  `archive/wiki/meta/allimages_fandom.json`, state is resumable.
- Extensions: Fandom Scribunto=yes, Cargo=no; TFWiki Scribunto=no, Cargo=no.
  Fandom `Module:` (ns 828) has 0 pages.
- Raw: `archive/wiki/raw/` (not in git, large); lists: `archive/wiki/meta/`;
  state: `archive/wiki/state.json`; manifest: `archive/wiki/manifest.json`;
  errors: `archive/wiki/errors.json` (24 entries, mostly HTTP 403
  from static.wikia.nocookie.net; retry with browser UA/Referer works).
- Parsing: **0 pages** parsed into `data/wiki/`; raw only. Every saved page is
  listed in `archive/wiki/unparsed/pages.json` with the reason. No invented
  values; hidden base stats (crit/armor/block) are not claimed.
- Author collection link: `https://1drv.ms/u/s!ApD2f3dIXZ_7yjf4KMB9YQzgWQCG?e=jiLxKN`
  from `User:KRBrickBot` revid 10874, see `OPEN_QUESTIONS.md`.
- Coverage report: `COVERAGE_WIKI.md`.

## 5. What is NOT verified / must not be claimed
- Battle did not start. No `match-*` request was observed.
- Roster stats, ranks, hero ids, quest names, map layout, rewards, account
  level/resources are [ASSUMED] / invented.
- Tutorials still all `"s": "completed"` (deliberate deviation).
- `quest-movedir` success is NOT confirmed; only the request is observed.
- FIDELITY.md legacy percentages are invalid.

## 6. Files changed this session
- `server/stub_server.py` — `/quests/quest-begin`, `/quests/quest-movedir`
  (including the one-shot `currentBattleId + localPlayer` experiment).
- `server/data/quest_begin_response.json`, `quest_detail.json` — `entities`
  is now a dictionary keyed by entity id; top-level `scaledBossTable`; boss
  entity on (1,0).
- `spec/quest_protocol.md` — §2f: exact NRE instruction, `builder.summary.
  bossTable` chain, entity factory, `characters`, negative experiment.
- `LEDGER.md`, `FIDELITY.md`, `MASTER_PROMPT.md` — updated (v3.2).
- `OPEN_QUESTIONS.md` — author OneDrive link, battle-trigger gap, archive gaps.
- `COVERAGE_WIKI.md`, `archive/wiki/*.py`, `archive/wiki/README.md`,
  `data/wiki/README.md` — wiki archive and integrity state.
- `archive/wiki/meta/author_collection.json` — link, revid 10874, source.
- Work scripts: `disasm_calls.py`, `write_spec_2f.py`, `gen_coverage.py`,
  `find_tiles_arg.py`, `archive_wiki.py`.

## 7. Evidence index
- `work/r13.png` — BOTS roster.
- `work/r38.png` — quest detail with team, START active.
- `work/r47.png`, `work/r51.png` — quest map loaded.
- `work/r86.png`, `work/r95.png`, `work/r117.png` — boss entity rendered
  (6★, 8888) after the `entities` dictionary fix.
- `work/r119.png` — movedir accepted, bot stays at 11%, no
  `/matches/activate-match` after the `currentBattleId + localPlayer` attempt.
- `server/requests.jsonl` — request log; `05:41:47Z` is the negative attempt.
- `archive/wiki/state.json`, `manifest.json`, `errors.json` — archive integrity.
