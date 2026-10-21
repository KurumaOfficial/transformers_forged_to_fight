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
