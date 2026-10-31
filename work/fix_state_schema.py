p = r".\STATE.md"
s = open(p, encoding="utf-8").read()
s = s.replace(
"""- `savedTeams` and `activeTeams` are **arrays**. Active team:
  `{aid,type,modes,expire,heroes:{bid:details}}`. Saved team:
  `{sid,heroes:[details]}`.""",
"""- `activeTeams` is a **dictionary keyed by `aid`** (`BCGUserActiveTeamDict`),
  not an array. Active team value:
  `{aid,type,modes,expire,heroes:{bid:details}}`; `heroes` is a dictionary
  parsed into `TeamHeroes` (`List<BCGHeroDetails>`).
  `savedTeams` schema remains less certain (`BCGUserSavedTeamDict` in the
  dump); do not assume an array."""
)
open(p, "w", encoding="utf-8").write(s)
print("ok")
