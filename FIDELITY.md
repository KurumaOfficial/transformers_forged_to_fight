# FIDELITY: Учёт точности воспроизведения и сознательных отклонений
## Transformers: Forged to Fight (com.kabam.bigrobot v9.2.0)

В данном документе фиксируются все временные допущения, упрощения и сознательные отклонения от оригинального серверного поведения, введённые для достижения вех разработки, а также план их поэтапной ликвидации (технический долг).

---

## 1. Реестр сознательных отклонений (Fidelity Deviations)

| ID | Компонент | Текущее поведение заглушки | Поведение оригинального сервера | Причина отклонения | План устранения |
|---|---|---|---|---|---|
| **DEV-001** | **Система обучения (FTE и 36 туториалов)** | Сервер отдаёт все 36 туториалов со статусом `"s": "completed"` в `/tutorial/get-login-data`. | Новый игрок начинает с `FTE` (`FTEIntroCutScene` -> `FTEIntroFight`), затем последовательно проходит `ShieldTutorial`, `BotPlacement` и др. | Необходимость прямой проверки загрузки 3D базы (`HomeFlow`) и ассетов без блокировки в обучающем бою. | После реализации боевого среза (Этап 2B) реализовать пошаговое прохождение веток туториала с сохранением прогресса в DataStore. |
| **DEV-002** | **Профиль и ресурсы командира** | Статично задан 10 уровень, 50 000 золота, 25 000 энергона, 500 осколков в `/account/data`. | Новый игрок стартует с 1 уровня, 0 энергона, ограниченного стартового золота и растет по кривой опыта. | Исключение блокировок интерфейса по уровню игрока (level-gating) при валидации экранов хаба. | Внедрение персистентной БД игроков (SQLite/JSON), начисление опыта и ресурсов за миссии. |
| **DEV-003** | **Сетка базы игрока (BaseBoard)** | Одноэлементная сетка 1x1 (`gridDimension: 1`, плитка (0, 0)) с темой `"primordial"`. | Полноразмерная Cybertron-база с десятками слотов под строения (генераторы, хранилища, реликвии, защитные платформы). | Минимизация зависимостей для выявления минимально допустимого датасета `Map` и устранения краша `PathAnalyzer`. | Добавление полной матрицы сокетов (`Sockets`, `Buildings`, `AvailableBuildings`) по дампу префаба `library_primordial_base`. |
| **DEV-004** | **Ростер персонажей** | Захардкоженный список из 4 ботов (Optimus Prime 2*, Bumblebee 1*, Megatron 2*, Barricade 1*). | Персонажи выдаются из кристаллов (gacha), сохраняются с уникальными UID, уровнем, рангом и способностями. | Обеспечение клиентов ботами для тестирования переходов UI. | Полноценный сервис инвентаря и ростера с сохранением состояний прокачки. |
| **DEV-005** | **Квесты и прогрессия** | Заглушки `/quests/quest-list`, `/quests/quest-active`, `/quests/quest-progression` отдают минимальные пустые списки. | Сервер возвращает акты, главы, миссии, узлы карт, награды за 100% исследование и сундуки. | Концентрация усилий на прохождении экрана загрузки и хаба. | **Задача Этапа 2B**: спецификация и наполнение 1-го сюжетного квеста. |

---

## 2. Черновые метрики (LEGACY, не доказаны; не использовать в отчётах)

- **Аутентификация и сессия (`/auth/*`):** **95%** (полная совместимость со схемой Sparx, HMAC-SHA1 сигнатуры проверяются клиентом).
- **База персонажей (`/bcg/*`):** **85%** (все 8 обязательных коллекций и кривые роста приняты клиентом без ошибок).
- **Карта базы (`/base/*`, `Map`):** **75%** (схема `pathData` и `MapTile` валидна, 3D сцена рендерится, требуется расширение сокетов).
- **Боевая математика (`/tuning`, `BCGAttributeDataBase`):** **30%** (таблицы приняты клиентом, но формулы расчета урона подлежат исследованию в 2B).
- **Квесты и сюжет (`/quests/*`):** **20%** (структура эндпоинтов известна, наполнение карт миссий запланировано на 2B).


---

## 3. Обновление 2026-10-21 (по фактическому запуску)

| ID | Компонент | Фактическое состояние | Доказательство |
|---|---|---|---|
| DEV-006 | Содержимое квестов | Act 1 «All Fall Down», Chapter 1 «Arrival», миссия «Landing Site», карта 3x1, награды — **выдуманы** для вертикального среза | [ASSUMED], server/data/quest_list.json |
| DEV-007 | Ростер | Пуст. /bcg/getLoginData содержит каталог, но userData/BCGUserHero не принят клиентом. EDIT SQUAD пуст, START заблокирован | [RUN] 2026-10-21, work/FINAL_story_chapters.png, stage1_logcat_full_final.txt |
| DEV-008 | Туториалы | Все 36 помечены completed (обход) | [RUN], сохраняется |
| DEV-009 | Ресурсы/уровень | 0/0 в верхней панели, Lvl 0; значения account_data не совпадают с UI | [RUN] |
| DEV-010 | Бой | Не запускался. match_activate_response.json / match_resolve_response.json не проверены | [NOT OBSERVED] |

Честная формулировка: клиентская часть (APK, ассеты, рендер, UI) — оригинальная;
серверная часть на данный момент — каркас. Доля восстановленных серверных
значений близка к нулю, кроме схемы Sparx и нескольких wire-ключей.

---

## 4. Обновление 2026-10-22 (ростер и вход в квест)

| ID | Компонент | Фактическое состояние | Доказательство |
|---|---|---|---|
| DEV-007 | Ростер | **Схема восстановлена**, ростер работает: BOTS показывает Bumblebee 100, EDIT SQUAD даёт TOTAL 100. Значения статов/ранга/ID — [ASSUMED] | [RUN] work/r13.png, work/r38.png, spec/bcg_userdata.md |
| DEV-011 | Featured hero | BOTS больше не падает; `featuredhero` добавлен в `/account/data` с Optimus. Реальная ротация Kabam неизвестна | [RUN] work/run_logcat_8.txt |
| DEV-012 | Квест-карта | `quest-begin` принят, карта 3×3 загружается, бот на старте. Карта/контент выдуманы | [RUN] work/r47.png, work/r51.png |
| DEV-013 | Движение по карте | `quest-movedir` отправляется, но бот визуально не двигается; клиент остаётся в pending-progression | [RUN] requests.jsonl 18:22/18:31 |
| DEV-010 | Бой | Не запускался. `match-activate`, `match-loaded`, `match-resolve` не наблюдены | [NOT OBSERVED] |

Честная оценка: клиентская часть оригинальная; серверная схема ростера и
входа в квест подтверждена запуском, но **числовые данные** (статы, ранги,
награды, карта) по-прежнему синтетические. Боевая часть не начата.

---

## 5. Обновление 2026-10-22 (ход по карте подтверждён)

| ID | Компонент | Фактическое состояние | Доказательство |
|---|---|---|---|
| DEV-013 | Движение по карте | **Работает**: `results:[{action:"moveto",moveto:{x,y}}]` + `progression`; бот перешёл на (1,0), 22% EXPLORED | [RUN] work/r75.png, requests.jsonl 18:55 |
| DEV-014 | Бой из карты | `battle`-действие с минимальным enemy не вызвало `/matches/activate-match`; нужен валидный entity/`currentBattleId` | [RUN] 18:55–18:56, `/matches/*` отсутствуют |
| DEV-007 | Ростер | Схема работает; **значения** Optimus/Bumblebee/статы — [ASSUMED] | [RUN] work/r13.png, work/r38.png |
| DEV-009 | Ресурсы/уровень | По-прежнему синтетические, UI показывает Lvl 0 / 0/0 | [RUN] work/r75.png |

### Таблица верности (честно, по подсистемам)

| Подсистема | Схема/wire | Данные/значения | Комментарий |
|---|---|---|---|
| APK, ассеты, UI, рендер | 100% оригинал | 100% оригинал | клиент не менялся, кроме endpoint + подписи |
| Sparx auth/envelope | подтверждена [CLIENT]+[RUN] | токены/аккаунт [ASSUMED] | вход до хаба работает |
| BCG каталог | ключи подтверждены [CLIENT] | статы/ранги/ID [ASSUMED] | 13 wire-gotchas в `spec/wire_gotchas.md` |
| BCG userData/ростер | подтверждена [RUN] | герой и статы [ASSUMED] | BOTS + EDIT SQUAD работают |
| Квест-лист/детали | ключи подтверждены [RUN] | контент [ASSUMED] | 1.1 Landing Site выдуман |
| quest-begin/карта | подтверждена [RUN] | карта 3×3 [ASSUMED] | карта грузится |
| quest-movedir | подтверждена [RUN] | прогрессия [ASSUMED] | ход работает |
| Бой (`/matches/*`) | не наблюдалась | нет данных | 0% подтверждено |
| Экономика, магазин, PvP, альянсы | не начато | нет данных | вне текущего среза |

Формулировка: клиентская часть — оригинальная; серверная **схема** ростера,
квеста и хода подтверждена запуском, но **числовые данные** остаются
синтетическими. Боевая часть не подтверждена.

### DEV-015 — боевой тайл и префайт (2026-10-23)

Точная NRE-ветка: `entities` — словарь, а не массив
(`MapTile.Deserialize 0x1485094/0x1485098`). Босс рендерится (6★, 8888).
`battle`-действие (`QuestActionResult..ctor 0xEA28BC`) — правильный
триггер: после movedir клиент открыл префайт «SELECT YOUR BOT».
[RUN] `work/battle3.png`, `work/pre2.png`.

Локальная команда пустая: `localPlayer.team` — `List` count 0; «+»/FIGHT
даёт NRE в `PrefightScreenPresentation.GetNewScale(HeroData robot)`.
`/matches/activate-match` не вызван; бой **0% подтверждён**.
[RUN] `work/read_prefight_state.py`, logcat 14:35/14:46.

**2026-10-23, team:** `QuestUserInfo.team` — словарь, внутри
`List<QuestUserHero>`; ключ = blueprint, значение: `hp` (float,
абсолютное), `pi`, `sig_lvl`, `stat_mods`, `sig_mods`. `level/rank/max_hp`
в `QuestUserHero` нет. `TeamIsKnockedOut` (`0x1181DC8`) при count 0
возвращает true; память после попытки 3: `currentBattleId=battle1`,
`localPlayer` есть, `team` count 0. `/matches/activate-match` не вызван.

**2026-10-23, activeTeams:** `BCGUserActiveTeamDict` — словарь по
`activityID`, `BCGUserActiveTeam.heroes` — словарь, из которого
строится `TeamHeroes` (`List<BCGHeroDetails>`). Ответ переведён на
`activeTeams`-словарь + `heroes`-словарь с `blueprint/rank/level/hp/max_hp`;
надпись «ALL KNOCKED OUT» исчезла, но команда всё ещё пустая,
«+»/FIGHT даёт NRE, `/matches/activate-match` не вызван.

**2026-10-23, A1/A2/S1/S2:** `GetCurrentTeam` ищет active team
по `ActiveQuest.mode`; mode-клоны добавлены, prefight пуст. `QuestUserInfo.team`
внутри List, JSON — dict; верхнеуровневый team переведён в dict. Smoke PASS,
golden regression 9/9 PASS; `/matches` не вызван.

**2026-10-23, wiki/data:** synergy 40/44; 13 topic files with
as_of/latest; client-only map 13+7+5; manifest 5154/5154 verified
after 5 stale-hash corrections; C5 catalog 59 packs; C2 formula partial.

## Updated fidelity table — 2026-10-23

| Area | Level | Basis |
|---|---|---|
| Login/session, BCG catalog, quest list/begin/detail/move | good | accepted by client; map and prefight open [RUN] |
| Prefight roster/team, FIGHT | low | team empty, GetNewScale NRE, no /matches [RUN] |
| Match protocol | none/assumed | no activate-match capture |
| Wiki text/history/File descriptions | high | 5154/5154 manifest verified |
| Wiki images | medium | 694/2752; 209 host 403 |
| Wiki bot stats/abilities | medium-high | 44 bots, synergy 40/44, some fields missing |
| Client bot catalog | high for IDs/classes | 59 packs, 59 class/faction, 39 stars |
| OpenAPI/tuning/localization | partial | C1/C3/C4 open |

### 2026-10-24: prefight provider

CORRECTED 2026-10-25: `PreFightScreen._model` is **not** null. The live object
has a `PrefightScreenData` model; the old OnFight NRE came from a null `_enemy`
because `scaledBossTable.enemy1.key` was the entity id instead of the boss
blueprint. See `docs/prefight_flow.md` §12–14.
The provider is fetched only via
`InterfaceInjector.Get<IPrefightDataProvider>` (`0x11E7640`) in
`CacheReferences` (`0xE38F08`). Live injector state: tag `tform`, 78
interfaces, one persistent (`IAdsProvider -> TFormIronSourceAdsModel`),
all but entry 0 default-only. The current roster/team probes show
`TeamHeroes count=1` and `localPlayer.team count=1`, so team-data
variants cannot fix the prefight until the provider is resolved.
[RUN] `work/read_bcg_memory.py`, `work/read_tag.py`,
`work/read_injector.py`; [STATIC] `0xE397BC`, `0xE38E4C`, `0x11E7640`.

**2026-10-24, R1 roster:** All 59 client bot packs are granted and listed
in BOTS (`tests/smoke/09_bots.png`); a non-Bumblebee details screen
(Windblade) opens without NRE (`10b_bot_info.png`). Class/faction from
`bot_catalog_real.json`; only 12 bots have wiki star-1 HP/ATK, the other
47 use [ASSUMED] 1000/120. The card shows rating 300 vs wiki 264 for
Windblade, so R2 is still open. Abilities are `NO ABILITIES`, special
attack names are raw `M1_SPECIAL_ATTACK_NAMEID_*` keys, and the synergy
box is empty for Windblade (R3/R4 open). `teamSizeMax=1` is a deliberate
deviation for the 1-bot test quest.

**2026-10-24, I1/I2:** `docs/interfaces.md` lists all 78 injector interfaces.
`IPrefightDataProvider` is entry 69, default-only; `IAdsProvider` is the only
persistent/tform entry. No ad-network request observed. S2 prints xfail/target
status. T5 is MASTER_PROMPT v4.3.

## 2026-10-25 fidelity update

| Area | Level | Basis |
|---|---|---|
| Login/session, BCG catalog, quest list/detail/begin/move | good | 90-mission list accepted; prefight opens [RUN] |
| Prefight roster/team, FIGHT | **medium-high** | Bumblebee vs Rhinox, HP/FIGHT enabled; activate-match sent [RUN] |
| Battle scene / combat | low/blocked | `InitPlayer` NRE; no match-loaded/resolve [RUN] |
| Match protocol | partial | first activate request captured; response ASSUMED |
| Wiki text/history/File descriptions | high | 5154/5154 manifest verified |
| Wiki images | medium | 696/907 (2 recovered), 209 403, priority 2/36 |
| Wiki bot stats/abilities | medium | 44 pages; 12 star-1; 47 ASSUMED; abilities raw |
| Client bot catalog | high | 59 packs, classes/factions |
| OpenAPI/tuning/localization | partial | C1/C2/C3 partial |
| Infrastructure | partial | SQLite opt-in, routing central, plans written |

## 2026-10-25 late update

| Area | Level | Basis |
|---|---|---|
| Prefight/FIGHT | **medium-high** | provider fixed earlier; activate-match sent [RUN] |
| Battle scene | low/blocked | model id + tags fixed; `PlayerAttributes.Init` HashSet NRE; no match-loaded [RUN] |
| Quest list/detail/begin/move | **good** | 90 missions; dynamic detail/begin/movedir; smoke PASS [RUN] |
| Map generator | **medium** | validated 9-tile template, per-qid hash; entity still template [RUN] |
| Boss data | **medium-high** | 60/90 client ids; 1.1 Rhinox, 1.4.2 Sideswipe [WIKI+RUN] |
| R1 stats | **partial** | LOBO 14.3%/16.4% no anchor; 4.1%/2.8% one anchor; 37 derived [DERIVED] |
| R2 rating | **partial** | fit RMSE 7.77, not client formula [DERIVED] |
| Git/publication | **audit done** | no secrets/APK/libil2cpp in history; remote has binary/wiki dumps/personal path; no push until user decision |
| Emulator | **improved** | windowed angle stable; watchdog + snapshot added |

## 2026-10-25 hygiene/schema update

| Area | Level | Basis |
|---|---|---|
| Git dangling audit | done | exact APK/zip originals identified; no deletion |
| Pre-commit guard | done | blocks binaries/large/keys/personal path |
| Quest routing | **good** | separate module; behavior unchanged; smoke PASS |
| Boss coverage | **improved** | 70/90 ids; 20 gaps documented |
| R1 coverage | partial | 37 WIKI / 22 ASSUMED + uncertainty |
| R2 rows/regression | partial | 236/142 rows; non-integer fit |
| Ability schema | partial | core fields/RVAs + raw-id source blocked |
