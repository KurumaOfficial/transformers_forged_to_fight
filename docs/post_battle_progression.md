# Post-battle actions and progression (Q4/Q5, static)

Status: **blocked by the battle-init NRE**. The client reaches
`/matches/activate-match` but does not reach match-loaded/resolve, so no
post-battle response has been observed. Everything below is `[STATIC]` from
`dump.cs` and the localization metadata.

## Client constants

- `Questboard.ACTION_FIGHT_LOST = "fightlost"`.
- Result/action keys in localization: `battlecomplete`, `fightlost`,
  `questcomplete`, `chaptercomplete`, `actcomplete`, `outOfEnergy`.
- `Gameboard.Action_OutOfEnergy` (`0x...`) wraps an action after a move when the
  quest energy is exhausted.
- `Gameboard.Action_QuestComplete` plays the quest-complete FX and then calls
  the quest completion callback.
- `QuestResultsScreen` consumes `IQuestResultsDataProvider` (entry 70) and
  `IQuestResultsCallbacks`.
- `MatchManager.ResolveMatch<QuestsMatchResults, MatchStats>` sends the match
  result; `QuestsManager.Async` handles `match-resolved`.

## Expected server flow (from `spec/match_protocol.md`)

1. `POST /matches/match-loaded/{type}/{id}` after the arena is ready.
2. `POST /matches/resolve-match/{type}` with quest result, enemy health,
   winners/losers and stats.
3. Async `{component:"quests", message:"match-resolved", payload:...}`.
4. Quest progression update: `currentFightId`, `currentBattleId`,
   `currentBattleState`, `currentBattlePos`, `currentBattleEnemyHealth`,
   `cleared`, `revealed`, `percentComplete`.
5. Reward grant (gold/shards/XP) and `quest-progression`/`quest-active`
   refresh.

## Stub readiness

- `server/data/match_resolve_response.json` exists but is `[ASSUMED]`.
- `quest_progression.json` supports the shape but is not updated by a real
  fight.
- The SQLite schema has `match`, `reward_ledger` and `quest_run` tables ready
  for the resolve step.

## What must be captured next

Real bodies for `match-loaded`, `resolve-match`, the async envelope and the
post-battle progression delta. Until then Q4/Q5 remain documented, not
implemented.
