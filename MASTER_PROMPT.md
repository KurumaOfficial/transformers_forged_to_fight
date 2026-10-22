# MASTER_PROMPT — Transformers: Forged to Fight offline revival

Restored copy of the master prompt (2026-10-22). Canonical source: the user's
message of that date. If this file and the user's prompt disagree, ask the user.

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

## 6. Current blocker (as of 2026-10-22)
Roster was the blocker; it is now fixed. See STATE.md for the current blocker:
`quest-movedir` response is not committed (bot stays at start; pending
progression). Battle has not started.

### Roster findings (now verified)
- `/bcg/getLoginData.result.userData` must be the wrapper
  `{userData:{...},updates:{heroes,...},deletes:{}}`.
- Hero `entity_type` must be `"bot"` (GetHeroes reads `entities["bot"]`).
- `savedTeams`/`activeTeams` are arrays.
- Catalog blueprints use key `id`, not `blueprint`.
- `featuredhero` must be in `/account/data`.
- Details: `spec/bcg_userdata.md`.

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
