# STATE — Transformers: Forged to Fight 9.2.0 offline revival

Updated: 2026-10-21 21:30 UTC (local ~00:30 22.10.2026)

## 0. What this file is
Checkpoint against context loss. It records only what was verified in this session.
Evidence tags: [RUN] executed and observed, [STATIC] read in code/data, [DERIVED] inferred
from verified facts, [ASSUMED] guess.

## 1. Environment (verified this session)
- Project root: `C:\Users\gameg\Desktop\TFTF`
- Original APK SHA-256: `77D2E9DD833C3789DB541E04AF08082547603B5815BE28CF5F5D0C68173763CB` [RUN]
- Patched APK: `work/patched_build/tftf_patched_v9.2.0.apk`, SHA-256
  `2777927F84E3DE3456446E5D83C787F6EC1009877F29B7067BF627B2019D442B` [RUN]
- Endpoint patch inside patched APK:
  `{"Default":{"Prod":"http://127.0.0.1:8080"}}` (4164-byte SerializedFile) [RUN]
- Emulator `TFTF_AVD` (Pixel 4, API 30, x86_64) started from
  `work/android-sdk/emulator/emulator.exe`; AEHD operational [RUN]
- `adb shell getprop ro.product.cpu.abilist` =
  `x86_64,x86,arm64-v8a,armeabi-v7a,armeabi` [RUN]
- App installed: `com.kabam.bigrobot` 9.2.0, versionCode 123129100, targetSdk 30 [RUN]
- `adb reverse tcp:8080 tcp:8080` was set for the final run [RUN]
- Note: `adb root` was used to inspect `/data/data`; it restarts adbd and kills
  running `adb logcat` sessions. Use `adb logcat` again after `adb root`.

## 2. Stage 1 — re-verified to the Home hub
Final clean run: requests 2026-10-21 21:23:13 → 21:24:45 UTC, 44 requests.
Evidence:
- `work/stage1_logcat_full_final.txt` — full `adb logcat -v threadtime`, no filters
- `server/requests.jsonl` — clean request log for that run
- `work/FINAL_hub.png` — 3D base hub (FIGHT menu visible)
- `work/FINAL_story_chapters.png` — Story → Act 1 → Chapter 1 → quest tile
- `work/stage1_logcat_full.txt` — earlier full run incl. login/tutorial
- `work/stage2_logcat_full.txt` — debug run, includes quest UI work

Observed boot sequence (actual, from requests.jsonl):
1. `POST /auth/init` (anonymous)
2. `POST /auth/enumerate` → server returns `[]`
3. `POST /auth/prelogin` → `salt: ""`
4. `POST /auth/login` → `auth.device: true`, stoken
5. parallel subsystem login: `/account/data`, `/bcg/getLoginData`, `/tuning`,
   `/payments/payouts`, `/autorefresh/*`, `/performance/profile`,
   `/redeemer/refresh`, `/events/refresh`, `/ds/10001/`,
   `/tutorial/get-login-data`, `/gamestats/*`, `/offers/getLoginData`,
   `/push/token`, `/inventory`, `/quests/quest-list`, `/quests/quest-active`,
   `/base/active`, `/pvp/get-login-data`, `/quests/quest-progression`,
   `/chat/data`, `/telemetry`, `/userprofile/`
6. HomeFlow (3D base) renders. `PLAY NOW` tap was required on a cold start.

This confirms [RUN] the earlier claim that the client reaches HomeFlow. It does
NOT confirm that all server payloads are correct; many are [ASSUMED].

## 3. Stage 2A — protocol discoveries this session
### 3.1 Quest wire format (verified by decompilation + run)
The blocker that hid chapters was the summary index keys. The client reads
`act`, `chapter`, `mission` on each quest summary, NOT `actIndex`,
`chapterIndex`, `missionIndex`.

Set-level keys used by `Legacy.QuestSet.AddQuestSummarys` [STATIC, RVA 0x10381F0]:
`hash`, `setId`, `setName`, `expiry`, `timeLimit`, `timeLimitGrace`, `showUI`,
`group`, `difficulty`, `difficulty_color`, `difficulty_color_bg`,
`difficulty_label`, `minLevel`, `recommendMinLevel`, `cdn`, `use_ui_color`,
`ui_color`, `hasProgression`, `tags`, `actCount`, `chapterCount`,
`availableQuests`, `acts`, `chapters`.
- `chapterCount` is a 1-based array: `[0, 1]` means Act 1 has one chapter.
  Sending `[1]` crashes `BuildSummaryTable` with ArgumentOutOfRangeException
  (observed in logcat). [RUN]
- `availableQuests` is an array of Summary objects. Each Summary needs
  `id`, `category`, `act`, `chapter`, `mission` (all ≥1). [RUN]
- `acts` and `chapters` are overlay arrays with `act` / `chapter` indices and
  presentation fields (`friendlyName`, `description`, `image`, ...). [STATIC]
- `QuestSummarys` is built from `availableQuests`; `QuestMaps` is separate. [STATIC]

After changing the summary keys to `act/chapter/mission`, the chapter panel
rendered and the quest tile opened `/quests/quest-detail/story_act1_ch1_m1`. [RUN]

### 3.2 Observed quest-detail call
`POST /quests/quest-detail/{qid}` body:
`{"hash":"v1","nonce":"...","api":11,"setId":"story_act_1"}` [RUN]
Response `quest_detail.json` is currently [ASSUMED] except for the keys above.

### 3.3 Observed next blocker (Stage 2B)
Quest detail screen renders, but:
- `TOTAL 0 / RECOMMENDED 100-200`
- `START` is disabled
- `EDIT SQUAD` has empty slots
- no `/bcg/getUserData` request is made
- opening BOTS crashes with `NullReferenceException` in
  `HeroesScreen.SetFeaturedHeroData` [RUN]
Cause: the roster is empty. `/bcg/getLoginData` currently contains a catalog
(`heroes`, `blueprints`, `characters`, ...) but the user roster is not being
accepted. The exact `userData`/`BCGUserHero` wire keys are not yet verified.

## 4. Files changed in this session (uncommitted at time of writing)
- `server/data/quest_list.json` — real Act/Chapter/quest structure, act/chapter/
  mission keys, `chapterCount [0,1]`, expiry/showUI/group keys. Values still
  [ASSUMED] except the schema.
- `server/data/quest_detail.json` — summary indices and team size 0 for testing.
- `server/data/quest_progression.json` — existing [ASSUMED] progression.
- `server/data/bcg_login_data.json` — added an experimental `userData` block
  (not yet accepted by the client; do not treat as working).
- `server/data/bcg_user_data.json` — new experimental roster payload.
- `server/stub_server.py` — `/bcg/getUserData` now loads the file; quest routes
  added earlier in the session.
- `work/disasm_strings.py` — RVA/ELF disassembler with string-literal key
  resolution; useful for further protocol work.
- Evidence PNG/logs listed in §2.

## 5. What is NOT verified / must not be claimed
- The roster / `userData` schema is NOT working.
- `match_activate_response.json` and `match_resolve_response.json` are
  [ASSUMED]; no battle has been started or resolved.
- No fight has been observed in this session.
- `quest_list` content (Act 1 "All Fall Down", "Landing Site", rewards, map)
  is invented for the vertical slice, not original Kabam data.
- `account_data` resources/level, starter roster, tuning values are [ASSUMED].
- The old `REPORT.md` figures (100% combat, 85-90%, 50-55%) are not evidence.

## 6. Next step

Milestone commit: `5dcc0c4` (stage1+2a). Stage 2B partial report:
`report/stage2b_vertical_slice.md`.

1. Fix roster: determine the exact `BCGUserHero` / `BCGUserData` wire keys
   (start from `BCGUserHeroBase..ctor` RVA 0xA62348 and `OnBCGData` RVA
   0x168C7C4), or find a real `userData` dump. Then make one hero appear in
   `EDIT SQUAD`.
2. Once a team exists, tap START and capture `/quests/quest-begin/...` and
   `/matches/activate-match/...`; build the 1v1 battle slice.
3. Only after 2B, expand to other systems.
