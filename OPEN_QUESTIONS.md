# OPEN QUESTIONS

## 1. Коллекция автора

**https://1drv.ms/u/s!ApD2f3dIXZ_7yjf4KMB9YQzgWQCG?e=jiLxKN**
(`User:KRBrickBot`, revid 10874).

OneDrive отдаёт `isAuthenticated:false`; без входа нет `downloadUrl`.
Скачивание не выполнено. Ссылка не входит в zip.

## 2. Team / prefight / ActivateMatch

- `QuestUserInfo.team` — JSON-словарь (`Dot.Object 0x103D5D8`), внутри
  `List<QuestUserHero>`; ключ = blueprint. Значение: `hp` (float,
  абсолютное), `pi`, `sig_lvl`, `stat_mods`, `sig_mods`. Полей
  `level/rank/max_hp` в `QuestUserHero` нет.
- `TeamIsKnockedOut` (`0x1181DC8`): count 0 -> true; иначе любой HP>0 ->
  false. Поэтому «ALL KNOCKED OUT» при team count 0 — согласовано.
- Память после попытки 3: `currentBattleId=battle1`, `localPlayer` есть,
  `team` List count 0. Словарь с `hp=1000`, `pi=100`, base-blueprint не
  был принят; тип/формат значения не решён.
- `PreFightScreen.OnFight` (`0xE397BC`) -> `PrefightScreenData.OnFight`
  (`0xE3E778`); HP префайта берётся из `TeamData.GetHP` (`0x10E1AE4`),
  не из `QuestUserHero.HP`.
- `activeTeams` — словарь по `activityID` (`BCGUserActiveTeamDict`),
  `BCGUserActiveTeam.heroes` — словарь. После перевода на эту форму
  «ALL KNOCKED OUT» исчез, но команда пустая, «+»/FIGHT — NRE.
- `ActiveQuest.ActivateMatch` (`0x10A0038`) прямых BL не имеет; вызов
  через UI/делегат, требует непустые `battleId` и `hero`.
- `/matches/activate-match` не вызван. `match_activate_response.json` —
  `[ASSUMED]`; точный JSON-контракт ответа не подтверждён.
- Frida/gadget/патчи не использовались.

## 3. Wiki

- Fandom: 3613 = 817 non-File + 2796 File. Все 817 non-File — full
  history+HTML; все 2796 File descriptions — latest revision.
- TFWiki: 8 FTF pages.
- Cargo нет; Scribunto на Fandom есть, `Module:` = 0.
- Images: 694/2752; 209 errors (mostly 403). Remaining resumable.
- Parsed: 44 bots, 252 pages; matrix `bot_matrix.json`; ID map
  `id_map.json`; versions `versions.json` (cutoff 2023-01-13, 96 changed,
  11 created after).
- `Sharkticon` (no numeric table) и layout-шаблон — unparsed.
- Скрытые статы (crit/armor/block) не выдумывались.

## 4. Attribution

URL/revid в raw и manifest; CC BY-SA 3.0 для TFWiki; Fandom — условия
сайта. Личное использование.

- A2: `QuestUserInfo.team` JSON принят как dict на верхнем уровне,
  но memory `localPlayer.team` count 0; точная вложенность (users/localPlayer)
  не подтверждена. [RUN]
- A5: `/matches/activate-match` не вызван; тела и `FighterInitData`
  остаются `[ASSUMED]`.
- A3: harness variants не запускался пакетом 10–20; smoke/golden готовы.

- C1: OpenAPI quest endpoints still `[NOT OBSERVED]`; depth for
  login/tuning/gacha/shop/etc. is partial. [STATIC]
- C3: full TuningManager key/default scan not done; only four defaults
  verified in `server/data/tuning_client_defaults.json`.
- C4: only 8 `D_STAT` keys found by the JSON-object extractor; full
  ability localization needs another text-asset extraction path.
- C2: rating pseudocode partial; need runtime `BCGAttributeData` dump.
- W3: topic files are curated page sets, not complete numeric tables for
  every event/relic/crystal chance; values missing where not in wikitext.

## 5. Remaining P0/P1/P2 blockers (2026-10-23)

- A4: plus/FIGHT NRE is `GetNewScale` dereferencing null `robot` or
  `robot+0x48`; roster never opens. [RUN]+[STATIC]
- A5: `/matches/activate-match` not called; all match bodies `[ASSUMED]`.
- A3: 10 variants run; none filled TeamData. Harness supports more variants.
- W5: 209 image errors are all HTTP 403; no bypass.
- C1: OpenAPI has 54 paths but login/catalog/gacha/shop depth is partial.
- C3: only four TuningManager defaults verified.
- C4: only eight D_STAT keys extracted; full localization path unknown.
- I1: only autorefresh metadata extracted; full routing/data split open.

- C4 (update): 3315 `D_STAT`/`ID_STAT` entries extracted from binary assets;
  language/mapping to bot ability names still needs a per-language selection
  and wiki cross-check.
- W5 (update): `data/wiki/image_index.json`; 694 unique images, 209 403s.
- A3 (update): 10 variants run; v07 (activeTeams as dict) broke login, so the
  login parser expects a list. This narrows the next test to team-element
  contents, not the activeTeams container itself.

## 6. Prefight provider blocker (2026-10-24)

- `PreFightScreen._model` (`+0x98`) is **null**; FIGHT NRE is
  `PreFightScreen.OnFight` `0xE397BC`, and no team code is reached. [RUN]
- Model source: `CacheReferences` `0xE38F08` ->
  `InterfaceInjector.Get<IPrefightDataProvider>` `0x11E7640`. [STATIC]
- Live injector: tag `tform`, 78 interfaces, persistent = 1
  (`IAdsProvider -> TFormIronSourceAdsModel`). Under `tform` only entry 0
  resolves; the other 77 entries are `default`-only. [RUN]
- Open: is `IPrefightDataProvider` one of the default-only entries, or
  missing from the map? Need a runtime resolution of the 78 interface
  names (RuntimeType handles are Mono-style handles, not Il2CppClass
  pointers) or a call-site trace.
- Team is no longer the blocker: active team and `localPlayer.team` both
  count 1 with the current stub. [RUN]
- P0 S: `smoke_test.py` needs polling instead of fixed sleeps; it
  false-FAILs on a slow cold boot. [RUN]

### 17. P0 S completed (2026-10-24)

- `smoke_test.py` now has robust boot waiting, fast/full modes, BOTS,
  bot popup, bot INFO, EDIT SQUAD, prefight FIGHT click, and memory
  probes. [RUN] full PASS, team count 1, model NRE true.
- `read_prefight_state.py` List bug fixed; `work/read_bcg_memory.py` and
  the fixed script agree on team count 1.
- `golden_regression.py` re-recorded (9/9 PASS) after the quest-list
  key correction and current movedir battle stub.
- `resume.ps1` added.
- A5 (arena/special unlock) remains open: the UI still shows Lvl 0 and
  the account level is not applied; the prefight provider blocker would
  also apply to those modes unless they use a different provider.

## 7. R1/R2/R3/R4 (2026-10-24)

- R1: 59 client bots are in the catalog and BOTS; Windblade details/INFO
  open without NRE. [RUN]
- R2: display rating 300 vs wiki 264 for Windblade; the client formula
  inputs are not matched. [RUN]+[WIKI]
- R3: details show `ABILITIES: NO ABILITIES`; special attack names are
  raw `M1_SPECIAL_ATTACK_NAMEID_*` keys. Need the ability catalog and
  localization mapping. [RUN]
- R4: synergy box is empty for Windblade even though `syn_autobots`
  exists; need the client's synergy eligibility/tag rule. [RUN]
- Data gap: 47/59 bots have [ASSUMED] rank-1 stats (no wiki star table).

### C4 update (2026-10-24)

- 7869 is correct for localization; 7994/7996 includes 127 AI/tuning keys.
- 3315 stat entries are exact; 3332 remains legacy/unreproducible
  (17 unaccounted). `data/wiki/ability_localization_client.json` is the
  current authoritative extraction.

## 9. P0 provider: registry resolved (2026-10-24)

- `IPrefightDataProvider` is injector entry **69** with only
  `default -> PrefightScreenData`; live tag is `tform`. `Get<T>` has a
  default fallback in code, so the null is likely a `ContainsKey`/type
  identity mismatch or a wrong call-site interface, not a missing
  implementation.
- Need to resolve the `0x2BE2870` method-info generic argument; compare it
  with entry 69. Then test settings/profile (default-only entries) under
  `tform` to distinguish tag vs type identity.
- A5/A6: not yet run; A5 must test the boss-tile trigger and map/prefight
  registry snapshots; A6 variants cannot alter a static registry, only the
  trigger.

## 10. Current queue status (2026-10-24, v4 queues)

- A1/A2/A3/A4: **done enough to localize the null**: entry 69
  `IPrefightDataProvider` is default-only; `Get` has a default fallback;
  live tag is `tform`; `ContainsKey`/type-identity or the call-site generic
  argument is the remaining suspect. See `docs/prefight_flow.md`.
- A5: **not run** (boss-tile trigger timing/order). Next: tap the boss tile
  without `battle`, record; then moveto and battle in separate responses;
  probe registry at map/prefight.
- A6: **blocked by A1**: the registry is static and variants cannot change
  it. The 10 variants already run (v01–v10) plus the static registry show
  why; a 20-run matrix is deferred until the type identity/call-site is
  resolved.
- A7: blocked until FIGHT reaches ActivateMatch.
- A8: arena/special unlock not done; account level still displays 0.
- A9: `docs/frida_plan.md` updated; no Frida.
- S1: known_issues/xfail added to smoke.
- S2: golden diff + baseline tag + changelog added; 9/9 PASS.
- S3: 59-bot auto sweep not run; single Windblade evidence exists.
- S4: `work/check_all.ps1` added; unittests 14/14 PASS.
- R1: 59 bots, 12/59 wiki stats; 47 assumed.
- R2/R3/R4/R5/R6: open/partial as in report.
- Q1/Q2/Q3: `data/quests_real.json`; only 1.1 wired; full 66-mission
  quest-list and map generator not done.
- C1/C3: partial; C4 explained.
- W4/W5: not re-run.
- I1/I2: partial/design only.

## 11. A1 runtime dump blocked (2026-10-24)

- `PreFightScreen_TypeInfo` (`ScriptMetadata` Address `0x2D0D108`) contains a
  **metadata usage token** (`0x200086F7`), not an `Il2CppClass*`. The same is
  true for `WindowManager_TypeInfo` (`0x2D15FF8` -> `0x2000DD0F`).
- The class struct for `PreFightScreen` was not found by scanning the
  libil2cpp mappings for a pointer to the resolved `"PreFightScreen"` string
  (two metadata string occurrences tested). The class is therefore in a
  metadata-heap mapping, not in libil2cpp's r--/rw segments; a whole-process
  scan was too slow and timed out.
- Consequence: the read-only probe cannot yet dump `_model`, `_config`,
  `_presentationSCI`, `_presentation` and the window flags. Resolving the
  `Il2CppMetadataUsage` table (token -> class/type) or a targeted
  WindowManager instance is required. Frida is not allowed.
- What **is** proven: `CacheReferences` is called from `PreFightScreen.SetupWindow`
  (`0xE38E24`), and the only provider source is `Get<IPrefightDataProvider>`
  (`0x11E7640`); entry 69 is default-only. The null is a runtime type/`ContainsKey`
  or `Activator.CreateInstance` issue, not a missing implementation.
- `QuestboardHud is inactive` was observed once at 16:35:21; it is not present
  in every run and cannot yet be tied to the provider.

## 12. I1/I2/S2/T5 status (2026-10-24)

- I1 done: `docs/interfaces.md` (78 rows).
- I2 done: ads provider static + no network request observed.
- S2 done: check_all prints target checks and xfail state.
- T5 done: MASTER_PROMPT v4.3.
- Next independent items: S1 59-bot sweep; R1/R2; Q1/Q2; C1/C3; W1/W2.

## 13. R1 growth curve (2026-10-24)

- 36/44 wiki bots have >=3 stat-table rows. A linear rank+level fit is
  rejected (HP RMSE up to 7,267; Attack usually 50–250). Growth is a
  curve/table, not a plane. `spec/stat_growth_fit.md`,
  `data/wiki/stat_growth_fit.json`.
- 47 client bots without a star-1 table remain `[ASSUMED]`; do not use the
  fit as wiki data. Next: piecewise per-rank curves and the client
  `curves`/`attributeGrowthDefs`.

## 14. Battle init after activate-match (2026-10-25)

Prefight is fixed by the enemy-key data change; FIGHT sends
`/matches/activate-match/quests_fight`. The next failure is
`BattleArbiterInitState.InitPlayer` NRE. `FightFlow.FightInitInfo` has
`playerFighter` and `enemyFighter` both non-null; the enemy fighter has
`Blueprint` but `TeamData == null`, the player has both. No match-loaded
request. Three attempts used: (1) infer null model, (2) live prefight dump,
(3) live FightInitInfo dump. Next would need the exact asset/component that
is null in the loaded character prefab, or a real activate-match response.

## 15. Open after 2026-10-25

- **Battle init:** `BattleArbiterInitState.InitPlayer` NRE; `FightInitInfo`
  fighters/blueprints non-null, enemy `TeamData` null. Need the exact
  null source (asset/component or FighterData field) or a real
  `match_activate_response`. 3 attempts used; do not re-run without new data.
- **R2:** simple HP/ATK fit RMSE 7.77, coefficient on HP ~0; not the client
  formula. Need operand binding/selection-bias branch.
- **R3:** ability text source not found; client details show `NO ABILITIES`
  and raw `M1_SPECIAL_ATTACK_*` ids.
- **R4:** `synergyBonuses` data populated but not live-verified; specials raw.
- **S1:** 12/59 BOTS cards; finish with scrolling.
- **W1:** 34 priority 403/no-URL images.
- **T1:** payloads split; routing still central.
- **Emulator:** headless QEMU stalls/crashes after a few minutes; a fresh
  stable boot is required for further live work.

## 16. 2026-10-25 late blockers

- Battle: `PlayerAttributes.Init` HashSet collection null. Live `Blueprint.Tags`
  is non-null (count 2), so the exact instance/collection needs a breakpoint.
  ModelID was fixed by `JSONPaths.m="m"`; tags by `t`/`tags`.
- R1: no-anchor LOBO error 14.3% HP / 16.4% ATK; the requested 7–8% for 47
  no-table bots is not supported. 37 table-anchored bots are `[DERIVED]`.
- Git: remote contains binary screenshots, wiki metadata/data and
  `C:\Users\gameg`; cleanup plan prepared, no push/rewrite without consent.
- Emulator: headless QEMU unstable; windowed angle is the current mode.

## 17. 2026-10-25 late additions

- Git dangling objects identified; no deletion. Hook installed.
- Battle: ModelID/tags fixed; `PlayerAttributes.Init` HashSet NRE remains.
- Q3: 70/90 boss ids; 20 gaps in `data/boss_gaps.json`.
- R1: 37 WIKI / 22 ASSUMED; R2 rows built but not integer-exact.
- R3: `M1_SPECIAL_ATTACK_*` not found in retained assets; needs external table.
- T1: quest routing split done; T2/T3 done; backup/nightly scripts added.

## 2026-10-26 battle init resolved / next blocker

- **RESOLVED:** `PlayerAttributes.Init` `ArgumentNullException` was
  `BaseRangedDamageType` (null) passed to `DamageType..ctor`, which tail-calls
  `HashSet<string>..ctor`. Fixed with non-null damage-type lists in blueprints
  and characters; `bumblebee_cin_dotm` alias added. Battle reaches
  `BattleArbiterMainState` with two fighters.
- **OPEN:** The player stays at `BCGAttributeData.HP = 1.0` (HPMax 1050) while
  the enemy attacks; the hit-react loop does not end, no death, no
  `resolve-match`, no rewards, no return to map. Suspects: minimum-HP stat,
  missing animation event, or the server `hp`/`attributes` shape.
- **OPEN:** `HeroData.Create - blueprint 'bumblebee_cin_dotm' does not exist`
  was fixed by an alias, but the client still logs other null character data
  during prefight; verify the UI.
- **OPEN:** `/matches/match-loaded` is not sent for quests_fight; determine
  whether it is PvP-only or required for quest resolution.
- **OPEN:** 9 Starscream boss gaps remain; no 9.2.0 character pack.
- **OPEN:** R2 server-side `HeroRatingHP/Attack` formula still not derived;
  client combination formula is now exact.

- **NEW HARD BLOCKER (2026-10-26):** `FuseODRBlocker`/`FuseLoadingScreen` on
  top of `HudScreen`; Play Asset Delivery `assetmoduleservice` is unavailable
  on the emulator (`com.android.vending` missing). Battle logic runs behind the
  loading screen but input is blocked. Need the original ODR packs or a
  non-ODR data path; do not patch the client.

- **ODR:** `FuseODRBlocker` Open with 0 active/requested downloads, no pending
  WADs; `ODRManager` has no manifest and `_initAndGetManifestComplete=0`; no
  `/odr/*` request reaches the stub; PlayCore cannot bind to
  `com.android.vending` on the sideloaded emulator. Not an arena tag issue.
- **R2:** LP infeasible on raw HP/ATK; need server rating split.
- **S1:** `sweep_bots59.py` pagination added; clean 59/59 still blocked by
  the global ODR/navigation state; current evidence remains 12/59.

- **ODR:** normal `ODRManager.Initialize` does not call `InitAndGetManifest`;
  lazy `EnsureManifest` -> `ODRAPI.GetManifest` is not started because the
  bundle exists. Blocker global + PlayCore missing; PlayStore image not
  downloaded (permission empty).
- **Hidden stats:** battle path recalculates locally; need `heroes[rank]` /
  `attributeGrowthDefs` / `curves`, not flat getBaseHeroData.
- **R2:** equivalent split exists (`data/rating_table.json`), retail split
  still missing.
