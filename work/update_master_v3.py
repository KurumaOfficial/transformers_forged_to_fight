p = r".\MASTER_PROMPT.md"
s = open(p, encoding="utf-8").read()
s = s.replace("# MASTER_PROMPT — Transformers: Forged to Fight offline revival",
              "# MASTER_PROMPT v3 — Transformers: Forged to Fight offline revival")
s = s.replace("Restored copy of the master prompt (2026-10-22). Canonical source: the user's\nmessage of that date. If this file and the user's prompt disagree, ask the user.",
              "Version 3, 2026-10-22. Restored/updated copy. Canonical source: the user's\nmessages; if this file and the user's prompt disagree, ask the user.")
start = s.index("## 6. Current blocker")
end = s.index("## 7. Rejected / do not repeat")
new6 = '''## 6. Current state (v3, 2026-10-22)
The roster blocker is **solved**. The client reaches BOTS, EDIT SQUAD, quest
detail, START, `quest-begin`, the quest map, and a confirmed move.

### 6.1 Nine roster/map wire gotchas (details: spec/wire_gotchas.md)
1. `/bcg/getLoginData.result.userData` is the wrapper
   `{userData:{...}, updates:{heroes,savedTeams,activeTeams,inventory}, deletes:{}}`.
2. Hero `entity_type` must be `"bot"` (`GetHeroes` reads `entities["bot"]`).
3. `savedTeams` / `activeTeams` are **arrays**; active team = `{aid,type,modes,expire,heroes:{bid:details}}`.
4. Catalog blueprints use key **`id`**, not `blueprint`; rank entries also use `id` + `rank`.
5. `featuredhero` must be in **`/account/data`**, not only `/auth/login`.
6. `/bcg/getBaseHeroData` returns a **JSON array** of `BCGHeroDetails`.
7. `/bcg/setSavedTeam` returns the full BCG catalog + userData wrapper.
8. `/quests/quest-begin/{qid}` returns `{activeQuests:{qid:{...,teamData}}}`.
9. Active map `grid` is square `gridDimension × gridDimension`; no invented entities.

### 6.2 Movement (solved)
`/quests/quest-movedir/{qid}/{dx}/{dy}` must return
`results:[{action:"moveto", moveto:{x,y}}]` plus `progression` (version,
currentPos, cleared, previouslyCleared, revealed) and `teamData`. The bot moved
from (0,0) to (1,0), HUD 11% -> 22% EXPLORED. [RUN] work/r75.png.

### 6.3 Current blocker: battle trigger
A `battle` action with a minimal `battleEnemy` did not call
`/matches/activate-match`; no `/matches/*` request was observed.
`ActiveQuest.ActivateMatch` (`RVA 0x10A0038`) requires `battleId` + hero and calls
`MatchManager.ActivateMatch<QuestsMatchData>`. The normal trigger is a battle
tile/entity (`BCGEntity`) or `progression.currentBattleId`, not a plain move.
RAIDS is disabled by the client ("Raids are temporarily disabled.");
SPECIAL/ARENAS/ALLIANCE are level-locked. [RUN]

Next: build a valid battle action/entity (`BCGEntity.Deserialize 0xC17FEC`,
`QuestBoss` keys) or set `currentBattleId`/`currentFightId` + `localPlayer`; then
capture `/matches/activate-match`, `/matches/match-loaded`,
`/matches/resolve-match`.

### 6.4 Fidelity table (honest)
| Subsystem | Wire/schema | Data/values | Evidence |
|---|---|---|---|
| APK, assets, UI, render | 100% original | 100% original | client unchanged except endpoint + signature |
| Sparx auth/envelope | confirmed [CLIENT]+[RUN] | account/token [ASSUMED] | boots to hub |
| BCG catalog | keys confirmed [CLIENT] | stats/ranks/ids [ASSUMED] | 13 gotchas |
| BCG userData/roster | confirmed [RUN] | hero/stats [ASSUMED] | BOTS + EDIT SQUAD |
| Quest list/detail | keys confirmed [RUN] | content [ASSUMED] | 1.1 Landing Site invented |
| quest-begin/map | confirmed [RUN] | map 3x3 [ASSUMED] | map loads |
| quest-movedir | confirmed [RUN] | progression [ASSUMED] | move works |
| Combat (`/matches/*`) | not observed | no data | 0% confirmed |
| Economy/shop/PvP/alliances | not started | no data | outside slice |

The client side is original. The **server schemas** for roster, quest begin and
movement are confirmed by run; the **numbers** remain synthetic. Combat is not
confirmed.

'''
s = s[:start] + new6 + s[end:]
s += '''

## 12. v3 changelog (2026-10-22)
- Roster solved: BOTS + EDIT SQUAD, 9 wire gotchas.
- Quest begin/map solved; movement solved with `action:"moveto"`.
- Current blocker: battle trigger (`/matches/activate-match`).
- Added `spec/wire_gotchas.md`, `report/stage2b_roster_and_quest_map.md`.
- Fidelity table updated (see 6.4).
'''
open(p, "w", encoding="utf-8").write(s)
print("MASTER_PROMPT v3 updated")
