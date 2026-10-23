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
