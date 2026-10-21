# Матрица охвата протокола (факты)

Дата: 2026-10-21. Источник последовательности: `server/requests.jsonl`
(чистый прогон 21:23:13–21:24:45 UTC, 44 запроса). Обозначения:
`REAL` — значение/схема подтверждены кодом клиента и/или запуском;
`ASSUMED` — заглушка, оригинального значения нет; `EMPTY` — пустой ответ;
`NOT OBSERVED` — клиент не вызывал.

| # | Запрос клиента | Что отдаёт заглушка | Статус | Чем подтверждено |
|---|---|---|---|---|
| 1 | `GET /auth/init` | `{status:"ok",session:"..."}` | ASSUMED | [RUN] клиент стартует |
| 2 | `POST /auth/init` | то же | ASSUMED | [RUN] повторный запуск |
| 3 | `POST /auth/enumerate` | `[]` | REAL (форма) | [RUN] пустой массив принят |
| 4 | `POST /auth/prelogin` | `{salt:"",status:"ok"}` | REAL (salt="") | [RUN] вход проходит |
| 5 | `POST /auth/login` | login_response.json | ASSUMED | [RUN] stoken/auth.device приняты |
| 6 | `GET /account/data` | account_data.json | ASSUMED | [RUN] хаб без NullRef |
| 7 | `GET /bcg/getLoginData` | bcg_login_data.json | ASSUMED | [RUN] каталог принят; ростер пуст |
| 8 | `GET /tuning` | tuning_data.json | ASSUMED | [RUN] клиент не падает |
| 9 | `GET /payments/payouts` | пустой | EMPTY | [RUN] |
| 10 | `GET /autorefresh/gacha/refresh` | generic | ASSUMED | [RUN] |
| 11 | `GET /autorefresh/gamestore/refresh` | generic | ASSUMED | [RUN] |
| 12 | `GET /performance/profile` | performance_profile.json | ASSUMED | [RUN] |
| 13 | `GET /autorefresh/objectives/refresh` | generic | ASSUMED | [RUN] |
| 14 | `GET /redeemer/refresh` | пустой | EMPTY | [RUN] |
| 15 | `GET /events/refresh` | пустой | EMPTY | [RUN] |
| 16 | `GET /autorefresh/prizes/refresh` | generic | ASSUMED | [RUN] |
| 17 | `GET /ds/10001/` | datasync_profile.json | ASSUMED | [RUN] |
| 18 | `POST /tutorial/get-login-data` | tutorial_data.json | REAL (s=completed) | [RUN] обход туториала |
| 19 | `GET /autorefresh/message/refresh` | generic | ASSUMED | [RUN] |
| 20 | `GET /gamestats/get-login-data` | пустой | EMPTY | [RUN] |
| 21 | `GET /offers/getLoginData` | пустой | EMPTY | [RUN] |
| 22 | `GET /autorefresh/kabamsignup/refresh` | generic | ASSUMED | [RUN] |
| 23 | `GET /autorefresh/missionsconfig/refresh` | missions_config.json | ASSUMED | [RUN] |
| 24 | `GET /autorefresh/ads/refresh` | generic | ASSUMED | [RUN] |
| 25 | `GET /push/token` | `{status,websocket}` | ASSUMED | [RUN] |
| 26 | `GET /inventory` | `{items:[]}` | ASSUMED | [RUN] |
| 27 | `GET /autorefresh/quests/refresh` | generic | ASSUMED | [RUN] |
| 28 | `GET /quests/quest-list` | quest_list.json | REAL (ключи) / ASSUMED (контент) | [STATIC]+[RUN] глава и тайл появились |
| 29 | `GET /quests/quest-active` | `{activeQuests:[],instances:[]}` | ASSUMED | [RUN] пустой принят |
| 30 | `GET /autorefresh/ave/refresh` | generic | ASSUMED | [RUN] |
| 31 | `GET /autorefresh/raid/refresh` | generic | ASSUMED | [RUN] |
| 32 | `GET /base/active` | base_active.json | REAL (pathData) / ASSUMED (контент) | [RUN] база рендерится |
| 33 | `GET /pvp/get-login-data` | пустой | EMPTY | [RUN] |
| 34 | `GET /autorefresh/ai/refresh` | generic | ASSUMED | [RUN] |
| 35 | `GET /gamestats/check-login-achievements` | `[]` | REAL (форма) | [RUN] |
| 36 | `GET /quests/quest-progression` | quest_progression.json | ASSUMED | [RUN] запрос наблюдается |
| 37 | `GET /chat/data` | пустой | EMPTY | [RUN] |
| 38 | `POST /telemetry` | `{}` | EMPTY | [RUN] |
| 39 | `POST /userprofile/` | `{}` | EMPTY | [RUN] |
| 40 | `POST /ds/10001` | `{}` | EMPTY | [RUN] |
| 41 | `GET /autorefresh/grouprefresh` | `{}` | EMPTY | [RUN] поллинг |
| 42 | `POST /quests/quest-detail/{qid}` | quest_detail.json | REAL (запрос) / ASSUMED (ответ) | [RUN] экран деталей |
| 43 | `POST /quests/quest-begin/{qid}` | — | NOT OBSERVED | ростер пуст, START серый |
| 44 | `POST /matches/activate-match/{type}` | — | NOT OBSERVED | — |
| 45 | `POST /matches/match-loaded/{type}/{id}` | — | NOT OBSERVED | — |
| 46 | `POST /matches/resolve-match/{type}` | — | NOT OBSERVED | — |
| 47 | `GET /bcg/getUserData` | bcg_user_data.json | NOT OBSERVED | клиент не запросил; BOTS падает в `SetFeaturedHeroData` |
| 48 | `POST /util/ping` | `{}` | ASSUMED | [RUN] более ранние прогоны |
| 49 | `POST /krash` | `{status,id}` | ASSUMED | [RUN] debug |
| 50 | `POST /bugs` | `{}` | EMPTY | [RUN] debug |
| 51 | `GET /health` | `{}` | EMPTY | [RUN] debug |
| 52 | `GET /ws` | 400 | NOT IMPLEMENTED | [RUN] клиент ретраит |

## Легенда достоверности
- **REAL (ключи)** — имена полей из `dump.cs`/`stringliteral.json`, поведение
  подтверждено запуском. Значения всё равно могут быть ASSUMED.
- **ASSUMED** — придуманные числа/структуры. Это не оригинал Kabam.
- **EMPTY** — пустой ответ; клиент его принимает, но экран может быть пустым.
- **NOT OBSERVED** — путь не вызывался; схема в SPEC помечена соответственно.

## Что проверяют 9 тестов
`tests/test_api_schemas.py` проверяет **внутреннюю согласованность заглушки**:
наличие конверта `ts/result`, массивы там, где клиент ждёт массив, обязательные
ключи `privacySettings`, `pathData`, квестовые `act/chapter/mission` и т.д.
Они **не доказывают** совместимость с клиентом. Совместимость доказывается
только запуском: `server/requests.jsonl` + `work/stage1_logcat_full_final.txt`
+ скриншоты.
