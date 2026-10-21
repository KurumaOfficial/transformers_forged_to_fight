# МАТРИЦА ОХВАТА СЕТЕВОГО ПРОТОКОЛА SPARX
## Transformers: Forged to Fight v9.2.0 (com.kabam.bigrobot)

---

### 1. Сводная матрица эндпоинтов (Bootflow, Base Hub, Quests, Combat)

| # | Метод | Эндпоинт | Статус | Источник | Обязательные поля (Wire-Keys) | Реакция клиента на ошибку |
|---|---|---|---|---|---|---|
| 1 | `POST` | `/auth/init` | **[RUN]** | `[CLIENT]` (AnonAuthenticator) | `session`, `status` | Фатальный алерт при загрузке, сессия не стартует |
| 2 | `POST` | `/auth/enumerate` | **[RUN]** | `[CLIENT]` (LoginAPI.Enumerate) | **JSON-массив** `[]` (не объект!) | Исключение `_PostInit.listToAuthenticate.Count=0` |
| 3 | `POST` | `/auth/prelogin` | **[RUN]** | `[CLIENT]` (LoginAPI.PreLogin) | `salt`, `status` | Если salt не пустой, вызывается `libapkprotect` |
| 4 | `POST` | `/auth/login` | **[RUN]** | `[CLIENT]` (LoginAPI.Login) | `auth.device: true`, `endpoints.device`, `stoken` | Модальное окно "Login Failed", ретрай |
| 5 | `GET` | `/account/data` | **[RUN]** | `[CLIENT]` (UserManager) | `privacySettings.friendsinvite`, `invitesDB`, `maxHelpsPerRequest` | `NullReferenceException` в `InvitesManager` |
| 6 | `GET` | `/bcg/getLoginData` | **[RUN]** | `[CLIENT]` (BCGManagerBase) | `attributeGrowthDefs`, `heroes`, `blueprints`, `evoBlueprints` | Алерт "No evo blueprints" или NullRef |
| 7 | `GET` | `/tuning` | **[RUN]** | `[CLIENT]` (TuningManager) | Список словарей тюнинга боевых констант | Клиент использует зашитые дефолтные числа |
| 8 | `GET` | `/payments/payouts` | **[RUN]** | `[CLIENT]` (PaymentsAPI) | Пустой словарь/массив | Магазин скрывает платные предложения |
| 9 | `GET` | `/performance/profile` | **[RUN]** | `[CLIENT]` (PerformanceManager) | Графический профиль | Клиент выбирает средний профиль |
| 10 | `GET` | `/autorefresh/*` | **[RUN]** | `[CLIENT]` (AutoRefreshAPI) | `check` (string), `refresh` (int), `cache` (bool) | Повторный поллинг с интервалом |
| 11 | `GET` | `/redeemer/refresh` | **[RUN]** | `[CLIENT]` (RedeemerManager) | Структура наград и подарков | Раздел промокодов пуст |
| 12 | `GET` | `/events/refresh` | **[RUN]** | `[CLIENT]` (EventManager) | Список активных ивентов | Вкладка ивентов пуста |
| 13 | `POST`| `/tutorial/get-login-data` | **[RUN]** | `[CLIENT]` (TutorialAPI) | `"s": "completed"`, `"current_bid": "close"`, `"branches"` | Запуск обучающего боя `FTEIntroFight` |
| 14 | `POST`| `/tutorial/{action}` | **[RUN]** | `[CLIENT]` (TutorialAPI) | `s`, `branchID` | Зависание на шаге туториала |
| 15 | `GET` | `/gamestats/get-login-data`| **[RUN]** | `[CLIENT]` (GameStatsManager) | `stats`, `achievements` | Статистика обнулена |
| 16 | `GET` | `/offers/getLoginData` | **[RUN]** | `[CLIENT]` (OffersManager) | Каталог акций | Витрина предложений пуста |
| 17 | `GET` | `/ds/{uid}/` | **[RUN]** | `[CLIENT]` (DataAPI) | `profile` (громкость, тултипы) | Сброс локальных настроек в дефолт |
| 18 | `GET` | `/push/token` | **[RUN]** | `[CLIENT]` (PushAPI) | `status`, `websocket` | Отключение пуш-нотификаций |
| 19 | `GET` | `/inventory` | **[RUN]** | `[CLIENT]` (InventoryAPI) | `items` | Инвентарь отображается пустым |
| 20 | `GET` | `/wallet` | **[RUN]** | `[CLIENT]` (WalletAPI) | `gold`, `energon`, `ore13` | Ресурсы берутся из кэша `/account/data` |
| 21 | `GET` | `/base/active` | **[RUN]** | `[CLIENT]` (BaseManager) | **`pathData`**, `gridDimension`, `grid`, `theme: "primordial"` | `NullReferenceException` в `PathAnalyzer` |
| 22 | `GET` | `/pvp/get-login-data` | **[RUN]** | `[CLIENT]` (PvpManager) | Статус PvP-сезона | Арена недоступна |
| 23 | `GET` | `/chat/data` | **[RUN]** | `[CLIENT]` (ChatManager) | Каналы чата | Окно чата отключено |
| 24 | `POST`| `/userprofile/` | **[RUN]** | `[CLIENT]` (UserProfileAPI) | Профиль игрока | Карточка профиля не обновляется |
| 25 | `POST`| `/telemetry` | **[RUN]** | `[CLIENT]` (TelemetryAPI) | Статус `ok` | Игнорируется клиентом |
| 26 | `POST`| `/util/ping` | **[RUN]** | `[CLIENT]` (PingAPI) | Сессия активна | Клиент считает соединение разорванным |
| 27 | `GET` | `/quests/quest-list` | **[RUN]** | `[CLIENT]` (QuestsAPI) | **JSON-массив** глав и актов | Окно квестов отображается без глав |
| 28 | `GET` | `/quests/quest-active` | **[RUN]** | `[CLIENT]` (QuestsAPI) | Описание текущего активного квеста | Клиент считает, что активного квеста нет |
| 29 | `GET` | `/quests/quest-progression` | **[RUN]** | `[CLIENT]` (QuestsAPI) | Проценты прохождения глав | 0% на бейджах глав |
| 30 | `POST`| `/matches/activate-match/*`| **[SPEC]**| `[CLIENT]` (MatchAPI) | `matchId`, `fighterData` | Ошибка `FightFlow.OnMatchInit`, бой отменяется |
| 31 | `POST`| `/matches/resolve-match/*` | **[SPEC]**| `[CLIENT]` (MatchAPI) | `rewards`, `victory`, `xpEarned` | Диалог ретрая, награды не начисляются |

---

## 2. Критические требования к валидации (Validation Rules)

1. **Sparx Envelope:** Любой ответ со статусом `200` обязан содержать корневой объект с целочисленным `ts` (текущий Unix-timestamp) и полем `result`.
2. **Формат списков vs словарей:**
   - `/auth/enumerate` — **СТРОГО массив** `[]`. Передача `{}` ломает `LoginManager._PostInit`.
   - `/quests/quest-list` — **СТРОГО массив** `[]`. Передача `{}` ломает десериализатор списка глав.
   - `/gamestats/check-login-achievements` — **СТРОГО массив** `[]`.
3. **Формат путей карты (`Map`):**
   - Корневой ключ в описании карты — строго `"pathData"`, содержащий список объектов.
   - Внутри каждого объекта пути — ключ `"path"`, содержащий список точек `[{"x": 0, "y": 0}]`.
