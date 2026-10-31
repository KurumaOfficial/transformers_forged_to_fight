# Post-battle flow: static schema and observed victory screen (Step 2)

Status: **partial.** The resolve response now produces the real **VICTORY**
screen with battle stats, but rewards, tile clear and map progress are not
applied yet. No client patch.

## Static flow

```text
BattleArbiter / FightResultsData
  -> MatchManager.ResolveMatch<QuestsMatchResults, MatchStats> (0x11F19F4)
  -> POST /matches/resolve-match/quests_fight
       {qid, enemyHealth, matchResults:{battleId,result}, game_stats}
  -> QuestsManager.Async (0xD65038) / ProcessActionResultsAndProgression
       (0xD65EE8) consumes qid, progression, results, teamData
  -> QuestResultsScreenModel reads completion/mastery rewards
  -> map refresh (quest-active / quest-progression)
```

Relevant classes:

| class | fields / role |
|---|---|
| `QuestActionResult` (TypeDef 12581) | `qid`, `actionType`, `actionPos`, `actionTile`, `isFinalBoss`, `battleEnemy`, `battleTower`, `eventPoints`, `redeems`, `spends`, `withHeldItemRedeems`, `cleared`, `visibleClearedCount`, `walkableCount`, `visibleWalkableCount`, `percentHealthGained` |
| `Action.Type` (TypeDef 12685) | NONE, MOVE_TO, TELEPORT, BATTLE, AMBUSH, **BATTLE_COMPLETE**, FIGHT_LOST, QUEST_COMPLETE, CHAPTER_COMPLETE, ACT_COMPLETE, BARRIER_BLOCKED, OUT_OF_ENERGY |
| `Action..ctor` | parses the action dictionary; the movedir payload `{"action":{"moveto":{x,y}}}` is the working reference |
| `QuestsManager.ProcessActionResultsAndProgression` | applies `qid`, `progression`, `results`, `teamData` |
| `QuestResultsScreen` | reads `IQuestResultsDataProvider`; rewards list |

## What was tried `[RUN]`

With the test-only `weak_enemy.flag` (enemy HP 1), a normal quest fight was
won and `/matches/resolve-match/quests_fight` returned:

```json
{
  "victory": true,
  "enemyHealth": 0,
  "results": [
    {"action": {
      "battlecomplete": {"x": 1, "y": 0},
      "cleared": [{"x":0,"y":0},{"x":1,"y":0}],
      "visibleClearedCount": 2,
      "percentComplete": 30,
      "redeems": [{"type":"currency","data":"gold","quantity":2000}]
    }}
  ],
  "progression": {
    "currentPos": {"x":1,"y":0},
    "cleared": [{"x":0,"y":0},{"x":1,"y":0}],
    "percentComplete": 30
  },
  "teamData": {"...": "..."}
}
```

Observed:

- **VICTORY** screen appears with REWARDS, STATS (successful hits, hits
  received, highest chain) and `MISSION 2 22% EXPLORED`;
- `TAP ANYWHERE` returns to the map;
- map still shows **22%** and the player at the start tile;
- REWARDS is empty;
- the fight itself, K.O./win, resolve-match and return-to-map work.

Previously the same win returned `results: []` and no victory screen.

## Why it is still incomplete

- `battlecomplete` is recognized enough to show the screen, but the
  `cleared`/`percentComplete` fields are not applied to the active quest.
  The action may need the fields at a different level, or the client applies
  them through a later `quest-active`/`quest-progression` refresh (which still
  returns the static 22% data).
- Rewards are not shown with either `{type,data,quantity}` or
  `{id,type,amount}` in `rewards`/`redeems`. `QuestResultsScreenModel` likely
  reads RedeemerItem objects from the **active quest** data, not the action.
- `isFinalBoss`/`questcomplete` was only sent when the quest had that flag;
  normal missions need a tile-clear action, not a quest-complete action.

## Next static work

1. Disassemble `QuestActionResult..ctor` (`0xEA28BC`) around the key reads and
   the `Action.Type` dispatch; map the exact JSON keys for `cleared`,
   `percentComplete` and `redeems`.
2. Disassemble `QuestResultsScreenModel` and find the rewards source.
3. Cache the post-battle active quest and return it from
   `/quests/quest-active` / `/quests/quest-progression` after resolve.
4. Persist `cleared`/`currentPos` in SQLite (`TFTF_DB`) and verify with a
   restart.

Evidence: `work/postwin2.png` (victory screen), `work/postwin3.png` (map
22%), `work/postwin6.png` (rewards still empty).

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

## 2026-10-31 v4.13 Step 3 state attempt

server/stub_server.py now has pply_win_progress behind
work/persist_progress.flag: on a win it writes
quest_progression.json (cleared tiles, currentPos, percentComplete) and
quest_active.json (one active quest with the updated position).

[RUN] With the flag and a weak-enemy win, the files did update:

- Story.story_act1_ch4_m2.cleared = [{0,0},{1,0}]
- currentPos = {1,0}, percentComplete = 33
- quest_active.activeQuests[0].currentPosition = {1,0}

After TAP ANYWHERE, the map still showed **22% EXPLORED** and the old tile
state (docs/screens_ok/persist_map_22pct.jpg). So the server state alone is
not enough: the client does not refetch/apply this file on return, or the
attlecomplete action/progression is still not parsed. The flag is off by
default; no behavior change in the normal stub.

Next: find the post-return request sequence (
equests.jsonl) and the exact
quest-detail/quest-active read; then make the action/progression apply in
the same payload the client already consumes.
