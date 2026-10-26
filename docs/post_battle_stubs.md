# Post-battle stubs (Step 7.1)

Status: **prepared as a schema, not exercised.** The fight is blocked by the
global `FuseODRBlocker`; no `battlecomplete`/`fightlost`/`resolve-match` has
been observed. Do not treat these payloads as retail data.

## Client-side result object

`FightResultsPopup.FightResultsData` (TypeDef 10209):

| field | offset | type |
|---|---:|---|
| IsWin | 0x10 | bool |
| IsTimeout | 0x11 | bool |
| SuccessfulHits | 0x14 | int |
| HitsReceived | 0x18 | int |
| HighestCombo | 0x1C | int |
| FightType | 0x20 | FightFlow.FIGHT_TYPE |
| PlayerBotName | 0x28 | string |
| OpponentBotName | 0x30 | string |
| BonusPoints | 0x38 | float |
| Rewards | 0x40 | List<RedeemerItem> |
| WithheldRewards | 0x48 | List<RedeemerItem> |
| ActiveQuest | 0x50 | ActiveQuest |
| QuestFightData | 0x58 | FightFlow.QuestFightData |

`FightResultData` (TypeDef 8674): `RemainingHP` float[], `HighestCombo`,
`HitsReceived`, `SuccessfulHits`, `IsWin`, `IsQuit`, `IsTimeout`, `Stats`.

## Async names found in string literals

`battlecomplete`, `fightlost`, `questcomplete`, `chaptercomplete`,
`actcomplete`, `outOfEnergy` (also `QuestComplete`/`QuestCompleted`).
These are Sparx async/quest-flow names, not necessarily HTTP paths. The
expected envelope is `async: [{component, message, payload}]`; no entry has
been observed on the wire yet.

## Proposed `[ASSUMED]` payloads

```
battlecomplete: {
  "matchId": "match_pve_1001", "isWin": true, "remainingHP": [0.0, 0.0],
  "successfulHits": 0, "hitsReceived": 0, "highestCombo": 0,
  "rewards": [], "withheldRewards": []
}
fightlost: { "matchId": "match_pve_1001", "isWin": false, "reason": "death" }
questcomplete: {
  "qid": "story_act1_ch4_m2", "completion": 1.0, "rewards": [],
  "nextQid": "story_act1_ch4_m3"
}
chaptercomplete: { "act": 1, "chapter": 4, "rewards": [] }
actcomplete: { "act": 1, "rewards": [] }
outOfEnergy: { "energy": 0, "energyMax": 100, "nextRegen": 60 }
```

Rewards are `[]`/`[ASSUMED]`; the wiki economy report
(`docs/economy_report.md`) shows why exact numbers are unavailable.

## Guard

If implemented later, put it behind `EXPERIMENT["post_battle_stubs"]`
(default false) and do not change `/matches/resolve-match` unless the flag is
explicitly enabled. The current server returns
`server/data/match_resolve_response.json` unchanged.
