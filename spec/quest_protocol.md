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
 "results":[],"teamData":{...}}
```

Status: the request is observed, but the bot does not visibly move yet; the
client appears to stay in a pending-progression state. This is the next blocker.
[RUN]

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
