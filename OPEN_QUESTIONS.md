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
