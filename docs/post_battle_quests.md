# Post-battle quests / economy (Step 8.1): plan and current state

Status: **blocked by the fight not resolving** (`FuseODRBlocker`). No
`/matches/resolve-match` request has ever been observed; rewards, energy and
progression after a fight are therefore not exercised.

## Expected flow (static, partially verified)

1. `FightResultsData` (TypeDef 8674) is built by the battle:
   `RemainingHP[]`, `HighestCombo`, `HitsReceived`, `SuccessfulHits`,
   `IsWin`, `IsQuit`, `IsTimeout`, `Stats` [STATIC].
2. `MatchManager.ResolveMatch<QuestsMatchResults, MatchStats>`
   (`0x11F2304`) sends `POST /matches/resolve-match/quests_fight` with
   `qid`, `enemyHealth`, `matchResults{battleId,result}`, `matchStats`
   [STATIC] (see `spec/match_protocol.md`).
3. The server response is an `IDictionary`; `QuestsManager.Async`
   (`0xD65038`) handles `match-resolved`, and the quest flow handles
   `battlecomplete` / `fightlost` / `questcomplete`
   (`0x2D6FEF8`, `0x2D72E20`, `0x2D78090`). Exact payload keys are unproven.
4. `QuestsManager.ProcessActionResultsAndProgression` (`0xD65EE8`) applies
   `progression`, `results` and `teamData`; the movedir handler already
   proves those keys for map actions.
5. `QuestResultsScreenModel` reads completion/mastery/potential rewards from
   the quest/active quest data; `quest_list.json` currently sends the same
   `gold 2000 + shards 100` placeholder for every mission.

## What is implemented now

- `/quests/quest-begin` returns `teamData` and persists `quest_run`.
- `/quests/quest-movedir` returns `progression` + `results` + `teamData`.
- `/matches/activate-match` returns the `[ASSUMED]`
  `match_activate_response.json`.
- `/matches/resolve-match` returns the `[ASSUMED]`
  `match_resolve_response.json`; without a resolve request it is dead code.
- No energy deduction, mastery, unlock or reward grant is applied.

## What to add once the fight resolves

- A real resolve response: progression update for the battle tile, quest
  completion, results list, `teamData`, and an `async` `battlecomplete` /
  `fightlost` message with the payload the client actually reads.
- Energy spend per tile (`energyPerTile`) and out-of-energy handling.
- First-completion / mastery rewards from `quest_list.json`.
- Unlock the next mission/chapter and persist it.
- Smoke on missions from different acts (1.1, 2.1, 3.1, 4.1) and after a
  kill/restart.

Do not invent the async payload before a capture; the current
`match_resolve_response.json` is explicitly `[ASSUMED]`.
