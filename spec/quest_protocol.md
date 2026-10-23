# Quests wire protocol — verified slice (v9.2.0)

Status: partial. Only the keys below are verified by decompilation and/or a live
client run. Values are not original Kabam data unless marked.

## 1. `GET /quests/quest-list`

`result` is a JSON **array** of quest sets.

### 1.1 Set object — keys read by `Legacy.QuestSet.AddQuestSummarys`

Source: `dump.cs` RVA `0x10381F0`; key strings resolved from
`global-metadata.dat` / `stringliteral.json`; live run 2026-10-21.

| Wire key | Type | Meaning | Evidence |
|---|---|---|---|
| `hash` | string | set content hash | [STATIC] |
| `setId` | string | set id, used by quest-detail | [STATIC]+[RUN] |
| `setName` | string | UI set name | [STATIC] |
| `expiry` | int (unix) | set expiry; 0 may mean expired | [STATIC] |
| `timeLimit` | int | seconds | [STATIC] |
| `timeLimitGrace` | int | seconds | [STATIC] |
| `showUI` | bool | **not** `showInUI` | [STATIC] |
| `group` | string | **not** `groupTag` | [STATIC] |
| `difficulty` | string | difficulty id | [STATIC] |
| `difficulty_color` | {r,g,b,a} | UI colour | [STATIC] |
| `difficulty_color_bg` | {r,g,b,a} | UI colour | [STATIC] |
| `difficulty_label` | string | localized label | [STATIC] |
| `minLevel` | int | unlock level | [STATIC] |
| `recommendMinLevel` | int | **not** `recommendedMinLevel` | [STATIC] |
| `cdn` | string | CDN prefix | [STATIC] |
| `use_ui_color` | bool | UI flag | [STATIC] |
| `ui_color` | {r,g,b,a} | UI colour | [STATIC] |
| `hasProgression` | bool | progression flag | [STATIC] |
| `tags` | string[] | tags | [STATIC] |
| `actCount` | int | number of acts | [STATIC]+[RUN] |
| `chapterCount` | int[] | **1-based**; index 0 is a dummy. `[0,1]` = Act 1 has 1 chapter | [STATIC]+[RUN] |
| `availableQuests` | object[] | summaries; see 1.2 | [STATIC]+[RUN] |
| `acts` | object[] | act presentation overlay; each has `act` index | [STATIC] |
| `chapters` | object[] | chapter presentation overlay; each has `act`, `chapter` | [STATIC] |

`chapterCount` crash evidence: with `[1]` the client threw
`ArgumentOutOfRangeException` in `Legacy.QuestSet.BuildSummaryTable` because it
indexes `chapterCount[actIndex]` for `actIndex == 1`. [RUN]

### 1.2 Summary object in `availableQuests`

The client builds `Act[actIndex].Chapters[chapterIndex].Quests[missionIndex]`
from these fields. The index keys are **`act`, `chapter`, `mission`**, not the
C# property names `actIndex`, `chapterIndex`, `missionIndex`.

| Wire key | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | quest id; used by quest-detail and progression |
| `category` | string | yes | e.g. `Story` |
| `act` | int ≥1 | yes | 1-based |
| `chapter` | int ≥1 | yes | 1-based |
| `mission` | int ≥1 | yes | 1-based |
| `unlocked` | bool | recommended | read by `QuestSummary.UpdateProgression` |
| `completed` | bool | recommended | |
| `mastered` | bool | recommended | |
| `cleared` | array | recommended | list of coordinates |
| `visibleClearedCount` | int | recommended | |
| `friendlyName`, `description`, `theme`, `todIndex`, `energyPerTile`, `minXpPerTile`, `maxXpPerTile`, `minHealthPerTile`, `maxHealthPerTile` | mixed | optional | presentation |
| `alwaysLocked`, `unlockTime`, `minLevel`, `minCL`, `useLockReason`, `lockReason` | mixed | optional | lock logic |
| `teamSizeMin`, `teamSizeMax` | int | optional | team limits |
| `firstCompletionRewards`, `masteryCompletionRewards`, `potentialCompletionRewards` | object[] | optional | redeemer items |
| `difficulty`, `recommendedPartyPI`, `recommendedMasteryPI`, `multiplier` | mixed | optional | UI |

Observed behavior after adding `act/chapter/mission`: the chapter card and quest
tile rendered; tapping the tile sent `POST /quests/quest-detail/{qid}`. [RUN]

### 1.3 Act / chapter overlay objects

`acts[]` item: `act` (int), `friendlyName`, `description`, `image`, `cdnImage`,
`fsImage1`, `fsImage2`, completion reward keys.

`chapters[]` item: `act` (int), `chapter` (int), `friendlyName`, `description`,
`image`, `cdnImage`, `fsImage1`, `fsImage2`, completion reward keys.

## 2. `POST /quests/quest-detail/{qid}`

Observed request body:

```json
{"hash": "v1", "nonce": "6ad929f66911bc4d665c000a", "api": 11, "setId": "story_act_1"}
```

`hash` and `setId` come from the quest-list set; `qid` is the summary `id`. [RUN]

Response shape currently used by the stub (not verified against Kabam):
`{"summary": {...}, "map": {...}}`. The client accepts it and renders the quest
screen. [RUN] The `map` must be a square `gridDimension × gridDimension` matrix
(`grid[y][x]`); a 3×1 row with `gridDimension: 3` crashes the active-quest map
with `ArgumentOutOfRangeException` in `EB.Missions.Map.Deserialize`. [RUN]

The roster must be present in `userData` (see `spec/bcg_userdata.md`), otherwise
START stays disabled.

## 2b. `POST /quests/quest-begin/{qid}`

Observed request:

```json
{"quitExisting":true,"nonce":"...","hash":"v1","api":11,
 "setId":"story_act_1","tm0":"bumblebee_cin_dotm_2"}
```

`tm0..tm3` are the selected team blueprint ids. [RUN]

The client callback (`QuestsManager.<>c__DisplayClass65_0.<BeginQuest>b__0`,
`RVA 0xCDD210`) reads:

```
result.activeQuests[qid].teamData
result.activeQuests
```

So the response must be:

```json
{"activeQuests": {
  "<qid>": {
    "qid": "<qid>", "category": "Story", "mode": "story",
    "team": ["bumblebee_cin_dotm_2"],
    "data": { ... }, "map": { ... },
    "progression": { ... },
    "teamData": {
      "userData": {"blueprintsMax":50,"teamSizeMax":3,"teamCountMax":3},
      "updates": {"heroes":[...],"activeTeams":[...],"savedTeams":[...],
                  "inventory":{"f":{},"bp":{},"max":{}}},
      "deletes": {}
    }
  }
}}
```

`teamData` is passed to `BCGManager.UpdateUserData` (`RVA 0xD65F38`). [RUN]

Map tiles must not contain invented `entities`: an unknown boss/entity id makes
`MapTile.Deserialize` throw `NullReferenceException`. Remove `entities` until a
real boss table id is available. [RUN]

## 2c. `POST /quests/quest-movedir/{qid}/{dx}/{dy}`

Observed request (from the start tile, direction right):

```json
{"api":11,"nonce":"..."}
```

The response is passed to `ActiveQuest.AddActionResultsAndUpdateProgression`
(`RVA 0xC3A278`), which reads `result.progression` and `result.results`, and to
`QuestsManager.UpdateActiveTeam(result.teamData)`. `QuestProgression..ctor`
(`RVA 0xCA5684`) reads `version`, `currentPos`, `cleared`, `previouslyCleared`,
`revealed`, `cfid`, `currentBattleId`, `currentBattlePos`, etc. [STATIC]

Current stub response:

```json
{"progression":{"version":2,"currentPos":{"x":1,"y":0},
  "cleared":[{"x":0,"y":0},{"x":1,"y":0}],"previouslyCleared":[],"revealed":[]},
 "results":[{"action":"moveto","moveto":{"x":1,"y":0}}],
 "teamData":{...}}
```

**Verified working.** The key is `results[].action = "moveto"` with a `moveto`
sub-object containing `x`/`y`. `actionType: 1` / `actionPos` / `actionTile` are
ignored. The bot moved from (0,0) to (1,0); HUD changed 11% -> 22% EXPLORED.
[RUN] `work/r75.png`, requests 18:55.

`QuestActionResult..ctor` (`RVA 0xEA28BC`) reads the `action` string and then the
sub-object with the same name (`moveto`, `teleport`, `battle`, ...). `moveto`
reads `x`/`y`; `isFinalBoss` and battle entities come from the same sub-object.
[STATIC]

### 2c.1 Battle trigger (not yet reached)

A `battle` action with a minimal `battleEnemy` did not call
`/matches/activate-match`. `ActiveQuest.ActivateMatch` (`RVA 0x10A0038`) requires
a `battleId` and a hero and calls `MatchManager.ActivateMatch<QuestsMatchData>`.
The normal trigger is a battle tile/entity (`BCGEntity.Deserialize`,
`RVA 0xC17FEC`) or `progression.currentBattleId`/`currentFightId` + `localPlayer`.
RAIDS is disabled by the client ("Raids are temporarily disabled."), SPECIAL/
ARENAS/ALLIANCE are level-locked. [RUN]

### 2c.2 Sparx `async` envelope

Async messages are `{component, message, payload, id, channel}`. `HttpEndPoint`
dispatches them via `PushManager.HandleMessage` (`RVA 0x12FE17C`) to the manager
named by `component`; `QuestsManager.Async` (`RVA 0xD65038`) handles
`avx-update`, `sync`, `match-activated`, `match-resolved`, `refresh`, etc.
For `avx-update` it calls `AvxQuestsSync.OnAsyncUpdate`. The HTTP `result` alone
is enough for `moveto`; `async` is not required for that step. [STATIC]+[RUN]

## 2d. `POST /quests/quest-quit/{qid}`

Observed when the red exit button is confirmed. The stub has no dedicated
route; the client returns to mode select. [RUN]

## 3. `GET /quests/quest-progression`

`result` is a dictionary keyed by **category** (`Story`), then by quest `id`.
Each value is passed to `QuestSummary.UpdateProgression`:
`unlocked`, `completed`, `mastered`, `cleared`, `visibleClearedCount`. [STATIC]
The current stub's values are [ASSUMED].

## 4. `GET /quests/quest-active`

Current stub returns `{"activeQuests": [], "instances": []}`. This is [ASSUMED];
no active quest has been verified.

## 5. Error reactions (observed)

| Condition | Client reaction |
|---|---|
| `chapterCount` too short | `ArgumentOutOfRangeException` in `BuildSummaryTable`, error dialog |
| summary missing `act/chapter/mission` | no chapter/quest tiles; no exception |
| quest-detail 200 but empty team | quest screen renders; START disabled |
| empty roster | `EDIT SQUAD` shows empty slots; BOTS screen NRE in `HeroesScreen.SetFeaturedHeroData` |
| `userData` flat (no wrapper) | roster stays empty, no exception |
| `entity_type: "hero"` | hero parsed but `GetHeroes` (`entities["bot"]`) returns none |
| non-square active map grid | `ArgumentOutOfRangeException` in `EB.Missions.Map.Deserialize` |
| invented map entity | `NullReferenceException` in `MapTile.Deserialize` |

## 6. Open questions

- Exact `quest-movedir` response fields that make the client commit the move
  (current stub returns `progression` + `teamData` but the bot stays at start).
- `match-activate`, `match-loaded`, `match-resolve` bodies and responses (not
  yet observed in a live run).
- Real quest ids, act/chapter names, maps and rewards (current content invented).

## 2e. Боевой тайл: статика и три варианта (2026-10-22)

### 2e.1 Как клиент понимает, что на тайле бой

`ActiveQuest..ctor` (`RVA 0xC38BC8`) читает из объекта активного квеста
`scaledBossTable` (ключ на `0xC38DE8`). Это словарь `bossTableId -> boss data`,
который передаётся в `Quests.Builder`.

`MapTile.Deserialize` (`RVA 0x1484C04`) для каждого элемента `entities`:
- читает `entityType` (`0x14857E8`);
- читает `boss` — это `bossTableId` (`0x14852A4`);
- ищет `bossTableId` в `scaledBossTable`;
- проверяет тип записи и создаёт `QuestBoss`/`BCGEntity`;
- читает `links` (`0x1485B2C`), `visibleLinks` (`0x1485B4C`), `bg`
  (`0x1485BC4`), `bt` (`0x1485C08`, список Vector2), `ab` (`0x1485C28`),
  `sockets` (ошибка `Error deserializing EB.Missions.Socket`).
- при ошибке пишет `Error deserializing EB.Missions.Entity (bossTableId = {0},
  type = {1})` и затем падает в `MapTile.Deserialize` (NRE). [STATIC]+[RUN]

`Entity.Deserialize` (`RVA 0x1334A04`) читает `uid`, `key`, `hi`.
`QuestBoss.Deserialize` (`RVA 0xEA3F60`) использует JSONPaths 8589:
`isFinalBoss`, `characters`, `rank`, `level`, `sig_lvl`, `flvl`, `aiType`,
`aiString`, `aiPer`, `mapOverride`, `todIndex`, `item01..03` + chances,
`mapBuffs`/`otherBuffs`, `synergyBonuses`, `userTitle`, `userRank`.
`BCGEntity.Deserialize` (`RVA 0xC17FEC`) вызывает `QuestBoss.Deserialize` и
кладёт `builder.quest` в `BCGEntity.quest` (`+0xE8`). [STATIC]

`QuestProgression.currentBattleId` (`+0x40`), `currentFightId` (`+0x38`),
`currentBattlePos` (`+0x50`) и `QuestActionResult` с `action:"battle"` — поля,
которые использует предбоевой экран/`ActivateMatch`. `ActiveQuest.ActivateMatch`
(`RVA 0x10A0038`) требует `battleId` и героя и вызывает
`MatchManager.ActivateMatch<QuestsMatchData>` → `/matches/activate-match`.
Обычный `moveto` его не вызывает. [STATIC]

### 2e.2 Проверка запуском: три варианта

Карта: 3×3, бот стартует (0,0), боевая сущность на (1,0).
`scaledBossTable.enemy1` + tile `entities:[{id,entityType:"boss",boss:"enemy1",
type:"boss"}]`.

| Вариант | Что добавлено | Результат |
|---|---|---|
| 1 | `scaledBossTable.enemy1` + tile entity; поля `characters`, `rank`, `level`, `sig_lvl`, `flvl`, `aiType`, `aiString`, `aiPer`, `mapOverride`, `todIndex` | `Error deserializing EB.Missions.Entity (bossTableId = enemy1, type = boss)`; затем NRE в `MapTile.Deserialize` |
| 2 | + `uid`, `key`, `hi`, `type`, `baseType` в запись босса | ошибка Entity исчезла, но NRE в `MapTile.Deserialize` остался |
| 3 | + `bg:false`, `bt:[]`, `ab:[]`, `sockets:{}` на всех тайлах | NRE в `MapTile.Deserialize` остался |

`/matches/*` не вызван ни в одном варианте. [RUN]

### 2e.3 Память после обычного хода (без entity)

После `quest-movedir` (ответ `action:"moveto"`):
`Legacy.QuestsManager.Instance` -> `QuestDB.ActiveQuests` содержит 1 запись
`story_act1_ch1_m1`; `pendingProgressionCount = 0`;
`progression.version = 2`; `currentPos = (1.0, 0.0)`;
`currentFightId = null`; `currentBattleId = null`; `currentBattlePos = (0,0)`.
Клиент принял ход, бой не создан. [RUN] `work/adb_legacy_quest.py`.

### 2e.4 Вывод

Боевой тайл требует не только `scaledBossTable`, но и корректной структуры
`entities`/`MapTile`; после трёх вариантов точное недостающее поле не найдено.
Дальше — динамическая трассировка `MapTile.Deserialize`/`QuestBoss.Deserialize`
или поиск реального `scaledBossTable`/tile entity в клиентских ассетах.

## 2f. Боевой тайл: точная причина NRE и полный разбор (2026-10-23)

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

## 2g. `battle` action и префайт (2026-10-23)

### 2g.1 `QuestActionResult..ctor` (RVA 0xEA28BC)

Конструктор читает `data["action"]` как `IDictionary` (`0xEA2BA4`).
Под-объекты перебираются в порядке и задают `Action.Type`:

| Ключ | Тип | Значение |
|---|---|---|
| `moveto` | MOVE_TO | 1 |
| `teleport` | TELEPORT | 2 |
| `battle` | BATTLE | 3 |
| `ambush` | AMBUSH | 4 |
| `battlecomplete` | BATTLE_COMPLETE | 5 |
| `fightlost` | FIGHT_LOST | 6 |
| `questcomplete` | QUEST_COMPLETE | 7 |
| `chaptercomplete` | CHAPTER_COMPLETE | 8 |
| `actcomplete` | ACT_COMPLETE | 9 |
| `barrierBlocked` | BARRIER_BLOCKED | 10 |
| `outOfEnergy` | OUT_OF_ENERGY | 11 |

`battle` (тип 3) читает:

- `x` — `Dot.Integer`, `y` — `Dot.Integer` (`0xEA2E44/0xEA2E68`);
- `isFinalBoss` — `Dot.Bool` (`0xEA2E90`);
- `battleEnemy` — `Dot.Object` (`0xEA2ED8`), обязательный `id` (`0xEA2F18`);
  далее `BCGEntity..ctor` (`0xC17F64`) + `Deserialize`;
- `battleTower` — необязательный `Dot.Object` (`0xEA30B0`);
- `actionTile = activeQuest.map.GetTile(x,y)` (`0x12EDA98`).

`BCGEntity` наследует `QuestBoss`; `battleEnemy` использует те же поля,
что `scaledBossTable` (`characters`, `rank`, `level`, `sig_lvl`,
`flvl`, `aiType`, `isFinalBoss`, ...). [STATIC]

### 2g.2 Проверка на живом клиенте

После `quest-movedir/1/0` сервер вернул:

```json
"results": [
  {"action": {"moveto": {"x": 1, "y": 0}}},
  {"action": {"battle": {
     "x": 1, "y": 0, "isFinalBoss": false,
     "battleEnemy": { "id": "enemy1", "characters": ["bumblebee_cin_dotm_2"], "...": "..." }
  }}}
]
```

Клиент **открыл префайт-экран** «SELECT YOUR BOT» — это главный
положительный результат: `battle`-действие является правильным
триггером. [RUN] `work/battle3.png`, `work/pre2.png`, `work/s5.png`.

Но локальная команда пустая:
- при нажатии «+»/FIGHT: `NullReferenceException` в
  `PrefightScreenPresentation.GetNewScale(HeroData robot)` из
  `TweenCharacterOut` (`work/battle6.png`, logcat 14:35:40Z/14:46:15Z);
- после добавления `team`-словаря и base-blueprint: сообщение
  «YOUR BOTS ARE ALL KNOCKED OUT» (`work/s5.png`).

Память `ActiveQuest.progression` после ответа:
`version=3`, `currentPos=(1,0)`, `currentBattleId="battle1"`,
`localPlayer` существует, `name="Commander"`, но `localPlayer.team`
имеет `List` count 0. То есть `team` всё ещё не разобран, хотя
`QuestUserInfo` читает его через `Dot.Object` (`0x103D5D8`) и создаёт
`QuestUserHero` (`0x103CC70`). Формат team остаётся нерешённым;
`/matches/activate-match` не вызван. [RUN] `work/read_prefight_state.py`.

### 2g.3 Вызовы `ActivateMatch`

`ActiveQuest.ActivateMatch` (`0x10A0038`) не имеет прямых `BL`:
поиск по коду дал 0 вызовов; метод-указатель встречается в данных
(`0x569620`, `0x2CE5140`), то есть вызов идёт через UI/делегат.
`ActivateMatch` требует `progression.localPlayer.battleId` (непустой)
и `hero`; иначе логирует `No battle id!` / `No hero!`. Префайт —
наблюдаемый путь к этому вызову, но кнопка FIGHT не дошла до него
из-за пустой команды. [STATIC]+[RUN]

## 2h. `team` и проверка «ALL KNOCKED OUT» (2026-10-23)

### 2h.1 `QuestUserInfo.team`

`QuestUserInfo` (`0x103CFF4`) читает `team` через `Dot.Object`
(`0x103D5D8`), то есть **JSON-словарь**, и создаёт внутренний
`List<QuestUserHero>` (`+0x68`). Не массив.

`QuestUserHero..ctor` (`0x103CC70`) получает:

- `x1` — **ключ словаря**, он же blueprint/ID героя (`+0x10`);
- `x2` — значение-словарь.

Ключи значения (`Dot`):

| Ключ | Поле | Тип |
|---|---|---|
| `hp` | `HP` `+0x18` | `float`, абсолютное HP |
| `pi` | `HeroRating` `+0x1C` | `int` |
| `sig_lvl` | `SigLvl` `+0x20` | `int` |
| `stat_mods` | `StatMods` `+0x28` | массив строк |
| `sig_mods` | `SigMods` `+0x30` | массив строк |

В `QuestUserHero` **нет** полей `level`, `rank`, `max_hp`; максимум HP
приходит из `TeamData`/`HeroData`. `hp` — абсолютное, не доля: проверка
ниже сравнивает его с `0.0`.

### 2h.2 «ALL KNOCKED OUT»

`PlayerMarker.TeamIsKnockedOut(List<QuestUserHero>)` — `RVA 0x1181DC8`:

```text
if list == null or list.Count < 1: return true
for each hero:
    if hero.HP > 0.0: return false
return true
```

Строка локализации: `ID_UI_PREFIGHT_ALL_BOTS_KNOCKED_OUT`
(`work/localization_all.json:7024`). Поэтому **count 0 = all knocked out**;
это объясняет противоречие: память показывала `team` count 0, а экран —
нокаут. [STATIC]

### 2h.3 Память после попытки 3

Снимок `work/read_prefight_state.py` после ответа с `team`-словарём:

```text
currentPos=(1,0)
currentBattleId="battle1"
localPlayer: name="Commander", strongestHero="bumblebee_cin_dotm"
localPlayer.team: List, count 0
```

То есть `currentBattleId` разобран, `localPlayer` создан, но `team`
остался пустым. Причина — не «нокаут» и не `currentBattleId`, а
непринятый формат/тип значения `team` (проверка типа значения в
`0x103D770`). Формат всё ещё не решён; `/matches/activate-match` не
вызван. [RUN]

### 2h.4 Обработчик FIGHT

- `PreFightScreen.OnFight` — `RVA 0xE397BC`.
- `PrefightScreenData.OnFight` — `RVA 0xE3E778` (реализация
  `IPrefightDataProvider.OnFight`, slot 33).
- `PrefightScreenData.GetCurrentTeam` (`0xE3D188`) и
  `TeamData.GetHP` (`0x10E1AE4`) — источник HP для префайта;
  `QuestUserHero` используется для маркера/нокаута, не для выбора
  отображаемой команды.

`ActiveQuest.ActivateMatch` (`0x10A0038`) прямых `BL` не имеет; вызов
идёт через UI/делегат. Условия: непустые `progression.localPlayer.
battleId` и `hero`; иначе `No battle id!` / `No hero!`. [STATIC]

### 2h.5 Заглушка `/matches/activate-match`

Первый вызов ещё не получен. `server/data/match_activate_response.json`
остаётся **`[ASSUMED]`**: `matchId`, `matchType`, `seed`, `fighterData.
enemyFighter` и вложенные `attributes`. Статически подтверждены только
`FighterData` (`Id`, `PlayerName`, `PlayerTag`, `IsBoss`,
`BaseAttributes`, `Attributes`, `Blueprint`, `SigLevel`, `AttackBonus`,
`AIProfile`, `OverrideAIPersonality`, `TeamData`) и
`BCGAttributeDataBase` (`HPMax`, `HPMaxBase`, `HP`, `Attack`,
`AttackBase`, `Armor`, `CritChance`, `CritDamage`, `PerfectBlockChance`,
`BlockProficiency`, `ManaGain`, `ManaStart`, `ResistMagic`,
`ResistPhysical`, `StunTime`, `StunChance`, `HeroRating*`). Точный
JSON-контракт ответа не подтверждён. [STATIC]+[ASSUMED]

### 2h.6 Статика `match-*` (перед первым вызовом)

- `QuestsMatchData` (`TypeDefIndex 12667`): `qid +0x10`, `battleId
  +0x18`, `hero +0x20`; `.ctor` `0xD6C27C`; `addToRequest`
  `0xD6C1C0`.
- `MatchManager.ActivateMatch<QuestsMatchData>` — `0x11F1FD0`
  (4-аргументная) / `0x11F1ED4` (3-аргументная); `MatchAPI.
  ActivateMatch` — `0x11F14F8/0x11F1680`, `ActivateMatchHandler`
  `0x11F1754`.
- `FighterData` (`TypeDefIndex 8671`): `Id`, `PlayerName`, `PlayerTag`,
  `IsBoss`, `BaseAttributes`, `Attributes`, `Blueprint`, `SigLevel`,
  `AttackBonus`, `AIProfile`, `OverrideAIPersonality`, `TeamData`.
- `BCGAttributeDataBase` (`TypeDefIndex 8303`): `StatMods`, `SigMods`,
  `BuffMods`, `SpecialAttackCount`, `HPMax`, `HPMaxBase`, `HP`,
  `Attack`, `AttackBase`, `Armor`, `CritChance`, `CritDamage`,
  `PerfectBlockChance`, `BlockProficiency`, `ManaGain`, `ManaStart`,
  `ResistMagic`, `ResistPhysical`, `StunTime`, `StunChance`,
  `HeroRating`, `HeroRatingHP`, `HeroRatingAttack`, `HeroRatingHPBase`,
  `HeroRatingAttackBase`.
- Точный JSON-контракт ответа `/matches/activate-match` не подтверждён:
  текущая заглушка в `server/data/match_activate_response.json` помечена
  `[ASSUMED]`. Ключи `matchId`, `matchType`, `seed`, `fighterData` не
  доказаны статикой. [STATIC]+[ASSUMED]

## 2i. `teamData.activeTeams`: словарь и `TeamHeroes` (2026-10-23)

`BCGUserData.activeTeams` имеет тип `BCGUserActiveTeamDict :
Dictionary<string, BCGUserActiveTeam>`. То есть JSON `activeTeams` — **словарь
по activityID**, не список.

`BCGUserActiveTeam..ctor(IDictionary)` — `RVA 0xA610F0`:

| Ключ | Поле | Тип |
|---|---|---|
| `aid` | `ActivityID` `+0x10` | string |
| `type` | `Type` `+0x18` | string |
| `modes` | `Modes` `+0x20` | List<string> |
| `expire` | `EstimatedExpire` `+0x30` | int |
| `heroes` | `TeamHeroes` `+0x28` | `Dot.Object` -> `BCGHeroDetailsList` |

`BCGHeroDetails` (`ctor 0xA5AA14`) / `BCGHeroDetailsBase`:

- `Blueprint +0x10`, `Rank +0x18`, `Level +0x1C`, `SigLevel +0x20`,
  `HPRating +0x24`, `HPMax +0x28`, `AttackRating +0x2C`,
  `Attack +0x30`, `Special +0x34`, `UserOwned +0x38`,
  `AttributeData +0x40`, `ForgeLevel +0x58`.

`TeamData.RefreshHeroData` (`0x10DE4D0`) берёт `mActiveTeam +0x28`
(`TeamHeroes`); если список пуст — команда пустая. `TeamData.GetHP`
(`0x10E1AE4`) читает `HeroData +0x40` -> `+0x34`.

### Проверка

Ответ теперь содержит:

```json
"activeTeams": {
  "story_act1_ch1_m1": {
    "aid": "story_act1_ch1_m1",
    "type": "story",
    "modes": ["Story"],
    "heroes": {
      "bumblebee_cin_dotm": {
        "blueprint": "bumblebee_cin_dotm",
        "rank": 1, "level": 1, "hp": 1000.0, "max_hp": 1000.0
      }
    }
  }
}
```

Префайт перестал писать «ALL KNOCKED OUT», но всё ещё показывает пустую
команду; «+»/FIGHT падает в `PrefightScreenPresentation.GetNewScale
(HeroData robot)`. `/matches/activate-match` не вызван. [RUN]
`work/teamfix4.png`, `work/teamfix6.png`.

Следующий подозреваемый — точный тип/поля элементов `heroes` для
`BCGHeroDetails` (не только `blueprint`, но и `hpMax`/`attack`/`attributeData`)
либо id, которым `PrefightScreenData.GetCurrentTeam` ищет active team.
