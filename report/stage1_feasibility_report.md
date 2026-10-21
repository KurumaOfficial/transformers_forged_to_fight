# ЭТАП 1: Проверка осуществимости и барьеры защиты
## Transformers: Forged to Fight (com.kabam.bigrobot v9.2.0)

---

### Резюме осуществимости и статусы

| Точка проверки | Статус / Результат | Уровень доказательства | Вывод |
|---|---|---|---|
| **1. TLS и SSL Pinning** | `HttpEndPoint` поддерживает схему `http://`. При `http://` класс `TcpClientBouncy` отключает TLS, и проверка сертификатов BouncyCastle (`NotifyServerCertificate` -> `TlsFatalAlert(42)`) **не вызывается вообще**. | **[STATIC]** (декомпиляция `0x1334414`, `0x1236CE8`, `0x1234430`, `0x14EC940`) | **Бинарный патч НЕ нужен**, если указать `http://` в `endpointconfig`. |
| **2. Класс `AcceptAllCertificates`** | `WWWk2018.AcceptAllCertificates` (RVA `0x140F830`) возвращает `true`. Относится к вторичной загрузке внешних изображений через `UnityWebRequest`, а **не** к RPC-протоколу Sparx. | **[STATIC]** (декомпиляция `0x140F830`, `WWWk2018`) | Протокол Sparx обслуживается `TcpClientBouncy`, а не UnityWebRequest. |
| **3. Античит `libapkprotect.so`** | `JNI_OnLoad` (`0xD16C`) возвращает `JNI_VERSION_1_6` без краша. Функции `APK_Check_*` вычисляют SHA1/HMAC по файлу APK и передают в `EB.Sparx.Protect.BuildLoginData`, откуда хэш отправляется в тело `/auth/login`. | **[STATIC]** (декомпиляция `libapkprotect.so` @ `0xD16C`, `0x12FA8B4`) | При переподписи APK клиент **не падает**. Сервер эмуляции принимает любой хэш. |
| **4. AndroidManifest: `usesCleartextTraffic` и сокеты** | `targetSdkVersion=30` (Android 11). `usesCleartextTraffic` в манифесте **не задан** (по умолчанию Java HTTP блокируется). Однако RPC Sparx, WebSocket и ENet идут через **нативные BSD-сокеты Linux** (`System.Net.Sockets.Socket` и `libenetlib.so`), минуя Java `NetworkSecurityPolicy`. | **[STATIC]** (парсинг AXML `AndroidManifest.xml`, декомпиляция `EB.Net.TcpClientBouncy`, `NetworkENet`) | Нативные сокеты клиента связываются с `http://127.0.0.1:8080` без системных блокировок. |
| **5. Расхождение 102 vs 108 бандлов** | 108 файлов `toc.txt` распарсены как JSON: 15 манифестов содержат `"bundles": {}` (пакеты без монолитных бандлов), остальные манифесты декларируют от 1 до 4 бандлов. Суммарно во всех TOC ровно **102 бандла**, и на диске в `assets/assetpack/` лежит ровно **102 бандла**. | **[STATIC]** (парсинг всех 108 TOC JSON + листинг файлов) | **Потерь 0**. Ни один бандл не утерян. |
| **6. Боевые расчёты и числа с сервера** | В боевую математику входят серверные таблицы `BCGAttributeDataBase` (`AttackBase`, `HPMaxBase`, `Armor`, `CritChance`, `CritDamage`, `BlockProficiency`, `ResistMagic`, `ResistPhysical`, `StunTime`) и таблица `/tuning`. | **[STATIC]** (декомпиляция `BCGAttributeDataBase` @ `0xC1486C`, `TuningManager` @ `0x15DA900`) | Клиент рассчитывает механику боя, но абсолютные числа шлёт сервер. |
| **7. Подпись APK (v1/v2/v3) и zipalign** | APK переподписан с использованием `uber-apk-signer` (v1.3.0): выполнен `zipalign` и внедрены сигнатуры **v1, v2 и v3** (требование Android 11+ для targetSdk 30). | **[RUN]** (проверено запуском `uber-apk-signer -y`) | APK полностью совместим с Android 11, 12, 13, 14+. |
| **8. Подмена URL в `endpointconfig`** | Выполнен прямой бинарный патч `assets/bin/Data/e1917cd7a6bdb4492a247b8f758df2ae` с пересчётом 64-битного заголовка SerializedFile (`fileSize`), таблицы объектов (`byte_size`) и длины `m_Script`. Результат проверен повторным парсингом. | **[RUN]** (проверено скриптом `work/verify_endpoint_patch.py`) | Unity десериализует ровно чистый JSON `{"Default":{"Prod":"http://127.0.0.1:8080"}}`. |
| **9. Схема логина и заглушка сервера** | Клиент запущен на эмуляторе, прошёл `auth/init -> enumerate -> prelogin -> login`, все подсистемы логина и **дошёл до 3D-базы HomeFlow**. Полный лог и скриншоты приложены. | **[RUN]** (2026-10-21, `work/stage1_logcat_full_final.txt`, `server/requests.jsonl`, `work/FINAL_hub.png`) | Этап 1 подтверждён. Содержимое ответов по-прежнему частично [ASSUMED]; см. FIDELITY/LEDGER. |

---

## 1. Детальный разбор сетевого транспорта, Cleartext Traffic и TLS

### 1.1. Откуда клиент берет адрес сервера?
- **[STATIC]** Класс [`Setup`](file:///C:/Users/gameg/Desktop/TFTF/work/il2cpp_dump/dump.cs#L421741) в методе `Awake` (RVA `0xA2A74C` в `libil2cpp.so`) проверяет статическое поле `Setup._apiEndPoint`.
- Если оно пустое, вызывается `EB.Version.GetApiEndPoint()` (RVA `0x1C077B0`).
- Метод `EB.Version.LoadApiEndPoints()` (RVA `0x1C074D0`) загружает ресурс `endpointconfig` через `Resources.Load("endpointconfig")`.
- Этот ресурс физически расположен в файле [`assets/bin/Data/e1917cd7a6bdb4492a247b8f758df2ae`](file:///C:/Users/gameg/Desktop/TFTF/work/unpacked/assets/bin/Data/e1917cd7a6bdb4492a247b8f758df2ae).
- В оригинале внутри файла содержится JSON:
  ```json
  {"Default":{"Prod":"https://tform-0901-hzlhiniyfcwf.tf-cdn.net"}}
  ```

### 1.2. Допустим ли `http://` вместо `https://`?
- **[STATIC]** Метод `EB.Sparx.EndPointFactory.Create(string url, EndPointOptions options)` (RVA `0x1334414`):
  - Создает `System.Uri` из переданного URL.
  - Извлекает схему (`Uri.get_Scheme`).
  - Сравнивает со строкой `"http"` (RVA `0x13344dc`) и `"https"` (RVA `0x13344fc`).
  - Обе схемы признаются валидными и направляются на создание `HttpEndPoint`.
- **[STATIC]** `EB.Net.TcpClientFactory.Create(bool secure, bool buffered)` (RVA `0x1236CE8`):
  - При `url.StartsWith("http://")` флаг `secure` устанавливается в `false`.
  - В конструкторе `EB.Net.TcpClientBouncy` (RVA `0x1234430`) значение сохраняется в поле `_secure` (смещение `0x48`).
  - При `_secure == false` в `TcpClientBouncy.TryConnect` (RVA `0x1235894`) проверка `cbz w8, #0x12359e8` **полностью обходит** создание TLS-клиента BouncyCastle и handshake. Устанавливается обычный POSIX TCP-сокет.
- **[STATIC]** В `EB.Net.TcpClientBouncy.MyTlsAuthentication.NotifyServerCertificate` (RVA `0x14EC940`):
  - При `https://` метод выполняет валидацию сертификата по встроенному хранилищу (`_certStore`). Если соответствие не найдено, на адресе `0x14ECB78` выбрасывается исключение `Org.BouncyCastle.Crypto.Tls.TlsFatalAlert(42)` (`bad_certificate`).
  - **Вывод:** При переводе URL на `http://` этот блок кода не выполняется. Клиент работает по открытому HTTP без каких-либо ошибок сертификатов.

### 1.3. AndroidManifest: `usesCleartextTraffic` и анализ всего сетевого трафика
При исследовании `AndroidManifest.xml` (парсинг AXML):
```xml
<manifest package="com.kabam.bigrobot" compileSdkVersion="30" ...>
  <uses-sdk minSdkVersion="23" targetSdkVersion="30" />
  <application ... />
```
- Атрибут `android:usesCleartextTraffic` **отсутствует**. На Android 9+ (API 28+) при `targetSdkVersion >= 28` системная политика Android по умолчанию запрещает открытый HTTP-трафик для Java-сети.
- Проанализированы все сетевые подсистемы игры:
  1. **Sparx RPC (`/auth/*`, `/tuning`, `/bcg/*`, `/account/*`)**:
     - Стек: `HttpEndPoint` -> `EB.Net.WebRequest` -> `EB.Net.TcpClientBouncy` -> `System.Net.Sockets.Socket`.
     - В IL2CPP C# сокеты компилируются в нативные вызовы Linux libc: `sys_socket`, `sys_connect`, `sys_send`, `sys_recv`.
     - Нативные вызовы libc исполняются напрямую в ядре Linux и **не проходят** через Java `HttpURLConnection` / `OkHttp` / `BlockGuardOs`. Соответственно, Java-политика `NetworkSecurityPolicy` на них **не действует**.
  2. **WebSocket (чат, push-нотификации)**:
     - Стек: `TalkWebSocket` -> `EB.Net.WebSocket` -> `ITcpClient` (`TcpClientBouncy`).
     - Прямые TCP-сокеты libc.
  3. **ENet (сетевой бой)**:
     - Стек: `NetworkENet` -> `libenetlib.so`.
     - Прямые UDP-сокеты libc (`socket(AF_INET, SOCK_DGRAM, 0)`).
  4. **MOTD (сообщение дня)**:
     - Передаётся внутри пакета синхронизации Sparx RPC (`MOTDManager.OnData(IDictionary)`).
  5. **Ассет-бандлы (102 шт.)**:
     - Упакованы локально в APK (`assets/assetpack/`) и монтируются через `PackDriver` из локальной файловой системы, а не по сети.
  6. **Вторичные изображения и CDN (`WWWk2018`)**:
     - Использует `UnityEngine.Networking.UnityWebRequest`. На Android UnityWebRequest делегирует загрузку Java-классу Unity Player (`HttpURLConnection`).
     - **Потенциальный риск:** Если наш сервер начнёт отдавать внешние HTTP-ссылки на картинки (например, аватарки на внешнем CDN), Java заблокирует их без `usesCleartextTraffic="true"`.
     - **Решение:** Для первого этапа (вход в главное меню) внешние ссылки не передаются. Если в будущем потребуется скачивание картинок с локального HTTP-сервера, в манифест можно внедрить байты флага `android:usesCleartextTraffic="true"` (`0x010104ec`) либо отдавать статику по локальному HTTPS.

---

## 2. Анализ античита `libapkprotect.so`

- **[STATIC]** Библиотека экспортирует функции:
  - `JNI_OnLoad` (смещение `0xD16C`): не осуществляет проверок целостности, только возвращает `JNI_VERSION_1_6`.
  - `APK_Check_Start` (смещение `0x15598`)
  - `APK_Check_Start_Salt` (смещение `0x1560C`)
  - `APK_Check_Step` (смещение `0xD480`)
  - `APK_Check_Complete` (смещение `0xD4A0`)
  - `APK_GetLibraries` (смещение `0xD4E4`)
- **[STATIC]** Класс C# `APKSignature` (TypeDefIndex: 4630):
  - Оборачивает эти функции через P/Invoke.
  - Содержит методы `SyncGenerateSHA1SignatureFromAPK` и `SyncGenerateHMACSignatureFromAPK`.
- **[STATIC]** Класс C# `EB.Sparx.Protect` (TypeDefIndex: 7580):
  - Метод `BuildLoginData(IDictionary preloginData)` (RVA `0x12FA8B4`):
    - Получает salt/challenge из ответа `/auth/prelogin`.
    - Вызывает `APKSignature.SyncGenerateHMACSignatureFromAPK`.
    - Добавляет вычисленную подпись, список сборок (`GetLoadedAssemblies`) и архитектуру в словарь логина `/auth/login`.
- **Вывод:** `libapkprotect.so` является **пассивным сборщиком контрольной суммы для бэкенда**, а не активным защитником времени запуска. При переподписи APK игра не крашится. Наш локальный сервер просто принимает любой хэш.

---

## 3. Разрешение проблемы 102 vs 108 ассет-бандлов

В прошлом отчете отмечалось кажущееся расхождение: 108 манифестов против 102 бандлов.

- **[STATIC]** Проанализированы все 108 файлов `toc.txt` (манифесты Unity Play Asset Delivery):
  - 15 файлов `toc.txt` имеют пустое поле `"bundles": {}` (содержат отдельные несжатые ассеты, не объединённые в бандлы).
  - 93 файла `toc.txt` декларируют от 1 до 4 бандлов.
  - Сумма всех объявленных файлов `.assetbundle` по всем 108 TOC: **ровно 102**.
  - Количество файлов `.assetbundle` в папке `assets/assetpack/`: **ровно 102**.
- **Вывод:** Расхождение полностью объяснено. Ни один бандл не потерян. Все ассеты присутствуют внутри APK.

---

## 4. Патчинг `endpointconfig`: Бинарная структура и верификация

### 4.1. Анализ формата Unity SerializedFile (Format 22 / Unity 2020.3)
Файл [`assets/bin/Data/e1917cd7a6bdb4492a247b8f758df2ae`](file:///C:/Users/gameg/Desktop/TFTF/work/unpacked/assets/bin/Data/e1917cd7a6bdb4492a247b8f758df2ae):
- Смещение `0x00`: заголовок SerializedFile (версия 22).
- Смещение `0x1C`: `fileSize` (big-endian uint32) = 4188 байт.
- Смещение `0x24`: `data_offset` = 4096 (`0x1000`).
- Смещение `0x60`: Таблица объектов (Object Table, ровно 1 объект TextAsset).
- Смещение `0x70`: `byte_size` объекта (little-endian uint32) = 92 байта.
- Смещение `0x1000` (4096): Полезная нагрузка TextAsset:
  - `0x1000`: длина имени = 14 (`0x0E, 0x00, 0x00, 0x00`)
  - `0x1004`..`0x1011`: `"endpointconfig"` (14 байт)
  - `0x1012`..`0x1013`: `\x00\x00` (выравнивание до 4 байт, 16 байт)
  - `0x1014`: длина скрипта = 65 (`0x41, 0x00, 0x00, 0x00`)
  - `0x1018`..`0x1058`: JSON `{"Default":{"Prod":"https://tform-0901-hzlhiniyfcwf.tf-cdn.net"}}` (65 байт)
  - `0x1059`..`0x105B`: `\x00\x00\x00` (выравнивание до 4 байт, 68 байт)
  - Итого размер объекта: $4 + 16 + 4 + 68 = 92$ байта. $4096 + 92 = 4188$ байт.

### 4.2. Как `patch_apk_endpoint.py` переписывает файл
При установке `http://127.0.0.1:8080`:
- Новый JSON: `{"Default":{"Prod":"http://127.0.0.1:8080"}}` (длина 44 байта, $44 \pmod 4 = 0$, выравнивание 0 байт).
- Новый размер объекта: $4 + 16 + 4 + 44 = 68$ байт.
- Новый размер файла: $4096 + 68 = 4164$ байта.
- Скрипт атомарно обновляет:
  1. `fileSize` по смещению `0x1C` -> 4164 (`0x00001044`).
  2. `byte_size` по смещению `0x70` -> 68 (`0x44000000`).
  3. Длину скрипта по смещению 4116 -> 44 (`0x2C000000`).
  4. Записывает новый JSON и обрезает файл ровно до 4164 байт.
- **[RUN] Верификация повторным чтением (`verify_endpoint_patch.py`):**
  Симулированный десериализатор Unity считывает заголовок, находит объект по смещению 4096, считывает имя `"endpointconfig"` и текст `{"Default":{"Prod":"http://127.0.0.1:8080"}}`. Длина прочитанных байт совпадает с размером файла до последнего байта.

---

## 5. Подпись APK: zipalign + apksigner (v1, v2, v3)

Поскольку `targetSdkVersion = 30` (Android 11), использование старого `jarsigner` (v1) приводит к отказу в установке на современных телефонах (`INSTALL_PARSE_FAILED_NO_CERTIFICATES: No APK Signature Scheme v2 signature`).

- Использована утилита `work/uber-apk-signer.jar` (v1.3.0).
- **[RUN] Процесс сборки и результат:**
  1. Оригинальный APK скопирован в `work/patched_build/tftf_unsigned.apk` (оригинал не модифицируется).
  2. Внедрён пропатченный `endpointconfig` через 7-Zip (`7z a -tzip`).
  3. Выполнен `zipalign` с выравниванием ресурсов по 4-байтной границе.
  4. Произведена подпись тестовым сертификатом по схемам **v1, v2 и v3**.
  5. Сгенерирован финальный APK: `work/patched_build/tftf_patched_v9.2.0.apk`.
  6. Проверка верификатором:
     ```
     - zipalign verified
     - signature verified [v1, v2, v3]
     Successfully processed 1 APKs and 0 errors in 4.18 seconds.
     ```

---

## 6. Реальная последовательность запросов до HomeFlow `[RUN]`

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

Заглушка [`server/stub_server.py`](file:///C:/Users/gameg/Desktop/TFTF/server/stub_server.py)
логирует каждый запрос в `server/requests.jsonl` с `flush`; на неизвестные пути
отдаёт пустой `result`.

## 7. Инструкция по запуску на эмуляторе (актуальная)

Проверено на `TFTF_AVD` (Pixel 4, API 30, x86_64, AEHD).

### Шаг 1. Эмулятор
```powershell
$env:ANDROID_SDK_ROOT="C:\Users\gameg\Desktop\TFTF\work\android-sdk"
& "$env:ANDROID_SDK_ROOT\emulator\emulator.exe" -avd TFTF_AVD -no-boot-anim -gpu auto
adb wait-for-device
adb shell getprop ro.product.cpu.abilist
```
Ожидается строка, содержащая `arm64-v8a` (трансляция ARM64 на x86_64).

### Шаг 2. Сервер и reverse
```powershell
python server\stub_server.py 8080
adb reverse tcp:8080 tcp:8080
```

### Шаг 3. Установка патченного APK
```powershell
adb install -r --no-incremental "work\patched_build\tftf_patched_v9.2.0.apk"
```
Оригинальный APK не изменяется; патч только в копии.

### Шаг 4. Запуск и автоматический тап PLAY NOW
```powershell
adb shell am force-stop com.kabam.bigrobot
adb shell monkey -p com.kabam.bigrobot -c android.intent.category.LAUNCHER 1
# подождать сплэш ~55 с, затем:
python work\auto_play.py
```
`auto_play.py` находит зелёную кнопку PLAY NOW по цвету и тапает её.
PLAY NOW — обычный стартовый экран этой сборки на холодном запуске, не ошибка.
Если данные приложения сохранены, экран может не появиться; скрипт тогда
завершится с кодом 2, и тап не нужен.

### Шаг 5. Полный logcat
```powershell
adb logcat -c
adb logcat -v threadtime > work\logcat_full.txt
```
Без фильтров. Для этапа 1 уже снят `work/stage1_logcat_full_final.txt`.

### Шаг 6. Проверка
- `server/requests.jsonl` — последовательность запросов;
- `work/FINAL_hub.png` — хаб;
- `work/FINAL_story_chapters.png` — Story → Act 1 → Chapter 1.
