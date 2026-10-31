import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = r".\MASTER_PROMPT.md"
s = open(p, encoding="utf-8").read()
s = s.replace("# MASTER_PROMPT v3.3 -", "# MASTER_PROMPT v3.4 -", 1)
s += '''

## 16. v3.4 — team, prefight, wiki matrix (2026-10-23)
- `QuestUserInfo.team` is a JSON dictionary (`Dot.Object 0x103D5D8`);
  key = blueprint, value = `hp` (float, absolute), `pi`, `sig_lvl`,
  `stat_mods`, `sig_mods`. `QuestUserHero` has no level/rank/max_hp.
- `PlayerMarker.TeamIsKnockedOut` (`0x1181DC8`) returns true for count 0;
  hence "ALL KNOCKED OUT" with team count 0. Memory after attempt 3:
  `currentBattleId=battle1`, localPlayer exists, team count 0.
- `PreFightScreen.OnFight` (`0xE397BC`) -> `PrefightScreenData.OnFight`
  (`0xE3E778`); prefight HP comes from `TeamData.GetHP`.
- `battle` action opens prefight; `/matches/activate-match` still not
  called. Stub remains `[ASSUMED]`.
- Wiki: 3613 = 817 non-File + 2796 File; all non-File full history/HTML;
  all File descriptions; 694/2752 images; 44 bots + 252 pages parsed;
  matrix/ID map/version sets in `data/wiki/`.
'''
open(p, "w", encoding="utf-8").write(s)
print("ok")
