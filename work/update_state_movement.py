import re
p = r".\STATE.md"
s = open(p, encoding="utf-8").read()
s = s.replace("Updated: 2026-10-22 18:50 UTC (local ~21:50 22.10.2026)",
              "Updated: 2026-10-22 19:05 UTC (local ~22:05 22.10.2026)")
start = s.index("## 4. Current blocker")
end = s.index("## 5. What is NOT verified")
new = '''## 4. Current blocker (next step)
Movement is **solved**: `/quests/quest-movedir` must return
`results:[{action:"moveto", moveto:{x,y}}]` plus `progression` and `teamData`.
The bot moved from (0,0) to (1,0); the HUD changed from 11% to 22% EXPLORED.
[RUN] `work/r75.png`, requests 18:55.

The next blocker is the **battle trigger**. A `battle` action with a minimal
`battleEnemy` did not call `/matches/activate-match`; no `/matches/*` request was
observed. `ActiveQuest.ActivateMatch` (`RVA 0x10A0038`) requires a `battleId` and
a hero and calls `MatchManager.ActivateMatch<QuestsMatchData>`. The normal trigger
is a battle tile/entity (`BCGEntity`) or `progression.currentBattleId`, not a
plain move. RAIDS is disabled by the client ("Raids are temporarily disabled."),
SPECIAL/ARENAS/ALLIANCE are level-locked. [RUN]

Next:
1. Build a valid battle action/entity: inspect `BCGEntity.Deserialize`
   (`RVA 0xC17FEC`) and `QuestBoss` keys; use a blueprint that exists in the
   catalog (e.g. Bumblebee) as the enemy.
2. Or set `progression.currentBattleId`/`currentFightId` + `localPlayer` so the
   map exposes a fight node.
3. Then capture `/matches/activate-match`, `/matches/match-loaded`,
   `/matches/resolve-match`.

'''
open(p, "w", encoding="utf-8").write(s[:start] + new + s[end:])
print("updated")
