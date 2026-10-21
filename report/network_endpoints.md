# Network Endpoints, Protocols & Data Structures
## Transformers: Forged to Fight (v9.2.0 - com.kabam.bigrobot)

> **Примечание:** Данный документ составлен исключительно на основе статического анализа APK (декомпиляция метаданных IL2CPP v27, ELF-библиотек и сериализованных ассетов Unity).

## 1. Сетевая архитектура и транспорт

- **Сетевой движок:** `EB.Sparx` (Kabam Sparx Platform) & `EB.Net` (Exploding Barrel Network).
- **Транспортные протоколы:**
  - **HTTPS / REST:** `EB.Net.WebRequest`, `UnityEngine.Networking.UnityWebRequest`.
  - **WebSockets (WSS):** `EB.Sparx.NetworkWS` — постоянное соединение для нотификаций, чата, статусов матчей.
  - **Reliable UDP (ENet):** `EB.Sparx.NetworkENet` через нативную библиотеку `libenetlib.so`.
- **Формат сериализации:**
  - Основной формат данных — **JSON** (`EB.JSON`, `AFMiniJSON.Json`, `EB.Sparx.JSONStatUserDict`). Запросы упаковываются как JSON-RPC / REST вызовы.
- **CDN & Доставка ассетов:**
  - Продакшн CDN endpoint (найден в `assets/bin/Data/e1917cd7a6bdb4492a247b8f758df2ae`): `https://tform-0901-hzlhiniyfcwf.tf-cdn.net`.
  - MOTD CDN: `https://static.tf-cdn.net/motd/...`.
  - Доставка ассетов: Play Asset Delivery (Google PAD) через `Google.Play.AssetDelivery.dll` и локальный каталог `assets/assetpack/`.

## 2. Безопасность, Сертификаты и Античит

- **Certificate Pinning:**
  - В коде присутствует класс `AcceptAllCertificates` (используется для тестовых окружений или при определённых флагах сборки).
  - `EB.Net.TcpClientSSL` и `BouncyCastle.dll` реализуют TLS/SSL валидацию. Хардкод публичных ключей серверов Kabam в IL2CPP метаданных представлен строками `CERTIFICATE`, `-----BEGIN CERTIFICATE-----`.
- **Античит и защита целостности:**
  - `libapkprotect.so`: Экспортирует функции `APK_Check_Start`, `APK_Check_Start_Salt`, `APK_Check_Step`, `APK_Check_Complete`. Проверяет хэш DEX и подпись APK при запуске.
  - `libnms.so`: Компонент рекламного SDK ByteDance / Pangle (безопасность/валидация рекламы).
  - `libkrash.so`: Google Breakpad native crash reporter (`Krash_Initialize`, `Krash_Log`).
  - Классы `Security`: root-детекция и проверка отладчика встроены в вызовы `EB.Sparx.LoginManager` и `EB.Sparx.ServerAccessManager`.

## 3. Все обнаруженные API эндпоинты (по сервисам)

### Сервис `/` (3 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `//` | RPC / API маршрут |
| `///` | RPC / API маршрут |
| `////` | RPC / API маршрут |

### Сервис `/Applications` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/Applications` | RPC / API маршрут |

### Сервис `/CBC` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/CBC` | RPC / API маршрут |

### Сервис `/CFB` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/CFB` | RPC / API маршрут |

### Сервис `/SIC` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/SIC` | RPC / API маршрут |

### Сервис `/System` (3 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation` | RPC / API маршрут |
| `/System/Library/Frameworks/CoreServices.framework/Frameworks/CFNetwork.framework/CFNetwork` | RPC / API маршрут |
| `/System/Library/Frameworks/Security.framework/Security` | RPC / API маршрут |

### Сервис `/TIME_STATS.txt` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/TIME_STATS.txt` | RPC / API маршрут |

### Сервис `/account` (8 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/account` | RPC / API маршрут |
| `/account/auth_capture` | RPC / API маршрут |
| `/account/check-name` | RPC / API маршрут |
| `/account/data` | RPC / API маршрут |
| `/account/link` | RPC / API маршрут |
| `/account/name` | RPC / API маршрут |
| `/account/support` | RPC / API маршрут |
| `/account/unlink` | RPC / API маршрут |

### Сервис `/acknowledge_consent` (2 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/acknowledge_consent/decline_consent/` | RPC / API маршрут |
| `/acknowledge_consent/give_consent/` | RPC / API маршрут |

### Сервис `/ad_payments` (2 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/ad_payments/ad-completed` | RPC / API маршрут |
| `/ad_payments/ad-started` | RPC / API маршрут |

### Сервис `/allianceevents` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/allianceevents` | RPC / API маршрут |

### Сервис `/alliances` (15 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/alliances/assignOwner` | Управление альянсом |
| `/alliances/create` | Управление альянсом |
| `/alliances/demote` | Управление альянсом |
| `/alliances/details` | Управление альянсом |
| `/alliances/find` | Управление альянсом |
| `/alliances/find-recommended` | Управление альянсом |
| `/alliances/invite` | Управление альянсом |
| `/alliances/join` | Управление альянсом |
| `/alliances/kick` | Управление альянсом |
| `/alliances/leave` | Управление альянсом |
| `/alliances/promote` | Управление альянсом |
| `/alliances/refresh` | Управление альянсом |
| `/alliances/request-join` | Сюжетные и ивентовые квесты |
| `/alliances/request-members` | Сюжетные и ивентовые квесты |
| `/alliances/update` | Управление альянсом |

### Сервис `/appsflyer` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/appsflyer/register_id` | RPC / API маршрут |

### Сервис `/auth` (8 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/auth/enumerate` | RPC / API маршрут |
| `/auth/init` | RPC / API маршрут |
| `/auth/login` | Аутентификация / вход |
| `/auth/prelogin` | Аутентификация / вход |
| `/auth/unauth/failed` | RPC / API маршрут |
| `/auth/users/list` | RPC / API маршрут |
| `/auth/users/new` | RPC / API маршрут |
| `/auth/users/switch` | RPC / API маршрут |

### Сервис `/autorefresh` (2 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/autorefresh/` | RPC / API маршрут |
| `/autorefresh/grouprefresh` | RPC / API маршрут |

### Сервис `/ava` (3 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/ava/cancel-matchmaking` | Матчмейкинг / PVP |
| `/ava/enter-matchmaking` | Матчмейкинг / PVP |
| `/ava/matchmaking-entry` | Матчмейкинг / PVP |

### Сервис `/ave` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/ave` | RPC / API маршрут |

### Сервис `/base` (2 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/base` | RPC / API маршрут |
| `/base/active` | RPC / API маршрут |

### Сервис `/bcg` (12 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/bcg/buy-cat` | Данные ботов / ростера |
| `/bcg/buy-stamina` | Данные ботов / ростера |
| `/bcg/convert-to-coin` | Данные ботов / ростера |
| `/bcg/evolve-hero` | Данные ботов / ростера |
| `/bcg/getBaseHeroData` | Данные ботов / ростера |
| `/bcg/getHeroXPCurve` | Данные ботов / ростера |
| `/bcg/getLoginData` | Данные ботов / ростера |
| `/bcg/getUserData` | Данные ботов / ростера |
| `/bcg/removeActiveTeam` | Данные ботов / ростера |
| `/bcg/sell-hero` | Данные ботов / ростера |
| `/bcg/setSavedTeam` | Данные ботов / ростера |
| `/bcg/upgrade-hero` | Данные ботов / ростера |

### Сервис `/benchmark` (2 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/benchmark/performance` | RPC / API маршрут |
| `/benchmark/processes` | RPC / API маршрут |

### Сервис `/bin` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/bin/bash` | RPC / API маршрут |

### Сервис `/bugs` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/bugs` | RPC / API маршрут |

### Сервис `/channel.html` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/channel.html` | RPC / API маршрут |

### Сервис `/chat` (4 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/chat/data` | RPC / API маршрут |
| `/chat/inviteFriend` | RPC / API маршрут |
| `/chat/removeFriend` | RPC / API маршрут |
| `/chat/token` | RPC / API маршрут |

### Сервис `/configuration` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/configuration/system.runtime.remoting` | RPC / API маршрут |

### Сервис `/deeplinking` (2 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/deeplinking/process_links` | RPC / API маршрут |
| `/deeplinking/referrers` | RPC / API маршрут |

### Сервис `/events` (2 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/events/get-leaderboard-page` | RPC / API маршрут |
| `/events/refresh` | RPC / API маршрут |

### Сервис `/factions` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/factions/select` | RPC / API маршрут |

### Сервис `/fight` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/fight` | RPC / API маршрут |

### Сервис `/files` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/files/il2cpp/` | RPC / API маршрут |

### Сервис `/forums` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/forums/register` | RPC / API маршрут |

### Сервис `/gacha` (4 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/gacha/claimfree` | Открытие кристаллов |
| `/gacha/getOdds` | Открытие кристаллов |
| `/gacha/pick` | Открытие кристаллов |
| `/gacha/store` | Открытие кристаллов |

### Сервис `/gameentitlements` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/gameentitlements/refresh` | RPC / API маршрут |

### Сервис `/gamestats` (2 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/gamestats/check-login-achievements` | Аутентификация / вход |
| `/gamestats/get-login-data` | Аутентификация / вход |

### Сервис `/gamestore` (4 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/gamestore/buy` | Внутриигровой магазин |
| `/gamestore/gift` | Внутриигровой магазин |
| `/gamestore/sell` | Внутриигровой магазин |
| `/gamestore/use` | Внутриигровой магазин |

### Сервис `/inventory` (2 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/inventory` | RPC / API маршрут |
| `/inventory/` | RPC / API маршрут |

### Сервис `/invites` (4 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/invites/accept` | RPC / API маршрут |
| `/invites/privacy` | RPC / API маршрут |
| `/invites/refresh` | RPC / API маршрут |
| `/invites/reject` | RPC / API маршрут |

### Сервис `/kabamsignup` (3 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/kabamsignup/signup/complete` | RPC / API маршрут |
| `/kabamsignup/signup/later` | RPC / API маршрут |
| `/kabamsignup/signup/never` | RPC / API маршрут |

### Сервис `/krash` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/krash` | RPC / API маршрут |

### Сервис `/leaderboard` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/leaderboard` | RPC / API маршрут |

### Сервис `/leaderboards` (2 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/leaderboards` | RPC / API маршрут |
| `/leaderboards/` | RPC / API маршрут |

### Сервис `/leaderboardss3` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/leaderboardss3/get-scores-by-userids` | RPC / API маршрут |

### Сервис `/levelrewards` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/levelrewards/fetch` | RPC / API маршрут |

### Сервис `/loginrewards` (2 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/loginrewards/claim` | Аутентификация / вход |
| `/loginrewards/fetch` | Аутентификация / вход |

### Сервис `/loginrewards2` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/loginrewards2/fetch` | Аутентификация / вход |

### Сервис `/main` (4 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/main/heroes` | Данные ботов / ростера |
| `/main/mail` | RPC / API маршрут |
| `/main/mods` | RPC / API маршрут |
| `/main/relics` | RPC / API маршрут |

### Сервис `/master` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/master/list` | RPC / API маршрут |

### Сервис `/matches` (6 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/matches/activate-match/` | Матчмейкинг / PVP |
| `/matches/find-match/` | Матчмейкинг / PVP |
| `/matches/match-loaded/` | Матчмейкинг / PVP |
| `/matches/resolve-match/` | Матчмейкинг / PVP |
| `/matches/retry-match/` | Матчмейкинг / PVP |
| `/matches/simulate-match/` | Матчмейкинг / PVP |

### Сервис `/me` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/me/permissions` | RPC / API маршрут |

### Сервис `/messages` (2 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/messages/deletemulti` | RPC / API маршрут |
| `/messages/readmulti` | RPC / API маршрут |

### Сервис `/motd` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/motd/status` | RPC / API маршрут |

### Сервис `/notifications` (4 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/notifications/adjust_filters` | RPC / API маршрут |
| `/notifications/interstitial/response` | RPC / API маршрут |
| `/notifications/interstitial/shown` | RPC / API маршрут |
| `/notifications/registertoken` | RPC / API маршрут |

### Сервис `/objectives` (5 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/objectives` | Ежедневные / еженедельные цели |
| `/objectives/activate` | Ежедневные / еженедельные цели |
| `/objectives/cancel` | Ежедневные / еженедельные цели |
| `/objectives/complete` | Ежедневные / еженедельные цели |
| `/objectives/refresh` | Ежедневные / еженедельные цели |

### Сервис `/odr` (2 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/odr/get-manifest` | RPC / API маршрут |
| `/odr/get-published-manifests` | RPC / API маршрут |

### Сервис `/offers` (3 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/offers/accept` | RPC / API маршрут |
| `/offers/decline` | RPC / API маршрут |
| `/offers/getLoginData` | RPC / API маршрут |

### Сервис `/options` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/options` | RPC / API маршрут |

### Сервис `/packs.txt` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/packs.txt` | RPC / API маршрут |

### Сервис `/payments` (5 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/payments/check-payout` | RPC / API маршрут |
| `/payments/payouts` | RPC / API маршрут |
| `/payments/promo-eligible` | RPC / API маршрут |
| `/payments/store` | Внутриигровой магазин |
| `/payments/verify-payout` | RPC / API маршрут |

### Сервис `/performance` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/performance/profile` | RPC / API маршрут |

### Сервис `/periodic_subscriptions` (3 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/periodic_subscriptions/claim` | RPC / API маршрут |
| `/periodic_subscriptions/claimall` | RPC / API маршрут |
| `/periodic_subscriptions/view` | RPC / API маршрут |

### Сервис `/prizes` (4 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/prizes/claim` | RPC / API маршрут |
| `/prizes/claimall` | RPC / API маршрут |
| `/prizes/claimbox/` | RPC / API маршрут |
| `/prizes/claimsome` | RPC / API маршрут |

### Сервис `/push` (2 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/push/key-get` | RPC / API маршрут |
| `/push/token` | RPC / API маршрут |

### Сервис `/pvp` (11 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/pvp/clear-invalid-teams` | Арена и дуэли |
| `/pvp/find-arena-opponent` | Арена и дуэли |
| `/pvp/get-login-data` | Аутентификация / вход |
| `/pvp/get-new-opponent` | Арена и дуэли |
| `/pvp/get-pvp-match-data` | Матчмейкинг / PVP |
| `/pvp/get-user-data` | Арена и дуэли |
| `/pvp/lockin` | Арена и дуэли |
| `/pvp/match-loaded` | Матчмейкинг / PVP |
| `/pvp/quit` | Арена и дуэли |
| `/pvp/retry-match` | Матчмейкинг / PVP |
| `/pvp/select-opponent` | Арена и дуэли |

### Сервис `/quests` (19 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/quests/quest-active` | Сюжетные и ивентовые квесты |
| `/quests/quest-autocomplete/` | Сюжетные и ивентовые квесты |
| `/quests/quest-begin/` | Сюжетные и ивентовые квесты |
| `/quests/quest-detail/` | Сюжетные и ивентовые квесты |
| `/quests/quest-historical-results/` | Сюжетные и ивентовые квесты |
| `/quests/quest-join/` | Сюжетные и ивентовые квесты |
| `/quests/quest-list` | Сюжетные и ивентовые квесты |
| `/quests/quest-movedir/` | Сюжетные и ивентовые квесты |
| `/quests/quest-moveto/` | Сюжетные и ивентовые квесты |
| `/quests/quest-placehero/` | Данные ботов / ростера |
| `/quests/quest-progression` | Сюжетные и ивентовые квесты |
| `/quests/quest-quit/` | Сюжетные и ивентовые квесты |
| `/quests/quest-recall/` | Сюжетные и ивентовые квесты |
| `/quests/quest-reset-battle-timeout/` | Сюжетные и ивентовые квесты |
| `/quests/quest-resync/avx/` | Сюжетные и ивентовые квесты |
| `/quests/quest-swapheroes/` | Данные ботов / ростера |
| `/quests/quest-unlock-battle/` | Сюжетные и ивентовые квесты |
| `/quests/send-pressure-notification` | Сюжетные и ивентовые квесты |
| `/quests/use/` | Сюжетные и ивентовые квесты |

### Сервис `/raid` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/raid/claim/defense` | RPC / API маршрут |

### Сервис `/raids` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/raids` | RPC / API маршрут |

### Сервис `/ratemyapp` (5 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/ratemyapp/happy` | RPC / API маршрут |
| `/ratemyapp/nothappy` | RPC / API маршрут |
| `/ratemyapp/rate/complete` | RPC / API маршрут |
| `/ratemyapp/rate/later` | RPC / API маршрут |
| `/ratemyapp/rate/never` | RPC / API маршрут |

### Сервис `/redeemer` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/redeemer/refresh` | RPC / API маршрут |

### Сервис `/refresh` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/refresh` | RPC / API маршрут |

### Сервис `/resources` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/resources/fetch` | RPC / API маршрут |

### Сервис `/server_access` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/server_access/requestaccess` | Сюжетные и ивентовые квесты |

### Сервис `/skilltrees` (3 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/skilltrees` | RPC / API маршрут |
| `/skilltrees/activate-multiple-nodes` | RPC / API маршрут |
| `/skilltrees/skilltrees-list` | RPC / API маршрут |

### Сервис `/store` (3 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/store/offerurl` | Внутриигровой магазин |
| `/store/payouts` | Внутриигровой магазин |
| `/store/verify-payout` | Внутриигровой магазин |

### Сервис `/survey` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/survey/geturl` | RPC / API маршрут |

### Сервис `/telemetry` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/telemetry` | RPC / API маршрут |

### Сервис `/tos` (2 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/tos` | RPC / API маршрут |
| `/tos/accept` | RPC / API маршрут |

### Сервис `/tuning` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/tuning` | Балансировочные таблицы и коэффициенты |

### Сервис `/tutorial` (5 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/tutorial/complete-tutorial` | Шаги и прогресс туториала |
| `/tutorial/early-start-branch` | Шаги и прогресс туториала |
| `/tutorial/get-login-data` | Аутентификация / вход |
| `/tutorial/start-branch` | Шаги и прогресс туториала |
| `/tutorial/start-tutorial` | Шаги и прогресс туториала |

### Сервис `/userprofile` (3 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/userprofile/` | RPC / API маршрут |
| `/userprofile/bulk` | RPC / API маршрут |
| `/userprofile/find` | RPC / API маршрут |

### Сервис `/usertitle` (3 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/usertitle/activetitle/` | RPC / API маршрут |
| `/usertitle/clearTitle` | RPC / API маршрут |
| `/usertitle/titles/` | RPC / API маршрут |

### Сервис `/util` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/util/ping` | RPC / API маршрут |

### Сервис `/wallet` (2 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/wallet/` | Баланс валют (Energon, Gold, Ore) |
| `/wallet/balance` | Баланс валют (Energon, Gold, Ore) |

### Сервис `/wske` (6 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/wske/kabam/accounts/create` | RPC / API маршрут |
| `/wske/kabam/accounts/login` | Аутентификация / вход |
| `/wske/kabam/accounts/logout/` | RPC / API маршрут |
| `/wske/kabam/accounts/password/resetRequest` | Сюжетные и ивентовые квесты |
| `/wske/kabam/accounts/password/update` | RPC / API маршрут |
| `/wske/kabam/accounts/validateToken/` | RPC / API маршрут |

### Сервис `/zoneinfo` (1 эндпоинтов)
| Эндпоинт | Назначение |
|---|---|
| `/zoneinfo/tzdata` | RPC / API маршрут |

## 4. Ключевые серверные структуры данных (IL2CPP Схемы)

### Класс `BCGAttributeDataBase`
- **Сборка:** `Assembly-CSharp.dll`
- **Поля:**
  - `<StatMods>k__BackingField`
  - `<SigMods>k__BackingField`
  - `<BuffMods>k__BackingField`
  - `<SpecialAttackCount>k__BackingField`
  - `<HPMax>k__BackingField`
  - `<HPMaxBase>k__BackingField`
  - `<HP>k__BackingField`
  - `<Attack>k__BackingField`
  - `<AttackBase>k__BackingField`
  - `<Armor>k__BackingField`
  - `<CritChance>k__BackingField`
  - `<CritDamage>k__BackingField`
  - `<PerfectBlockChance>k__BackingField`
  - `<BlockProficiency>k__BackingField`
  - `<ManaGain>k__BackingField`
  - `<ManaStart>k__BackingField`
  - `<ResistMagic>k__BackingField`
  - `<ResistPhysical>k__BackingField`
  - `<StunTime>k__BackingField`
  - `<StunChance>k__BackingField`
  - `<HeroRating>k__BackingField`
  - `<HeroRatingHP>k__BackingField`
  - `<HeroRatingAttack>k__BackingField`
  - `<HeroRatingHPBase>k__BackingField`
  - `<HeroRatingAttackBase>k__BackingField`
  - `isModified`
- **Ключевые методы (52):** `.ctor`, `Clone`, `get_StatMods`, `set_StatMods`, `get_SigMods`, `set_SigMods`, `get_BuffMods`, `set_BuffMods`, `get_SpecialAttackCount`, `set_SpecialAttackCount`, `get_HPMax`, `set_HPMax`

### Класс `TFBCGAttributeData`
- **Сборка:** `Assembly-CSharp.dll`
- **Поля:**
  - `_buffType`
  - `_sigBuffType`
  - `_critRate`
  - `_resistCritRate`
  - `_resistCritDamage`
  - `_specialBonus`
  - `_projectileBonus`
  - `_classPower`
  - `_armorPenetration`
  - `_blockPenetration`
- **Ключевые методы (12):** `.ctor`, `get_BuffType`, `get_SigBuffType`, `get_CritRate`, `get_ResistCritRate`, `get_ResistCritDamage`, `get_SpecialBonus`, `get_ProjectileBonus`, `get_ClassPower`, `set_ClassPower`, `get_ArmorPenetration`, `get_BlockPenetration`

### Класс `TFBCGCharacterData`
- **Сборка:** `Assembly-CSharp.dll`
- **Поля:**
  - `<Faction>k__BackingField`
  - `<Subgroup>k__BackingField`
  - `<Generation>k__BackingField`
  - `<AIPersonality>k__BackingField`
  - `<VictoryStage>k__BackingField`
  - `<SpecialStage>k__BackingField`
- **Ключевые методы (14):** `Create`, `.ctor`, `get_Faction`, `set_Faction`, `get_Subgroup`, `set_Subgroup`, `get_Generation`, `set_Generation`, `get_AIPersonality`, `set_AIPersonality`, `get_VictoryStage`, `set_VictoryStage`

### Класс `BCGUserData`
- **Сборка:** `Assembly-CSharp.dll`
- **Поля:**
  - `heroes`
  - `entities`
  - `evoBlueprints`
  - `savedTeams`
  - `activeTeams`
  - `_evoBlueprintsMax`
  - `blueprintsMax`
  - `teamSizeMax`
  - `teamCountMax`
  - `_evoFragments`
- **Ключевые методы (7):** `.ctor`, `HasActiveTeamType`, `HasActiveTeam`, `SetInventoryMax`, `GetInventoryMax`, `SetInventoryFrag`, `GetInventoryFrag`

### Класс `BCGUserDataUpdate`
- **Сборка:** `Assembly-CSharp.dll`
- **Поля:**
  - `evoBlueprints`
  - `evoBlueprintsOld`
  - `evoBlueprintsMax`
  - `evoBlueprintsMaxOld`
  - `evoFragments`
  - `evoFragmentsOld`
- **Ключевые методы (1):** `.ctor`

### Класс `FighterInitData`
- **Сборка:** `Assembly-CSharp.dll`
- **Поля:**
  - `BotName`
  - `BotTag`
  - `PlayerName`
  - `PlayerTag`
  - `Portrait`
  - `NormalizedHealth`
  - `NormalizedMana`
  - `NumSpecials`
  - `MaxSpecials`
  - `Rating`
  - `Rarity`
  - `AttackBonus`
  - `Awakened`
  - `IsBoss`
  - `Class`
  - `ModClass`

### Класс `FightResultsData`
- **Сборка:** `Assembly-CSharp.dll`
- **Поля:**
  - `IsWin`
  - `IsTimeout`
  - `SuccessfulHits`
  - `HitsReceived`
  - `HighestCombo`
  - `FightType`
  - `PlayerBotName`
  - `OpponentBotName`
  - `BonusPoints`
  - `Rewards`
  - `WithheldRewards`
  - `ActiveQuest`
  - `QuestFightData`
  - `PVPFightData`
  - `PVPRaidFightData`
  - `AveFightData`
- **Ключевые методы (1):** `.ctor`

### Класс `Quests.ActiveQuest`
- **Сборка:** `Assembly-CSharp.dll`
- **Поля:**
  - `<category>k__BackingField`
  - `<qid>k__BackingField`
  - `<config>k__BackingField`
  - `<data>k__BackingField`
  - `<map>k__BackingField`
  - `<battlegroups>k__BackingField`
  - `quest`
  - `base_`
  - `mission`
- **Ключевые методы (76):** `.ctor`, `UpdateLegacyQuest`, `.ctor`, `.ctor`, `Dispose`, `ConfigChangedCallback`, `Join`, `Quit`, `ClaimGenerator`, `CanClaimGenerator`, `GetClaimGeneratorCountdown`, `Move`

### Класс `Quests.MapTile`
- **Сборка:** `Assembly-CSharp.dll`
- **Поля:**
  - `_barrier`
  - `isWaypoint`
  - `<bossSocket>k__BackingField`
  - `<towerSocket>k__BackingField`
  - `<buildingSocket>k__BackingField`
  - `quest`
  - `mission`
  - `summary`
- **Ключевые методы (25):** `.ctor`, `.ctor`, `.ctor`, `Deserialize`, `get_boss`, `get_tower`, `get_building`, `get_generator`, `GetBarrier`, `HasTile`, `HasIncomingBuffs`, `HasIncomingBuffs`

### Класс `Quests.Summary`
- **Сборка:** `Assembly-CSharp.dll`
- **Поля:**
  - `<layout>k__BackingField`
  - `<minDifficulty>k__BackingField`
  - `<maxDifficulty>k__BackingField`
  - `<difficulty>k__BackingField`
  - `<points>k__BackingField`
  - `curves`
  - `difficultyRanges`
  - `<teamSettings>k__BackingField`
  - `<autocompleteSettings>k__BackingField`
  - `<autocompleteStep>k__BackingField`
  - `<autocompleteUnlocked>k__BackingField`
- **Ключевые методы (35):** `.ctor`, `Deserialize`, `UpdateProgression`, `get_layout`, `set_layout`, `get_minDifficulty`, `set_minDifficulty`, `get_maxDifficulty`, `set_maxDifficulty`, `GetCost`, `GetCompletionRewards`, `GetMasteryRewards`

### Класс `Quests.Act`
- **Сборка:** `Assembly-CSharp.dll`
- **Поля:**
  - `fsImage1`
  - `fsImage2`
- **Ключевые методы (3):** `.ctor`, `.ctor`, `Populate`

### Класс `Quests.Chapter`
- **Сборка:** `Assembly-CSharp.dll`
- **Поля:**
  - `fsImage1`
  - `fsImage2`
- **Ключевые методы (3):** `.ctor`, `.ctor`, `Populate`

### Класс `EB.Sparx.LoginManager`
- **Сборка:** `Assembly-CSharp-firstpass.dll`
- **Поля:**
  - `BENCHMARK_NAME`
  - `_config`
  - `_api`
  - `_user`
  - `_loginData`
  - `_initialized`
  - `_lastAuthenticator`
  - `_authData`
  - `_serverTag`
  - `_authenticators`
  - `_authenticatorsToCapture`
  - `_assembliesToSearch`
  - `_assignUnique`
  - `_seperatorToken`
  - `_matEnabled`
  - `_emailOptIns`
  - `_capturedAuthData`
  - `_submittingCapturedAuthData`
  - `_lastSubmitAttemptTime`
  - `_lastError`
  - `<LoginState>k__BackingField`
  - `UserLoggedIn`
  - `UserLinked`
- **Ключевые методы (68):** `get_LocalUser`, `get_LocalUserId`, `get_LoginState`, `set_LoginState`, `get_LoginData`, `get_Authenticators`, `get_AuthenticatorName`, `get_AuthData`, `get_ServerTag`, `get_AssignUnique`, `get_SeperatorToken`, `get_EmailOptIns`

### Класс `EB.Sparx.TuningManager`
- **Сборка:** `Assembly-CSharp-firstpass.dll`
- **Поля:**
  - `_data`
  - `TuningAPIVersion`
  - `Notify`
- **Ключевые методы (17):** `get_Version`, `get_Name`, `Initialize`, `SetApiEndPoint`, `Connect`, `Disconnect`, `Refresh`, `OnRefresh`, `Apply`, `Apply`, `GetString`, `GetInt`

### Класс `EB.Sparx.WalletManager`
- **Сборка:** `Assembly-CSharp-firstpass.dll`
- **Поля:**
  - `_walletApiEnabled`
  - `_config`
  - `_api`
  - `_balance`
  - `_fetchBalance`
- **Ключевые методы (15):** `get_Balance`, `Initialize`, `SetApiEndPoint`, `Connect`, `OnEnteredForeground`, `Disconnect`, `Async`, `Fetch`, `Credit`, `Debit`, `OnCredit`, `OnDebit`

### Класс `EB.Sparx.InventoryManager`
- **Сборка:** `Assembly-CSharp-firstpass.dll`
- **Поля:**
  - `_config`
  - `_api`
  - `_data`
  - `_used`
  - `_overrides`
  - `InventoryChanged`
  - `ForceOverride`
  - `EverythingFree`
  - `_overrideKeys`
- **Ключевые методы (36):** `get__inventory`, `get_Inventory`, `add_InventoryChanged`, `remove_InventoryChanged`, `get_IsOverriden`, `get_OverrideCount`, `GetOverrideItem`, `Initialize`, `SetApiEndPoint`, `Connect`, `Disconnect`, `Override`

### Класс `EB.Sparx.ObjectivesManager`
- **Сборка:** `Assembly-CSharp-firstpass.dll`
- **Поля:**
  - `_objectives`
  - `_objectivesGroupData`
  - `OrderedObjectiveTypeCollectionsDictionary`
  - `_api`
  - `<CDN>k__BackingField`
  - `ObjectiveFactories`
  - `OnObjectiveActivate`
  - `OnObjectiveComplete`
  - `OnObjectiveUpdate`
  - `OnLogEvent`
- **Ключевые методы (34):** `get_Objectives`, `set_Objectives`, `GetObjectiveTypeCollections`, `GetCurrentObjectives`, `GetCurrentObjectiveCount`, `GetObjectiveById`, `GetObjectiveById`, `get_CDN`, `set_CDN`, `add_OnObjectiveActivate`, `remove_OnObjectiveActivate`, `add_OnObjectiveComplete`
