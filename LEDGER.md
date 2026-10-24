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

### 11.1 Точная причина NRE и положительный результат

`MapTile.Deserialize` читает `entities` через `Dot.Object` (IDictionary), не
`Dot.Array`. Массив `entities:[...]` → NRE. Словарь
`entities:{"enemy1":{...}}` → `quest-begin` проходит, босс рендерится
(6★, 8888). [RUN] `work/r86.png`, `work/r95.png`.

`scaledBossTable` лежит в объекте активного квеста
(`activeQuests[qid].scaledBossTable`), читается `ActiveQuest..ctor` (`RVA
0xC38BC8`, ключ `0xC38DE8`). `entityType:"boss"` + `characters:["bumblebee_cin_dotm_2"]`
приняты. [STATIC]+[RUN]

Поиск образца в ассетах: 3201 файл, совпадения только в `global-metadata.dat`;
реального JSON-образца нет. [STATIC]

Ход на тайл с боссом: `moveto` уходит, бот остаётся на месте, `/matches/*` нет.
Нужен `battle`-action/battleId. [RUN] `work/r96.png`.

### 11.2 Точная NRE-инструкция и отрицательный опыт (2026-10-23)

`MapTile.Deserialize` читает `entities` через `Dot.Object` (`0x1485094`);
`0x1485098 cbz x0,#0x1486508` — это и есть падающая ветка: массив не
является `IDictionary`, `Dot.Object` возвращает null, `0x1486508` — общий
throw-блок (`bl 0x9bb514`). Это происходит до `entityType`, поэтому поля
сущности не помогали. Словарь `entities:{"enemy1":{...}}` проходит.

`MapTile` читает таблицу из `builder.summary.bossTable` (`builder+0x28`,
`summary+0x98`). `ActiveQuest..ctor` читает верхнеуровневый
`scaledBossTable` (`0xC39038/0xC39044`) и передаёт его в
`Quests.Builder..ctor` (`0xC393E4`, `0xEF2D04`), который кладёт его в
`+0x18`. Поэтому таблица должна быть в верхнем уровне `activeQuests[qid]`.

Фабрика: `Quests.Builder.NewEntity` (`0xEF28CC`) по **baseType**:
`bcg|boss|tower` -> `BCGEntity`; `building` -> `Building`;
`generator` -> `Generator`; иначе generic `Entity`. `characters` —
`Dot.StringList` (`0x1464E0C`) -> `List<string>`.

Дешёвый опыт: в movedir-ответ добавлены `currentFightId`,
`currentBattleId`, `localPlayer` и др. Клиент отправил
`/quests/quest-movedir/.../1/0`, но бот остался на (0,0), HUD 11%,
`/matches/activate-match` не вызван. **Отрицательно**: progression-only
недостаточно; нужен battle-action/триггер `ActivateMatch(hero)`.
[RUN] `work/r119.png`, `server/requests.jsonl` 05:41:47Z.




## 12. Wiki archive (Part B, 2026-10-23)

- Fandom: **3613** страниц = **817 non-File + 2796 File**. Все **817
  non-File** сохранены с полной историей + HTML; 5 File тоже; все
  **2796 File-описаний** сохранены (последняя ревизия). [DERIVED]
  подтверждена. [RUN]
- TFWiki: **8** FTF-страниц с полной историей + HTML.
- Картинки: **694/2752**; **209** ошибок (в основном 403, без обхода).
  Manifest **5154** записи; state продолжается.
- Разбор: **44 бота** + **252 страницы**. Матрица качества
  `data/wiki/bot_matrix.json`: 43 — star HP/Attack, 38 — rank/level
  tables, 38 — abilities, 37 — ability rank tables, 40 — signature,
  39 — signature tables, 41 — special attacks, 1 — synergy.
- ID map `data/wiki/id_map.json`: 59 client packs = 52 bot packs + 7
  Sharkticon variants; 39 non-Sharkticon bots have a wiki stat page, 13 do
  not; 44 wiki stat pages = 39 matched + 5 wiki-only (Chromia, Dead End,
  Optimus Prime, Soundblaster/Tactician, Starscream). [CLIENT]+[WIKI]
- Версии `data/wiki/versions.json` + `versions/`: cutoff
  `2023-01-13T23:59:59Z`; 296 страниц; 96 изменённых; 11 созданных после
  cutoff (включая Netflix-страницы). as_of и latest лежат отдельно.
- OneDrive автора `isAuthenticated:false`; не скачивался.
- Отчёт: `COVERAGE_WIKI.md`, вопросы: `OPEN_QUESTIONS.md`.

### 11.5 `activeTeams` — словарь, `TeamHeroes` — список (2026-10-23)

`BCGUserData.activeTeams` — `BCGUserActiveTeamDict : Dictionary<string,
BCGUserActiveTeam>`, не список. `BCGUserActiveTeam..ctor` (`0xA610F0`)
читает `aid`, `type`, `modes`, `expire`, `heroes`; `heroes` — `Dot.Object`
(словарь), из которого строится `TeamHeroes` (`List<BCGHeroDetails>`).
`BCGHeroDetails` использует `blueprint`, `rank`, `level`, `sig_lvl`,
`HPRating`, `HPMax`, `AttackRating`, `Attack`, `AttributeData`, `ForgeLevel`.

Ответ переведён на `activeTeams`-словарь и `heroes`-словарь с
`blueprint/rank/level/hp/max_hp`. Экран «ALL KNOCKED OUT» исчез, но
префайт всё ещё пустой; «+»/FIGHT даёт NRE в
`PrefightScreenPresentation.GetNewScale(HeroData robot)`;
`/matches/activate-match` не вызван. [RUN] `work/teamfix4.png`,
`work/teamfix6.png`.


### 12.1 P0 A1/A2 + S1/S2 (2026-10-23, [RUN])

- `PrefightScreenData.GetCurrentTeam`: `_activeQuest+0x50` ->
  `ActiveQuest.mode+0x18` -> `BCGHelper.GetActiveTeam` (`0xC1FFDC`);
  lookup идёт по `BCGManager.UserData.activeTeams` с ключом **mode**
  (`story`). `qid`/`uniqueId` — не тот ключ.
- Добавлены mode-клоны `aid:"story"`/`"Story"` в login/quest-begin/
  movedir. Префайт всё равно пуст, NRE `GetNewScale`, `/matches` не
  вызван. [RUN] `work/mode_team.png`, `mode_team2.png`.
- `QuestUserInfo.team` — внутренний `List<QuestUserHero>` (+0x68);
  JSON-вход разбирается `Dot.Object` -> `QuestUserHero..ctor`
  (`0x103CC70`). Верхнеуровневый `team` quest-begin переведён в
  словарь `bid -> {hp,pi,sig_lvl,stat_mods,sig_mods}`; memory count
  всё ещё 0.
- `work/smoke_test.py`: холодный запуск -> PLAY NOW -> FIGHT -> STORY ->
  квест -> START -> карта -> боевой тайл; PASS, 7 скриншотов,
  `tests/smoke/latest.json`. `activate_match=false`, NRE есть.
- `work/golden_regression.py --record` + check: 9 эталонных запросов
  (`getLoginData`, account, tuning, quest-list/active/progression/
  detail/begin/movedir), PASS. `tests/golden/`.
- [RUN] `npm` не использовался; Frida/gadget/патчи не использовались.

- A3 variant `v01_baseline`: status=PASS, activate_match=False, plus_error=True, team_count=0. Текущая база: activeTeams list, story clone, heroes dict.

- A3 variant `v03_mode_team_only`: status=PASS, activate_match=False, plus_error=True, team_count=0. Одна active team с aid=story и полными hero fields.

- A3 variant `v04_hero_details_full`: status=PASS, activate_match=False, plus_error=True, team_count=0. Hero details с rating_hp/rating_attack/special_attacks/forge_level.

- A3 variant `v02_canonical_hero_key`: status=PASS, activate_match=False, plus_error=True, team_count=0. Ключ героя без _2: bumblebee_cin_dotm; heroes dict.

- A3 variant `v05_quest_team_flat`: status=PASS, activate_match=False, plus_error=True, team_count=0. quest-begin team = dict bid->hp/pi/sig_lvl/stat_mods/sig_mods.

- A3 variant `v06_modes_expire`: status=PASS, activate_match=False, plus_error=True, team_count=0. Type=Story, modes=[story,Story], expire=999999.

### 13. W1: synergy parser (2026-10-23)

Причина 1/44: `parse_bots.py` искал только `==Synergy Bonuses==`, а в
сыром викитексте 64 страницы используют `===Synergy Bonuses===` и
встречается `Common Synergies`. Добавлен `section_any` (2–4 знака `=`).
Повторный разбор: synergy у **40/44** ботов; missing: Chromia,
Cliffjumper, Ironhide, Soundblaster (у них нет секции/она не буллеты).
`data/wiki/bots.json` и `bot_matrix.json` перегенерированы; остальные
счётчики не изменились. [WIKI]


### 14. P1 W1–W6 / C2–C5 / P2 I2 (2026-10-23)

- W1: synergy parser fixed; **40/44** bots, matrix regenerated. [WIKI]
- W2: `notes/wiki_unity_tutorial.md`; page revid 10747, 2023-01-14; APK
  `assets/assetpack` verified. UABE not installed. [WIKI]+[CLIENT]
- W3: `data/wiki/topics/*.json` (13 topics) with as_of_2023/latest and
  curated page sets; no invented values. [WIKI]
- W4: `data/wiki/client_only.json`: 13 client-only non-Sharkticon, 7
  Sharkticon variants, 5 wiki-only pages. [CLIENT]+[WIKI]
- W6: `archive/INTEGRITY.md`; 5154/5154 manifest verified after correcting
  5 stale hashes; 209 errors all 403; new zip
  `TFTF_wiki_archive_2026-10-23_210335.zip`, sha256 `0731484c...`.
- C2: `spec/rating_formula.md`; entry `0xA4814C`, weights
  `heroRatingAttackWeight`/`heroRatingMaxHPWeight`, formula partial. [STATIC]
- C3: `server/data/tuning_client_defaults.json` with only four verified
  defaults; rest intentionally absent.
- C4: `data/wiki/ability_localization_client.json`; only 8 `D_STAT` keys
  found by the current extractor — blocked, see OPEN_QUESTIONS.
- C5: `server/data/bot_catalog_real.json`, 59 packs, class/faction for 59,
  stars for 39; missing values empty with reasons.
- I2: `docs/persistence_design.md` (design only).

### 12.2 P0 A3: harness + variants (2026-10-23)

`work/run_variant.py` backs up `bcg_login_data.json` and
`quest_begin_response.json`, applies a variant, runs `work/smoke_test.py --plus`
(7 flow screenshots + plus), parses `tests/smoke/latest.json`, appends a result
row and restores the base data. `work/variants/` has six variants:
baseline, canonical hero key, mode-only team, full hero fields, flat quest team,
and modes/expire.

Six client runs (time-boxed; not the requested 10–20): all returned
`login=true`, `quest_begin=true`, `movedir=true`, `activate_match=false`,
`plus_error=true`, `memory_team_count=0`. `work/teamfix*`, `tests/smoke/08_plus.png`.
Conclusion: changing activeTeams/heroes shape within these variants does not
fill `TeamData`; the blocker is deeper (exact BCGHeroDetails element parsing or
the active-team object source), not a simple alias. [RUN]

- A3 variant `v07_dict_team`: status=FAIL, activate_match=False, plus_error=True, team_count=None. login activeTeams as dict keyed story.

- A3 variant `v08_heroes_list`: status=PASS, activate_match=False, plus_error=True, team_count=0. active team heroes as list, not dict.

- A3 variant `v09_story_qid_hero`: status=PASS, activate_match=False, plus_error=True, team_count=0. aid story, hero key bumblebee_cin_dotm_2.

- A3 variant `v10_empty_control`: status=PASS, activate_match=False, plus_error=True, team_count=0. control: no active teams.

### 15. A3 10 variants / C4 / W5 index / I1 (2026-10-23)

- A3: six + four variants (v01–v10). v07 dict activeTeams made login fail
  (`/auth/init` only), confirming the login parser wants a list; v08–v10
  behaved like baseline. All non-control runs: `activate_match=false`,
  `plus_error=true`, `team_count=0`. [RUN]
- C4: binary scan found **3315** `D_STAT`/`ID_STAT` key/value entries;
  `data/wiki/ability_localization_client.json` regenerated. Values can be
  German/Italian/English depending on the asset; mapping to bots is open.
- W5: `data/wiki/image_index.json`: 694 unique files / 698 manifest entries;
  209 errors all 403; categories maps_quests 143, items 154, ui 54, bots 24,
  other 323 (present) and corresponding error categories.
- I1: `server/data/autorefresh_metadata.json` extracted and used by routing;
  behavior verified by golden regression. Full routing/data split still open.

### 16. Prefight provider / injector (2026-10-24)

- `PreFightScreen._model` (`+0x98`) is null at runtime; FIGHT NRE is at
  `PreFightScreen.OnFight` `0xE397BC` before any team access. [RUN]
- `CacheReferences` (`0xE38E4C`) obtains the provider exclusively through
  `InterfaceInjector.Get<IPrefightDataProvider>` (`0x11E7640`). There is
  no direct `new PrefightScreenData` BL in the binary. [STATIC]
- Injector runtime state (`work/read_tag.py`): tag `tform`, 78 interface
  entries, one persistent interface (`IAdsProvider` ->
  `TFormIronSourceAdsModel`). Entry 0 has `tform`+`default`; entries 1..77
  have `default` only. [RUN]
- Therefore changing `activeTeams`, `TeamHeroes`, `teamData`, `team`,
  `hp`, `pi`, `localPlayer` cannot fill the prefight: those paths are
  never reached. The earlier "team count 0" was a probe/timing artifact;
  the current live team count is 1. [RUN]
- `smoke_test.py` cold-boot timing is too tight (02_title still title);
  the manual flow reaches the prefight. [RUN]
- `golden_regression.py`: 2 shape changes expected after the quest-list
  key correction and current movedir battle stub; re-record pending. [RUN]

## 17. 2026-10-24: harness and exact NRE

- `PreFightScreen.OnFight` NRE confirmed by `smoke_test.py --fight`:
  `NullReferenceException` at `PreFightScreen.OnFight`, `_model` null.
  The `GetNewScale` NRE belongs to an older experiment and is not the
  current first failure. [RUN]
- `read_prefight_state.py` had a List-vs-Dictionary bug: it read a
  `List<QuestUserHero>` with dictionary offsets and printed count 0.
  The same pointer read as a List has count 1. Fixed; the harness now
  reports 1. [RUN]
- Full smoke PASS + golden 9/9 PASS after re-record. [RUN]

### 18. R1 roster and wiki attribution (2026-10-24)

- Roster: **59** bots in `userData.heroes` / `entities.bot`;
  **60** blueprints (59 bots + the existing Optimus rank catalog).
  The 57 new bots use the client pack id as `bid`/`modelId`/`character`
  and the wiki page name as `friendly_name`. [CLIENT]+[WIKI]
- Star-1 HP/ATK/rating: **12/59** from wiki tables; **47/59** are
  `[ASSUMED]` (1000 HP / 120 ATK / 100 rating). No hidden crit/armor/
  block values were invented.
- Class bit mapping: Brawler=1, Tactician=2, Scout=4, Demolition=8,
  Warrior=16, Tech=32. Sharkticon variant ids are mapped per variant;
  `Demolitions` is normalized to `Demolition`. [STATIC]
- `teamSizeMax=1` is a deliberate deviation for the synthetic 1.1 quest;
  `teamCountMax` remains 3. [ASSUMED]
- [RUN] BOTS + Windblade details/INFO screens open without NRE; the
  displayed rating is 300, while wiki star-1 Windblade says 264.
  Rating formula/inputs remain unresolved (R2).

### 19. C4 localization count reconciliation (2026-10-24)

- Broad scan of `work/unpacked/assets/bin/Data` for any `"k": "..."` key
  (not requiring the extractor's adjacent `"v"`) finds **7996** unique
  keys. 127 of them are not in `work/localization_all.json`; they are AI /
  tuning fields (`Aggressiveness`, `BlockDelayUnderAttack`,
  `CD_DashCombo_Weight`, numeric strings, etc.), not UI localization.
- `work/localization_all.json` has **7869** localization keys. The legacy
  **7994** is within 2 of the broad 7996 count, so the difference is
  explained by counting those 127 config keys (and two empty/numeric edge
  keys), not by missing localization text. Do not use 7994 as the
  localization total.
- `localization_all.json` and `ability_localization_client.json` agree
  exactly on **3315** stat strings: 8 `D_STAT` + 3307 `ID_STAT`, no
  duplicates. The legacy **3332** cannot be reproduced from the current
  assets; 17 keys are unaccounted. `global-metadata.dat` contains only
  `D_STATE`/`ID_STATE`, not 17 extra stat strings.
- Evidence: `work/analyze_localization_count.py`,
  `work/analyze_stat_count.py`.

### 20. A1/A2/A3/A4: registry resolved (2026-10-24)

- `work/dump_injector_names.py` resolves all 78 injector entries through
  `Il2CppTypeDefinition.nameIndex` -> `global-metadata.dat` string table.
- **`IPrefightDataProvider` is entry 69 with one implementation:
  `default -> PrefightScreenData`.** It has no `tform` implementation.
  `IAdsProvider` is the only entry with both `tform` and `default`.
- Live `_currentTag = "tform"`, `_gameInterfaces = 78`, persistent = 1.
- `Get<T>` (`0x11E7640`) does `ContainsKey` (0x11E7860), then iterates tuples:
  current tag compare at `0x11E7950`, **default fallback at `0x11E7988`**,
  then `Activator.CreateInstance` at `0x11E79E8`. So a default fallback
  exists; the null means `ContainsKey(typeof(T))` failed, the call site is a
  different interface, or `Activator.CreateInstance` returned null/threw.
- `PrefightScreenData` is the only class implementing
  `IPrefightDataProvider`; no story/arena/PvP variant.
- `HeroesScreen` is not an injector consumer (uses `BCGHelper.GetHeroes`);
  BOTS is not a working analog. Better analogs: `ISettingsScreenDataProvider`
  (entry 73), `IPlayerProfileDataProvider` (entry 39), both default-only.
- `Gameboard.OpenPreFightScreen` (`0xA550A0`) is called from
  `Action_Battle`/`Action_Ambush`; it does not create `PrefightScreenData`
  and does not register anything. `PrefightScreenData..ctor` has no direct
  BL call, consistent with `Activator.CreateInstance`.
- No provider/Injector error appears in logcat before the FIGHT NRE.
  `QuestboardHud is inactive` was the only nearby warning.
- Docs: `docs/prefight_flow.md` (Mermaid + addresses).
