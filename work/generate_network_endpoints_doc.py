import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Read endpoints from string literals
with open(r".\work\string_literals.txt", "r", encoding="utf-8") as f:
    literals = f.readlines()

api_pattern = re.compile(r'^\[\d+\]\s*(/[a-zA-Z0-9_\-\./]+)$')
endpoints = set()
for l in literals:
    m = api_pattern.match(l.strip())
    if m:
        path = m.group(1)
        if not path.startswith(("/proc", "/sys", "/dev", "/system", "/data/local", "/lib", "/usr", "/etc")):
            endpoints.add(path)

by_service = {}
for ep in sorted(endpoints):
    parts = ep.strip("/").split("/")
    svc = parts[0] if parts else "root"
    by_service.setdefault(svc, []).append(ep)

with open(r".\work\all_game_classes.json", "r", encoding="utf-8") as f:
    classes = json.load(f)

# Find key Sparx data structures
key_structures = [
    "BCGManagerBase", "BCGAttributeDataBase", "TFBCGAttributeData", "TFBCGCharacterData",
    "BCGUserData", "BCGUserDataUpdate", "HeroDataShared", "FighterInitData", "FightResultsData",
    "Quests.ActiveQuest", "Quests.MapTile", "Quests.Summary", "Quests.Act", "Quests.Chapter",
    "EB.Sparx.LoginManager", "EB.Sparx.TuningManager", "EB.Sparx.WalletManager",
    "EB.Sparx.InventoryManager", "EB.Sparx.ObjectivesManager"
]

doc_lines = []
doc_lines.append("# Network Endpoints, Protocols & Data Structures")
doc_lines.append("## Transformers: Forged to Fight (v9.2.0 - com.kabam.bigrobot)\n")
doc_lines.append("> **Примечание:** Данный документ составлен исключительно на основе статического анализа APK (декомпиляция метаданных IL2CPP v27, ELF-библиотек и сериализованных ассетов Unity).\n")
doc_lines.append("## 1. Сетевая архитектура и транспорт\n")
doc_lines.append("- **Сетевой движок:** `EB.Sparx` (Kabam Sparx Platform) & `EB.Net` (Exploding Barrel Network).")
doc_lines.append("- **Транспортные протоколы:**")
doc_lines.append("  - **HTTPS / REST:** `EB.Net.WebRequest`, `UnityEngine.Networking.UnityWebRequest`.")
doc_lines.append("  - **WebSockets (WSS):** `EB.Sparx.NetworkWS` — постоянное соединение для нотификаций, чата, статусов матчей.")
doc_lines.append("  - **Reliable UDP (ENet):** `EB.Sparx.NetworkENet` через нативную библиотеку `libenetlib.so`.")
doc_lines.append("- **Формат сериализации:**")
doc_lines.append("  - Основной формат данных — **JSON** (`EB.JSON`, `AFMiniJSON.Json`, `EB.Sparx.JSONStatUserDict`). Запросы упаковываются как JSON-RPC / REST вызовы.")
doc_lines.append("- **CDN & Доставка ассетов:**")
doc_lines.append("  - Продакшн CDN endpoint (найден в `assets/bin/Data/e1917cd7a6bdb4492a247b8f758df2ae`): `https://tform-0901-hzlhiniyfcwf.tf-cdn.net`.")
doc_lines.append("  - MOTD CDN: `https://static.tf-cdn.net/motd/...`.")
doc_lines.append("  - Доставка ассетов: Play Asset Delivery (Google PAD) через `Google.Play.AssetDelivery.dll` и локальный каталог `assets/assetpack/`.\n")

doc_lines.append("## 2. Безопасность, Сертификаты и Античит\n")
doc_lines.append("- **Certificate Pinning:**")
doc_lines.append("  - В коде присутствует класс `AcceptAllCertificates` (используется для тестовых окружений или при определённых флагах сборки).")
doc_lines.append("  - `EB.Net.TcpClientSSL` и `BouncyCastle.dll` реализуют TLS/SSL валидацию. Хардкод публичных ключей серверов Kabam в IL2CPP метаданных представлен строками `CERTIFICATE`, `-----BEGIN CERTIFICATE-----`.")
doc_lines.append("- **Античит и защита целостности:**")
doc_lines.append("  - `libapkprotect.so`: Экспортирует функции `APK_Check_Start`, `APK_Check_Start_Salt`, `APK_Check_Step`, `APK_Check_Complete`. Проверяет хэш DEX и подпись APK при запуске.")
doc_lines.append("  - `libnms.so`: Компонент рекламного SDK ByteDance / Pangle (безопасность/валидация рекламы).")
doc_lines.append("  - `libkrash.so`: Google Breakpad native crash reporter (`Krash_Initialize`, `Krash_Log`).")
doc_lines.append("  - Классы `Security`: root-детекция и проверка отладчика встроены в вызовы `EB.Sparx.LoginManager` и `EB.Sparx.ServerAccessManager`.\n")

doc_lines.append("## 3. Все обнаруженные API эндпоинты (по сервисам)\n")

for svc, eps in sorted(by_service.items()):
    doc_lines.append(f"### Сервис `/{svc}` ({len(eps)} эндпоинтов)")
    doc_lines.append("| Эндпоинт | Назначение |")
    doc_lines.append("|---|---|")
    for ep in eps:
        desc = "RPC / API маршрут"
        if "login" in ep: desc = "Аутентификация / вход"
        elif "hero" in ep or "bcg" in ep: desc = "Данные ботов / ростера"
        elif "quest" in ep: desc = "Сюжетные и ивентовые квесты"
        elif "match" in ep: desc = "Матчмейкинг / PVP"
        elif "pvp" in ep: desc = "Арена и дуэли"
        elif "alliances" in ep: desc = "Управление альянсом"
        elif "wallet" in ep: desc = "Баланс валют (Energon, Gold, Ore)"
        elif "gacha" in ep: desc = "Открытие кристаллов"
        elif "tuning" in ep: desc = "Балансировочные таблицы и коэффициенты"
        elif "tutorial" in ep: desc = "Шаги и прогресс туториала"
        elif "objectives" in ep: desc = "Ежедневные / еженедельные цели"
        elif "store" in ep: desc = "Внутриигровой магазин"
        doc_lines.append(f"| `{ep}` | {desc} |")
    doc_lines.append("")

doc_lines.append("## 4. Ключевые серверные структуры данных (IL2CPP Схемы)\n")

for sname in key_structures:
    matches = [c for c in classes if c["full_name"] == sname or c["full_name"].endswith("." + sname)]
    if matches:
        c = matches[0]
        doc_lines.append(f"### Класс `{c['full_name']}`")
        doc_lines.append(f"- **Сборка:** `{c['image']}`")
        if c["fields"]:
            doc_lines.append("- **Поля:**")
            for f in c["fields"]:
                doc_lines.append(f"  - `{f}`")
        if c["methods"]:
            doc_lines.append(f"- **Ключевые методы ({len(c['methods'])}):** " + ", ".join([f"`{m}`" for m in c["methods"][:12]]))
        doc_lines.append("")

out_md = r".\report\network_endpoints.md"
with open(out_md, "w", encoding="utf-8") as f:
    f.write("\n".join(doc_lines))

print(f"Saved {out_md} successfully!")
