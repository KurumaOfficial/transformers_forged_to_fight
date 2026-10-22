# LEDGER: Учёт источников данных и значений сервера эмуляции
## Transformers: Forged to Fight (com.kabam.bigrobot v9.2.0)

Каждое значение, поле и массив, отдаваемые сервером `stub_server.py`, строго фиксируются в данном реестре с указанием источника происхождения.

### Обозначения источников:
- **`[CLIENT]`**: Извлечено напрямую из бинарного кода клиента (`libil2cpp.so`, `dump.cs`, `global-metadata.dat`, ассет-бандлы).
- **`[WIKI]`**: Восстановлено по архивным базам данных, руководствам сообщества и видеозаписям оригинала.
- **`[RUN]`**: Подтверждено экспериментальным запуском на устройстве/эмуляторе (устранило сбой, продвинуло flow).
- **`[ASSUMED]`**: Временное предположение / синтетическое значение для поддержания работы (подлежит уточнению).

---

## 1. Аутентификация и сессия (`/auth/*`)

| Эндпоинт / Поле | Значение в сервере | Источник | Обоснование / Ссылка в клиенте |
|---|---|---|---|
| `/auth/init` -> `anon_token` | `"anon_tf_stub_token_12345"` | `[CLIENT]` | `EB.Sparx.AnonAuthenticator` (`0x1621218`) ожидает непустую строку сессии |
| `/auth/init` -> `stoken` | `"sess_tf_stub_token_12345"` | `[CLIENT]` | Формат токена сессии Sparx (`Sparx.Session`) |
| `/auth/enumerate` -> массив аккаунтов | `[{"primary": True, "user": {...}, "authenticators": [...]}]` | `[CLIENT]` + `[RUN]` | `LoginAPI.Enumerate` (`0x1468B74`) вызывает `Response.get_arrayList()`. Требуется массив, иначе `Count=0` |
| `/auth/prelogin` -> `salt`, `challenge` | `"tf_stub_salt_98765"`, `"tf_challenge_abc"` | `[CLIENT]` | `LoginAPI.PreLogin` (`0x14690C4`) для хэширования пароля/токена |
| `/auth/login` -> `auth.device` | `True` | `[CLIENT]` + `[RUN]` | `LoginManager._PostInit` (`0x162B508`) проверяет `Dot.Bool("auth.device")` |
| `/auth/login` -> `endpoints` | Маппинг всех сервисов на `http://127.0.0.1:8080` | `[CLIENT]` + `[RUN]` | `EndpointConfig.SetEndpoints` (`0x161C5B0`) |

---

## 2. Профиль командира (`/account/data`)

| Поле | Значение в сервере | Источник | Обоснование / Ссылка в клиенте |
|---|---|---|---|
| `user.uid` | `"10001"` | `[ASSUMED]` | Локальный дефолтный ID командира |
| `user.name` | `"Commander"` | `[ASSUMED]` | Отображаемое имя в UI хаба |
| `user.level` | `10` | `[ASSUMED]` | Уровень разблокирует основные режимы без лок-гейтов |
| `user.xp` | `1000` | `[ASSUMED]` | Прогресс опыта командира |
| `user.energy`, `maxEnergy` | `70`, `70` | `[ASSUMED]` | Запас энергии для квестов |
| `user.gold` | `50000` | `[ASSUMED]` | Золото в верхней панели ресурсов |
| `user.energon` | `25000` | `[ASSUMED]` | Энергон в верхней панели ресурсов |
| `user.shards` | `500` | `[ASSUMED]` | Осколки кристаллов |
| `user.ore13` | `1000` | `[ASSUMED]` | Руда-13 для прокачки ботов |
| `privacySettings` | `{"friendsinvite": True, "alliancerequest": True, ...}` | `[CLIENT]` + `[RUN]` | Устранило `NullReferenceException` в `InvitesManager.InvitePrivacySetting` (`0x165D468`) |
| `invitesDB` | `{}` | `[CLIENT]` + `[RUN]` | Защита от NullRef в `InvitesManager.ctor` |
| `maxHelpsPerRequest`| `5` | `[CLIENT]` + `[RUN]` | Константа запросов помощи альянса в `InvitesManager` |

---

## 3. База персонажей и боевая конфигурация (`/bcg/getLoginData`)

| Поле | Значение в сервере | Источник | Обоснование / Ссылка в клиенте |
|---|---|---|---|
| `heroes` | Каталог персонажей (Optimus Prime, Bumblebee, Megatron, Barricade) | `[CLIENT]` + `[WIKI]` | Идентификаторы персонажей из `global-metadata.dat` (`character_data`) |
| `attributeGrowthDefs`| Описание кривых роста статов | `[CLIENT]` + `[RUN]` | Обязательная коллекция в `BCGManagerBase.OnBCGData` (`0x168CFB4`) |
| `statMods`, `statModAppears` | Базовые модификаторы характеристик | `[CLIENT]` + `[RUN]` | Проверяются в `0x168D490` ("No Stat Mods") |
| `blueprints`, `evoBlueprints`| Рецепты эволюции и рангов | `[CLIENT]` + `[RUN]` | Проверяются в `0x168E870` ("No evo blueprints") |
| `synergyBonuses` | Таблица синергий классов | `[CLIENT]` + `[RUN]` | Проверяется в `0x168EBA0` ("No synergy bonuses") |
| `attackValues` | Сетка базовых атак | `[CLIENT]` + `[RUN]` | Проверяется в `0x168EED0` ("No attack Values") |
| `blueprintBonuses` | Бонусы рангов | `[CLIENT]` + `[RUN]` | Проверяется в `0x168F200` ("No Bonus Values") |
| `heroClasses` | 6 классов: Scout, Tech, Demolition, Tactician, Brawler, Warrior | `[CLIENT]` | Константы классов BCG |

---

## 4. Конфигурация базы игрока (`/base/active`, `base_mission`)

| Поле | Значение в сервере | Источник | Обоснование / Ссылка в клиенте |
|---|---|---|---|
| `theme` | `"primordial"` | `[CLIENT]` + `[RUN]` | `assets/bundles/theme/primordial_base/prefabs/library_primordial_base.prefab` |
| `setName` | `"primordial_base"` | `[CLIENT]` + `[RUN]` | Предотвратило загрузку несуществующего префаба `library__base` |
| `map.gridDimension`| `1` | `[CLIENT]` + `[RUN]` | Размер координатной сетки для `Map.GetTile(x, y)` (`0x14849C8`) |
| `map.walkableCount`| `1` | `[CLIENT]` + `[RUN]` | Количество проходимых плиток базы (`0x1483F40`) |
| `map.visibleWalkableCount` | `1` | `[CLIENT]` + `[RUN]` | Количество видимых плиток базы (`0x1483F60`) |
| `map.pathData` | `[{"path": [{"x": 0, "y": 0}]}]` | `[CLIENT]` + `[RUN]` | **Критический ключ**: `Map.Deserialize` (`0x14837EC`) и `MapPath..ctor` (`0x14840FC`). Устранило NullRef в `PathAnalyzer` |
| `grid[0][0]` | `{"position": {"x": 0, "y": 0}, "start": True, "final": True, "walkable": True}` | `[CLIENT]` + `[RUN]` | Удовлетворяет требованиям `Map.startTile` (`0x1484088`) и `endTile` |

---

## 5. Система обучения и туториалов (`/tutorial/*`)

| Поле | Значение в сервере | Источник | Обоснование / Ссылка в клиенте |
|---|---|---|---|
| Ключ статуса | `"s": "completed"` | `[CLIENT]` + `[RUN]` | `TutorialUserData.ctor` (`0x15E2448`) парсит только ключ `"s"`, игнорируя `"state"` |
| Ключ ветки | `"current_bid": "close"` | `[CLIENT]` + `[RUN]` | `TutorialUserData.ctor` парсит ключ `"current_bid"`, а не `"currentBranchID"` |
| `FTE` | `"s": "completed"` | `[RUN]` (отклонение) | Обход стартового обучающего боя для перехода в `HomeFlow` |
| 36 туториалов (Shield, Raids, DailyMissions и др.) | `"s": "completed"` | `[CLIENT]` (список имён) + `[RUN]` (отклонение) | Список извлечен из `global-metadata.dat`. Временное отключение блокирующих модальных окон |

---

## 6. Тюнинг и системные параметры (`/tuning`)

| Поле | Значение в сервере | Источник | Обоснование / Ссылка в клиенте |
|---|---|---|---|
| `tuning.version` | `1` | `[ASSUMED]` | Версия словаря тюнинга |
| `tuning.combat` | Заглушка боевых констант | `[ASSUMED]` | Будет наполнено в Этапе 2B |


---

## 7. Квестовый протокол (обновление 2026-10-21)

| Поле | Значение | Источник | Доказательство |
|---|---|---|---|
| chapterCount | [0, 1] (1-based, index 0 dummy) | [STATIC]+[RUN] | BuildSummaryTable RVA 0x1039BE4; краш при [1] |
| summary ct/chapter/mission | 1/1/1 | [STATIC]+[RUN] | после добавления ключей появились Chapter 1 и тайл квеста |
| vailableQuests | массив Summary | [STATIC]+[RUN] | AddQuestSummarys RVA 0x10381F0 |
| showUI / group / 
ecommendMinLevel | правильные wire-ключи | [STATIC] | вместо showInUI/groupTag/
ecommendedMinLevel |
| quest-detail body | {hash,nonce,api,setId} | [RUN] | server/requests.jsonl 2026-10-21 21:09:11 |
| Act/Chapter/quest names, map, rewards | выдуманы | [ASSUMED] | quest_list.json |
| /quests/quest-progression values | выдуманы | [ASSUMED] | quest_progression.json |
| /bcg/getUserData / userData | эксперимент, не принят | [ASSUMED] | cg_user_data.json |

---

## 8. BCG roster, featured hero и quest-begin (2026-10-22)

| Поле / запрос | Значение | Источник | Доказательство |
|---|---|---|---|
| `/bcg/getLoginData` -> `userData` | обёртка `{userData:{...}, updates:{...}, deletes:{}}` | `[CLIENT]` + `[RUN]` | `UpdateUserData` RVA 0x1695AA8; ростер появился только с обёрткой |
| `updates.heroes[]` | массив словарей героев | `[CLIENT]` + `[RUN]` | `HandleUserDataUpdates` RVA 0x1695CC0; `BCGUserHeroBase..ctor` RVA 0xA62348 |
| `entity_type` героя | `"bot"` (не `"hero"`) | `[CLIENT]` + `[RUN]` | `BCGHelper.GetHeroes` -> `GetEntities("bot")` RVA 0xC1F41C/0xC210D4 |
| `bid` | `bumblebee_cin_dotm_2` | `[CLIENT]` (id из ассетов) | BOTS/EDIT SQUAD |
| `savedTeams` / `activeTeams` | **массивы**, не словари | `[CLIENT]` + `[RUN]` | `Dot.Array` в `HandleUserDataUpdates`; dict вызвал пустой ростер |
| `activeTeams[]` | `aid,type,modes,expire,heroes{bid:details}` | `[CLIENT]` + `[RUN]` | `BCGUserActiveTeam..ctor` RVA 0xA610F0; TOTAL 100 |
| `savedTeams[]` | `sid,heroes[]` | `[CLIENT]` | `BCGUserSavedTeam..ctor` RVA 0xA635C4 |
| id blueprint в каталоге | ключ **`id`**, не `blueprint` | `[CLIENT]` + `[RUN]` | `BCGBlueprintBase..ctor` RVA 0xC15708; без `id` — «does not exist in BCG data» |
| `featuredhero` | в `/account/data`, `{cdn,orderType,heroes[]}` | `[CLIENT]` + `[RUN]` | `FeaturedHeroManager.Connect` RVA 0xB565B4; BOTS перестал падать |
| `/bcg/getBaseHeroData` | ответ — массив `BCGHeroDetails` | `[CLIENT]` + `[RUN]` | `BCGAPI.GetHeroBaseAttributes` RVA 0xC120F4; запрос rank 5 |
| `/bcg/setSavedTeam` | запрос `{teamID,heroes[]}`; ответ — полный BCG + обёртка userData | `[CLIENT]` + `[RUN]` | requests.jsonl 2026-10-22 18:20 |
| `/quests/quest-begin/{qid}` | запрос `{quitExisting,hash,api,setId,tm0..}`; ответ `{activeQuests:{qid:{...,teamData}}}` | `[CLIENT]` + `[RUN]` | `QuestsManager.BeginQuest` callback RVA 0xCDD210; карта загрузилась |
| map grid | квадратная `gridDimension × gridDimension` | `[CLIENT]` + `[RUN]` | `EB.Missions.Map.Deserialize`; 3×1 -> ArgumentOutOfRange |
| map entities | нельзя выдумывать | `[CLIENT]` + `[RUN]` | `MapTile.Deserialize`; неизвестный boss -> NullReference |
| `/quests/quest-movedir/{qid}/{dx}/{dy}` | запрос наблюдён; ответ `progression` + `teamData` | `[CLIENT]` + `[RUN]` | requests.jsonl 2026-10-22 18:22, 18:31; бот пока не двигается |
| `/quests/quest-quit/{qid}` | запрос наблюдён | `[RUN]` | requests.jsonl 2026-10-22 18:31 |

### Отрицательные результаты (2026-10-22)

| Вариант | Результат | Вывод |
|---|---|---|
| `userData.heroes` плоским блоком | ростер пуст | нужна обёртка `{userData,updates,deletes}` |
| `heroes` словарём / camelCase / с `id`,`uid`,`modes` | ростер пуст | ключи и обёртка важнее дополнительных полей |
| `entity_type: "hero"` | ростер пуст | `GetHeroes` читает `entities["bot"]` |
| `savedTeams`/`activeTeams` словарями | команда не сохраняется | клиент читает массивы |
| каталог с ключом `blueprint` вместо `id` | `HeroData.CreateForDisplay ... does not exist` | id blueprint = `id` |
| `featuredhero` только в `/auth/login` | BOTS NRE | эффективный источник — `/account/data` |
| `/bcg/getBaseHeroData` -> `{}` | NRE в callback | нужен массив `BCGHeroDetails` |
| `setSavedTeam` -> `{}` / плоский userData / полный каталог без обёртки | команда откатывается | нужен полный каталог + обёртка userData |
| `quest-begin` -> объект квеста без `activeQuests` | ошибка «unknown error» | нужен `{activeQuests:{qid:...}}` |
| `quest-begin` -> `activeQuests` без `teamData` | команда не применяется | `teamData` обязателен |
| карта 3×1 при `gridDimension:3` | `ArgumentOutOfRangeException` в `Map.Deserialize` | сетка квадратная |
| выдуманный entity в тайле | `NullReferenceException` в `MapTile.Deserialize` | убрать entities до реальных boss id |
| `quest-movedir` -> `{}` | бот стоит, pending-состояние | нужен `progression` + `teamData`; схема ещё уточняется |
| `quest-movedir` -> `progression` + `results[actionType=1]` + `teamData` | запрос уходит, бот не двигается, исключений нет | клиент, вероятно, ждёт sync/async-сообщение, а не только HTTP result |

### Локализация: 7 869 против 7 994
Текущий экстрактор (`work/extract_all_localization.py`) находит **7 869 уникальных ключей** `k` в 240 файлах `assets/bin/Data` (117 923 сырых вхождения, много языковых копий). Цифра 7 994 взята из старого `REPORT.md`/`generate_final_report.py` и текущим экстрактором не воспроизводится. Разница 125 не объяснена; вероятные причины — другой regex/набор файлов или учёт дублей/пустых значений в старом отчёте. [STATIC] для 7 869; 7 994 — [ASSUMED]/legacy.

---

## 9. Movedir: отрицательные и положительный результат (2026-10-22)

| Вариант ответа `/quests/quest-movedir` | Результат | Вывод |
|---|---|---|
| `progression` version 1 + `currentPos` + `cleared` | бот стоит, 11% | недостаточно |
| `progression` version 2 + `currentPos` + `cleared` | бот стоит, 11% | версия не решает |
| `progression` + top-level `currentPosition`/`playerPosition`/`currentTile` | бот стоит, 11% | top-level поля игнорируются |
| `progression` + `clearedTiles`/`percentComplete` | бот стоит, 11% | старые ключи не читаются |
| `results: [{actionType:1, actionPos, actionTile}]` | бот стоит, 11% | `actionType` не тот ключ |
| `results: [{action:"moveto", moveto:{x,y}}]` + `progression` | **бот перешёл на (1,0), 22% EXPLORED** | **рабочая схема** [RUN] work/r75.png |
| `results` + `battle` action с минимальным `battleEnemy` | ход есть, `/matches/activate-match` не вызван | battle-action требует валидного entity/полей |

Источник схемы: `QuestActionResult..ctor` (`RVA 0xEA28BC`) читает строку `action`
и под-объект с тем же именем (`moveto`, `teleport`, `battle`, ...); `moveto`
читает `x`/`y`. `progression` применяется `ActiveQuest.UpdateProgress`
(`RVA 0xC3A478`). [STATIC]+[RUN]

## 10. Явно [ASSUMED] значения

| Значение | Статус | Где |
|---|---|---|
| featured hero Optimus (`optimus_c_tf_t3`, rank 4/5, level 40) | [ASSUMED] | `server/data/account_data.json`, `bcg_login_data.json` |
| Bumblebee 100 (rank 1, level 1, статы 1000 HP / 120 ATK / rating 100) | [ASSUMED] | `server/data/bcg_login_data.json` |
| Ресурсы (gold/energon/shards/ore) и уровень командира | [ASSUMED] | `server/data/account_data.json` |
| Карта 3×3, названия Act/Chapter/Quest, награды | [ASSUMED] | `server/data/quest_*.json` |

---

## 11. Боевой тайл: три варианта (2026-10-22)

| Вариант | Состав | Результат | Вывод |
|---|---|---|---|
| 1 | `scaledBossTable.enemy1` + tile entity `{entityType:"boss",boss:"enemy1",type:"boss"}`; `characters,rank,level,sig_lvl,flvl,aiType,aiString,aiPer,mapOverride,todIndex` | `Error deserializing EB.Missions.Entity (bossTableId = enemy1, type = boss)`, затем NRE в `MapTile.Deserialize` | запись босса неполная |
| 2 | + `uid,key,hi,type,baseType` | ошибка Entity исчезла, NRE в `MapTile.Deserialize` остался | не хватает полей тайла/сущности |
| 3 | + `bg:false,bt:[],ab:[],sockets:{}` на всех тайлах | NRE в `MapTile.Deserialize` остался | не хватает чего-то ещё; `/matches/*` не вызван |

Память после обычного хода (без entity): `ActiveQuests` = 1
(`story_act1_ch1_m1`), `pendingProgressionCount = 0`, `progression.version = 2`,
`currentPos = (1,0)`, `currentFightId = null`, `currentBattleId = null`.
[RUN] `work/adb_legacy_quest.py`.

`ActiveQuest.ActivateMatch` (`RVA 0x10A0038`) требует `battleId` + героя;
обычный `moveto` его не вызывает. [STATIC]
