import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = r".\STATE.md"
s = open(p, encoding="utf-8").read()
start = s.index("Battle tile static/runtime")
end = s.index("## 4b.")
new = '''Battle tile static/runtime (2026-10-23):
- Exact NRE: `MapTile.Deserialize` reads `entities` via `Dot.Object`
  (`0x1485094`); `0x1485098 cbz x0,#0x1486508` jumps to the common throw
  block. A JSON array is not an `IDictionary`; `entities:{"enemy1":{...}}`
  fixed it.
- `MapTile` reads `builder.summary.bossTable` (`+0x28`/`+0x98`);
  `ActiveQuest..ctor` reads top-level `scaledBossTable` and passes it to
  `Quests.Builder..ctor` (`+0x18`).
- Factory by `baseType`: `bcg|boss|tower` -> `BCGEntity`; `building` ->
  `Building`; `generator` -> `Generator`; else generic `Entity`.
- Boss rendered (6★, 8888). [RUN] r86/r95/r117.
- `battle` action is the right trigger (`QuestActionResult..ctor
  0xEA28BC`); it opened the prefight screen. [RUN] battle3/pre2.
- `QuestUserInfo.team` is a JSON dictionary (`Dot.Object 0x103D5D8`):
  key = blueprint; value `hp` (float absolute), `pi`, `sig_lvl`,
  `stat_mods`, `sig_mods`. No level/rank/max in `QuestUserHero`.
- `TeamIsKnockedOut` (`0x1181DC8`): empty list -> true; any `HP>0` ->
  false. Memory after attempt 3: `battleId=battle1`, localPlayer exists,
  team count 0. [RUN] work/read_prefight_state.py.
- `BCGUserActiveTeamDict` is a dictionary; `BCGUserActiveTeam..ctor`
  (`0xA610F0`) reads `aid/type/modes/expire/heroes`; `heroes` is a
  dictionary parsed into `TeamHeroes` (`List<BCGHeroDetails>`).
- Sending `activeTeams` dictionary + `heroes` dictionary with
  `blueprint/rank/level/hp/max_hp` removed «ALL KNOCKED OUT», but the
  prefight team is still empty; «+»/FIGHT gives
  `PrefightScreenPresentation.GetNewScale(HeroData robot)` NRE.
  `/matches/activate-match` not called. [RUN] teamfix4/teamfix6.

Next: exact `BCGHeroDetails` element fields/keys and the id used by
`PrefightScreenData.GetCurrentTeam` (`BCGHelper.GetActiveTeam`).
No Frida/gadget/patches without consent.

'''
s = s[:start] + new + s[end:]
open(p, "w", encoding="utf-8").write(s)
print("ok")
