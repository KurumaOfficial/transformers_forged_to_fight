import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = r".\MASTER_PROMPT.md"
s = open(p, encoding="utf-8").read()
s = s.replace("# MASTER_PROMPT v3 -", "# MASTER_PROMPT v3.3 -", 1)
s += '''

## 15. v3.3 — battle action, prefight, wiki parse (2026-10-23)
- `QuestActionResult..ctor` (`0xEA28BC`) reads `data["action"]` as an
  IDictionary. `battle` fields: `x`, `y`, `isFinalBoss`, `battleEnemy`
  (`id` + BCGEntity/QuestBoss), optional `battleTower`; types 0..11 are
  in `spec/quest_protocol.md` §2g.
- Live: `battle` action opened the **prefight** screen. [RUN]
  `work/battle3.png`, `work/pre2.png`.
- Blocker: `localPlayer.team` is a `List` with count 0; «+»/FIGHT gives
  `PrefightScreenPresentation.GetNewScale(HeroData robot)` NRE. No
  `/matches/activate-match`.
- Wiki: 3613 Fandom pages enumerated; 817 non-File pages saved with full
  history+HTML, 2796 File descriptions saved, 523 images downloaded.
  44 bots + 252 pages parsed into `data/wiki/*.json` with [WIKI]/revid.
- Author OneDrive link is auth-gated; not downloaded.
'''
open(p, "w", encoding="utf-8").write(s)
print("ok")
