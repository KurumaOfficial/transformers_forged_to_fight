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
