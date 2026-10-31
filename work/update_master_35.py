import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = r".\MASTER_PROMPT.md"
s = open(p, encoding="utf-8").read()
s = s.replace("# MASTER_PROMPT v3.4 -", "# MASTER_PROMPT v3.5 -", 1)
s += '''

## 17. v3.5 — activeTeams dict / prefight (2026-10-23)
- `BCGUserActiveTeamDict` is a dictionary keyed by activityID, not a list.
- `BCGUserActiveTeam..ctor` (`0xA610F0`) reads `aid`, `type`, `modes`,
  `expire`, `heroes`; `heroes` is a dictionary parsed into
  `TeamHeroes` (`List<BCGHeroDetails>`).
- `BCGHeroDetails` uses `blueprint`, `rank`, `level`, `sig_lvl`,
  `HPRating`, `HPMax`, `AttackRating`, `Attack`, `AttributeData`,
  `ForgeLevel`.
- Sending `activeTeams` dictionary + `heroes` dictionary with
  `blueprint/rank/level/hp/max_hp` removed "ALL KNOCKED OUT"; prefight
  still empty, plus/FIGHT gives `GetNewScale` NRE; no
  `/matches/activate-match`.
'''
open(p, "w", encoding="utf-8").write(s)
print("ok")
