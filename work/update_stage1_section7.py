p = r'.\report\stage1_feasibility_report.md'
t = open(p, encoding='utf-8').read()
s = t.index('## 7.')
new = '''## 7. Инструкция по запуску на эмуляторе (актуальная)

Проверено на `TFTF_AVD` (Pixel 4, API 30, x86_64, AEHD).

### Шаг 1. Эмулятор
```powershell
$env:ANDROID_SDK_ROOT=".\\work\\android-sdk"
& "$env:ANDROID_SDK_ROOT\\emulator\\emulator.exe" -avd TFTF_AVD -no-boot-anim -gpu auto
adb wait-for-device
adb shell getprop ro.product.cpu.abilist
```
Ожидается строка, содержащая `arm64-v8a` (трансляция ARM64 на x86_64).

### Шаг 2. Сервер и reverse
```powershell
python server\\stub_server.py 8080
adb reverse tcp:8080 tcp:8080
```

### Шаг 3. Установка патченного APK
```powershell
adb install -r --no-incremental "work\\patched_build\\tftf_patched_v9.2.0.apk"
```
Оригинальный APK не изменяется; патч только в копии.

### Шаг 4. Запуск и автоматический тап PLAY NOW
```powershell
adb shell am force-stop com.kabam.bigrobot
adb shell monkey -p com.kabam.bigrobot -c android.intent.category.LAUNCHER 1
# подождать сплэш ~55 с, затем:
python work\\auto_play.py
```
`auto_play.py` находит зелёную кнопку PLAY NOW по цвету и тапает её.
PLAY NOW — обычный стартовый экран этой сборки на холодном запуске, не ошибка.
Если данные приложения сохранены, экран может не появиться; скрипт тогда
завершится с кодом 2, и тап не нужен.

### Шаг 5. Полный logcat
```powershell
adb logcat -c
adb logcat -v threadtime > work\\logcat_full.txt
```
Без фильтров. Для этапа 1 уже снят `work/stage1_logcat_full_final.txt`.

### Шаг 6. Проверка
- `server/requests.jsonl` — последовательность запросов;
- `work/FINAL_hub.png` — хаб;
- `work/FINAL_story_chapters.png` — Story → Act 1 → Chapter 1.
'''
open(p, 'w', encoding='utf-8').write(t[:s] + new)
print('ok')
