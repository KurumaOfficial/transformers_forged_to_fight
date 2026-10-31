import io
p = r'.\report\stage1_feasibility_report.md'
t = open(p, encoding='utf-8').read()
s = t.index('## 6.')
e = t.index('## 7.')
new6 = '''## 6. Реальная последовательность запросов до HomeFlow `[RUN]`

Ниже — не схема «по коду», а фактический порядок из `server/requests.jsonl` за
чистый запуск 2026-10-21 21:23:13–21:24:45 UTC (44 запроса). Полный лог:
`work/stage1_logcat_full_final.txt`, скриншоты: `work/FINAL_hub.png`,
`work/FINAL_story_chapters.png`.

```text
POST /auth/init
POST /auth/enumerate                    -> result: []  (пустой массив, не объект)
POST /auth/prelogin                     -> salt: ""
POST /auth/login                        -> auth.device: true, stoken
GET  /account/data
GET  /bcg/getLoginData
GET  /tuning
GET  /payments/payouts
GET  /autorefresh/gacha/refresh
GET  /autorefresh/gamestore/refresh
GET  /performance/profile
GET  /autorefresh/objectives/refresh
GET  /redeemer/refresh
GET  /events/refresh
GET  /autorefresh/prizes/refresh
GET  /ds/10001/
POST /tutorial/get-login-data
GET  /autorefresh/message/refresh
GET  /gamestats/get-login-data
GET  /offers/getLoginData
GET  /autorefresh/kabamsignup/refresh
GET  /autorefresh/missionsconfig/refresh
GET  /autorefresh/ads/refresh
GET  /push/token
GET  /inventory
GET  /autorefresh/quests/refresh
GET  /quests/quest-list
GET  /quests/quest-active
GET  /autorefresh/ave/refresh
GET  /autorefresh/raid/refresh
GET  /base/active
GET  /pvp/get-login-data
GET  /autorefresh/ai/refresh
GET  /gamestats/check-login-achievements
GET  /quests/quest-progression
GET  /chat/data
POST /telemetry
POST /userprofile/
POST /ds/10001
GET  /autorefresh/grouprefresh       (фоновый поллинг)
```

Важные поправки к прежним утверждениям:
- `/auth/enumerate` в этой сборке **принимает пустой массив** и после него клиент
  сам идёт в `prelogin/login`. Утверждение «нужен массив аккаунтов с
  `primary/user/authenticators`» для текущего сценария не подтвердилось. `[RUN]`
- `/auth/prelogin` с `salt: ""` не запускает `APK_Check_Start_Salt`; вход
  проходит. `[RUN]`
- В современном потоке **нет** `/bcg/getBaseHeroData`, `/bcg/getUserData`,
  `/wallet/fetch` на старте. Клиент запрашивает `/bcg/getLoginData`,
  `/inventory`; отдельного `/wallet/fetch` в чистом прогоне нет. `[RUN]`
- `/ws` в чистом прогоне до хаба не появился; веб-сокет — отдельная задача чата.
  В отладочных прогонах он ретраился с 400, потому что заглушка не умеет
  WebSocket-upgrade. `[RUN]`

Конверт Sparx (`EB.Sparx.Response` @ `0x12FD4C8`) остаётся прежним:
```json
{"ts": 1792189445, "result": {}, "sync": {}, "async": [], "error": null, "fatal": false, "retry": false}
```

Заглушка [`server/stub_server.py`](file:///./server/stub_server.py)
логирует каждый запрос в `server/requests.jsonl` с `flush`; на неизвестные пути
отдаёт пустой `result`.

'''
t = t[:s] + new6 + t[e:]
old = r'adb logcat -v time -s Unity:V ActivityManager:I Sparx:V CRASH:E *:E > work\logcat.txt'
new = r'adb logcat -v threadtime > work\logcat_full.txt'
if old in t:
    t = t.replace(old, new)
t += '''
---

## 8. Доказательства этапа 1 (сессия 2026-10-21) `[RUN]`

| Что | Файл / команда | Результат |
|---|---|---|
| Полный logcat без фильтров | `work/stage1_logcat_full_final.txt` | 136 КБ, от старта процесса до HomeFlow |
| Лог запросов | `server/requests.jsonl` | 44 запроса, последовательность выше |
| 3D-база (HomeFlow) | `work/FINAL_hub.png` | BASE/BOTS/FIGHT/…, кнопка FIGHT активна |
| Story → Act 1 → Chapter 1 | `work/FINAL_story_chapters.png` | «ACT 1», «Chapter 1: Arrival», тайл «1.1 Landing Site» |
| ABI эмулятора | `adb shell getprop ro.product.cpu.abilist` | `x86_64,x86,arm64-v8a,armeabi-v7a,armeabi` |
| Патч endpoint | `work/patched_build/tftf_patched_v9.2.0.apk` | внутри `{"Default":{"Prod":"http://127.0.0.1:8080"}}`, файл 4164 байта |
| Версия клиента | `adb shell dumpsys package com.kabam.bigrobot` | 9.2.0 / 123129100 / targetSdk 30 |

Скриншот хаба был получен после ручного тапа `PLAY NOW` на холодном старте;
автоматического входа в этом прогоне не было.
'''
open(p, 'w', encoding='utf-8').write(t)
print('ok', len(t))
