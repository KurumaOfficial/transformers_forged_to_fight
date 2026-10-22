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
