import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = r".\spec\quest_protocol.md"
s = open(p, encoding="utf-8").read()
i = s.find("## 2f.")
new = r'''## 2f. Боевой тайл: точная причина NRE и полный разбор (2026-10-23)

### 2f.1 Точная инструкция NRE

`MapTile.Deserialize` (`RVA 0x1484C04`) читает `entities` через
`Dot.Object` (`0x1485094`), а не через `Dot.Array`. Это **IDictionary**.
Сразу после вызова стоит проверка:

```
0x1485094  bl   Dot::Object(IDictionary)
0x1485098  cbz  x0, #0x1486508      ; null -> общий блок throw
...
0x1486508  bl   0x9bb514            ; throw helper (NullReferenceException)
```

Если `entities` — JSON-массив, `Dot.Object` возвращает null, ветка
`0x1485098` уходит в `0x1486508`, и падает NRE. Это и было точное
разыменование; оно происходит **до** разбора `entityType`, поэтому
добавление полей в сущность не помогало. [STATIC]+[RUN]

Словарь `entities:{"enemy1":{...}}` проходит, `quest-begin` не падает,
босс рендерится (6★, 8888). [RUN] `work/r86.png`, `work/r95.png`,
`work/r117.png`.

### 2f.2 Что происходит после `entityType`

Цикл по `entities` (`0x1485100` GetEnumerator, `0x14851E8` current):

| Адрес | Действие | Возможный null |
|---|---|---|
| `0x14851E8` | `cbz x0, #0x1486524` — текущее значение словаря | null -> throw |
| `0x148521C` | `x23 = [entry+8]` — данные сущности | — |
| `0x148522C` | `x24 = key` — id сущности | — |
| `0x14852A4` | `Dot.String(entityType, default "boss")` | default `"boss"` |
| `0x14852D4` | `Dot.String(parentEntityType, default entityType)` | default |
| `0x14852D8` | `cbz x21, #0x148652C` — builder | null -> throw |
| `0x14852DC` | `[builder+0x28]` = `summary` | null -> `0x1486530` |
| `0x14852E8` | `[summary+0x98]` = `bossTable` | null -> `0x1486534` |
| `0x1485304` | `TryGetValue(entityId, out boss)` | false -> fallback |
| `0x1485310` | `cbz out boss` | null -> `0x1486570` |
| `0x1485314` | `[boss+0x20]` = `boss.type` | `op_Inequality` допускает null |
| `0x1485320` | сравнение `boss.type != entityType` | несовпадение -> LogError и skip |
| `0x1485414` | виртуальный вызов у `boss` с позицией | — |

Точные адреса null-проверок: `0x148652C` (builder), `0x1486530`
(summary), `0x1486534` (bossTable). Все они ведут в общий throw-блок
`0x1486508`. [STATIC]

Если `TryGetValue` не нашёл id, вызывается фабрика:
`0x14853D8` -> `builder.NewEntity(baseType=x27, entityType=x23, position)`.
Ветка `generator` — `0x1485418`. [STATIC]

### 2f.3 Откуда `MapTile` берёт таблицу

`MapTile.Deserialize` **не получает таблицу параметром**. Она читается из
`builder.summary.bossTable`:

- `EB.Missions.Builder` (`TypeDefIndex 6430`): `scaledBossTable +0x18`,
  `summary +0x28`;
- `Summary` (`TypeDefIndex 6443`): `bossTable +0x98`;
- `Quests.Builder` (`TypeDefIndex 12716`): `scaledBossTable` наследуется
  от `EB.Missions.Builder`, `quest +0x50`.

Цепочка `quest-begin`:

1. `ActiveQuest..ctor` (`RVA 0xC38BC8`) читает `scaledBossTable` из
   **верхнего уровня объекта активного квеста**: `Dot.Object` на
   `0xC39044`, ключ `scaledBossTable` (`0xC39038`), результат временно
   лежит в `[sp+0x10]`.
2. На `0xC393E4` он передаётся третьим аргументом в
   `Quests.Builder..ctor` (`RVA 0xEF2D04`), который кладёт его в
   `EB.Missions.Builder.scaledBossTable` (`+0x18`).
3. `MapTile.Deserialize` на `0x14852DC` читает `builder.summary` (`+0x28`),
   затем `summary.bossTable` (`+0x98`) и делает `TryGetValue` по id
   сущности (`0x1485304`).

Следовательно, `scaledBossTable` должен лежать **в верхнем уровне
объекта `activeQuests[qid]`**, не в `data` и не в `map`. Наша рабочая
структура:

```json
"activeQuests": {
  "story_act1_ch1_m1": {
    "scaledBossTable": {"enemy1": {"...": "..."}},
    "data": {"...": "..."},
    "map": {"grid": [[...]]}
  }
}
```

Если таблица null, `MapTile` падает на `0x1486530/0x1486534`; если в
`entities` массив — раньше, на `0x1485098`. [STATIC]+[RUN]

### 2f.4 `entityType`, `baseType` и фабрика

`MapTile` передаёт в фабрику два разных значения:

- `entityType` — ключ `entityType`, default `"boss"`;
- `baseType` — ключ `parentEntityType`, default = `entityType`.

`Quests.Builder.NewEntity` (`RVA 0xEF28CC`) выбирает класс по **baseType**
(первый аргумент), а `entityType` передаёт в конструктор:

| baseType | Класс | Адрес |
|---|---|---|
| `bcg` | `BCGEntity` | `0xEF29BC` |
| `boss` | `BCGEntity` | `0xEF29BC` |
| `tower` | `BCGEntity` | `0xEF29BC` |
| `building` | `Building` (если есть у owner) | `0x149B5D4` |
| `generator` | `Generator` | `0x149B800` |
| любой другой | базовый `Entity` | `0x133490C` |

Это и есть реестр «строка -> класс». Для боевого тайла мы использовали
`baseType:"boss"`, `entityType:"boss"` — создан `BCGEntity`. [STATIC]+[RUN]

Небоевую сущность отдельным запуском не проверяли; статически
`baseType:"generator"` даёт `Generator`, `baseType:"building"` — `Building`,
иначе generic `Entity`. [STATIC]

### 2f.5 `characters` в `QuestBoss.Deserialize`

`QuestBoss.Deserialize` (`RVA 0xEA3F60`) читает `characters` через
`Dot.StringList` (`0x1464E0C`) в поле `potentialCharacters` (`+0x58`,
`List<string>`). Тип элементов — **строки**, не объекты. [STATIC]

Мы передали `"characters":["bumblebee_cin_dotm_2"]`; клиент принял
сущность и отрисовал босса. Идентификатор ростера `bumblebee_cin_dotm_2`
принят клиентом; базовый бандл в ассетах —
`work/unpacked/assets/bumblebee_cin_dotm_odr/toc.txt`
(`bumblebee_cin_dotm.assetbundle`), без суффикса `_2`. [RUN]+[CLIENT]

### 2f.6 Поиск образца в ассетах

Просканировано 3201 файл `work/unpacked/assets` на `scaledBossTable`,
`bossTableId`, `isFinalBoss`, `entityType`, `aiType`. Совпадения только в
`global-metadata.dat` (имена строк); реального JSON-образца
`scaledBossTable`/`entityType` нет. [STATIC]

### 2f.7 Дешёвый опыт `currentBattleId + localPlayer`

В ответ `quest-movedir/1/0` добавлены `currentFightId`, `currentBattleId`,
`currentBattleBossId`, `currentBattlePos`, `currentBattleEnemyHealth` и
`localPlayer` (с `team`). Клиент отправил movedir, но:

- бот остался на (0,0), HUD 11%;
- `/matches/activate-match` не вызван;
- других `/matches/*` нет.

Опыт **отрицательный**: одной `progression.currentBattleId + localPlayer`
недостаточно. Нужен `battle`-action/иной триггер, который вызовет
`ActiveQuest.ActivateMatch(hero)`. [RUN] `work/r119.png`, лог
`server/requests.jsonl` (05:41:47Z).

`ActiveQuest.ActivateMatch` (`RVA 0x10A0038`) статически требует
непустые `battleId` (из `progression.currentBattleId` / `Player.battleId`)
и `hero`; иначе логирует `No battle id!` / `No hero!`. [STATIC]
'''
open(p, "w", encoding="utf-8").write(s[:i] + new)
print("ok")
