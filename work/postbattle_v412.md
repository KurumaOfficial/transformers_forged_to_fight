
## 2026-10-31 v4.12 async schema and attempts

Static keys resolved from `QuestsManager.Async` (`0xD65038`) and
`ActiveQuest.AddActionResultsAndUpdateProgression` (`0xC3A278`):

- Async message `match-resolved` reads payload `qid`, `battleId`, then calls
  `ProcessActionResultsAndProgression(quest, payload)`.
- `ProcessActionResultsAndProgression` reads `teamData`; the active-quest
  update reads `results`, `progression`, `version`.
- `QuestProgression..ctor` reads `version`, `currentPos`, `cleared`,
  `previouslyCleared`.
- `QuestActionResult..ctor` reads the `action` wrapper and the action-type
  keys: `moveto`, `teleport`, `battle`, `ambush`, `battlecomplete`,
  `fightlost`, `questcomplete`, `chaptercomplete`, `actcomplete`.

Attempts with weak-enemy wins (`work/weak_enemy.flag`, test only):

1. `battlecomplete` with `x/y` + `cleared`/`visibleClearedCount`/
   `percentComplete` at action level; `progression.version=3`.
   Result: VICTORY, 22%, REWARDS empty.
2. Fields moved inside `battlecomplete`; top-level `battleId`/`version`
   added; async `match-resolved` payload sent.
   Result: VICTORY, 22%, REWARDS empty.
3. `completionRewards` object (`firstGold`, `firstItems`, `firstXP`,
   `masteryGold`, `masteryItems`, `masteryXP`, `potentialItems`) and
   `firstCompletionRewards` lists added both inside `battlecomplete` and at the
   action wrapper.
   Result: PERFECT/VICTORY, 22%, REWARDS still empty.

Evidence: `docs/evidence/post_battle_2026-10-31/` (request body and
screenshots). The resolve request/response loop and the victory screen work;
the reward/progression presentation still does not bind.

What is still open:

- The exact `QuestActionResult` construction of `firstCompletionRewards`
  (the ctor only calls `Dot.Object` for action types; the reward list is
  populated elsewhere, likely in `ActiveQuest`/`QuestFlow` from the quest
  summary).
- The active-quest refresh: `/quests/quest-active` still returns the static
  22% payload, so even an in-memory progression would be overwritten.
- Persistence: no SQLite write of `cleared`/`currentPos` yet.
