# STATE — Transformers: Forged to Fight 9.2.0 offline revival

Updated: 2026-10-22 18:45 UTC (local ~21:45 22.10.2026)

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
   and the 3×3 map loads with the bot on the start tile. [RUN] `work/r47.png`,
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
- Active map `grid` must be square `gridDimension × gridDimension`; a 3×1 row
  crashes `EB.Missions.Map.Deserialize` with ArgumentOutOfRangeException. [RUN]
- Map tiles must not contain invented `entities`; unknown boss ids crash
  `MapTile.Deserialize` with NullReferenceException. Removed for now. [RUN]
- `POST /quests/quest-movedir/{qid}/{dx}/{dy}` response currently
  `{progression:{version,currentPos,cleared,previouslyCleared,revealed},
  results:[],teamData:<wrapper>}`. The request is observed, but the bot does not
  visually move; client likely stays in pending progression. [RUN]
- Details: `spec/quest_protocol.md`.

## 4. Current blocker (next step)
`quest-movedir` response is not committed by the client: bot stays on the start
tile and the map ignores further tile taps (pending progression). Need to
determine the exact response fields / result action that ends the pending move.
Candidate work:
1. Inspect `ActiveQuest.AddActionResultsAndUpdateProgression` (`RVA 0xC3A278`)
   and `QuestProgression..ctor` (`RVA 0xCA5684`) for the `results` item schema.
2. Compare with a real Kabam `movedir` capture if one can be obtained.
3. Check whether the client expects `progression.currentPos` as a different
   vector shape or a `results` action (e.g. move/loot).
4. Only after movement works: tap the final tile, observe
   `/matches/activate-match`, `/matches/match-loaded`, `/matches/resolve-match`.

## 5. What is NOT verified / must not be claimed
- Battle did not start. No `match-*` request was observed.
- Roster stats, ranks, hero ids, quest names, map layout, rewards, account
  level/resources are [ASSUMED] / invented.
- Tutorials still all `"s": "completed"` (deliberate deviation).
- `quest-movedir` success is NOT confirmed; only the request is observed.
- FIDELITY.md legacy percentages are invalid.

## 6. Files changed this session
- `server/stub_server.py` — `/bcg/getBaseHeroData`, `/bcg/setSavedTeam`,
  `/quests/quest-begin`, `/quests/quest-movedir`, `/quests/quest-quit` fallback.
- `server/data/bcg_login_data.json` — id keys, rank 4/5, userData wrapper,
  bot entity, saved/active team arrays.
- `server/data/account_data.json` — `featuredhero`.
- `server/data/login_response.json` — `featuredhero` (kept for completeness).
- `server/data/quest_begin_response.json`, `quest_detail.json` — square 3×3 map,
  entities removed.
- `server/data/redeemer_data.json` — nextrefresh moved to 2030 (stops the loop).
- `spec/bcg_userdata.md`, `spec/quest_protocol.md` — updated.
- `LEDGER.md`, `FIDELITY.md`, `STATE.md` — updated.
- Work scripts: `map_addr.py`, `build_rva_map.py`, `disasm_calls.py`, `xref.py`,
  `scan_jsonpaths.py`, `adb_live.py`, `adb_mem_featured.py`.

## 7. Evidence index
- `work/r13.png` — BOTS roster.
- `work/r38.png` — quest detail with team, START active.
- `work/r47.png`, `work/r51.png` — quest map loaded.
- `work/r52.png`–`work/r67.png` — movement attempts.
- `work/run_logcat_8.txt` — clean BOTS run.
- `server/requests.jsonl` — full request log (2026-10-22 17:41–18:31).
