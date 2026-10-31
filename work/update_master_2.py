import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = r".\MASTER_PROMPT.md"
s = open(p, encoding="utf-8").read()
i = s.index("## 14.")
new = '''## 14. v3.2 — боевой тайл и вики-архив (2026-10-23)
- Exact NRE: `MapTile.Deserialize` reads `entities` via `Dot.Object`
  (`0x1485094`); `0x1485098 cbz x0,#0x1486508` is the null-reference throw.
  `entities` is an `IDictionary` keyed by entity id, not an array.
- `MapTile` reads `builder.summary.bossTable` (`builder+0x28`,
  `summary+0x98`). `ActiveQuest..ctor` reads top-level `scaledBossTable`
  (`0xC39038/0xC39044`) and passes it to `Quests.Builder..ctor`
  (`0xC393E4`, `0xEF2D04`, field `+0x18`).
- Factory by `baseType`: `bcg|boss|tower` -> `BCGEntity`; `building` ->
  `Building`; `generator` -> `Generator`; otherwise generic `Entity`
  (`0xEF28CC`). `characters` is `Dot.StringList` -> `List<string>`.
- Boss rendered (6 stars, 8888). [RUN] `work/r86.png`, `work/r95.png`,
  `work/r117.png`. Asset scan (3201 files): no real sample, metadata only.
- Cheap experiment with `currentBattleId + localPlayer` in `progression`:
  negative; movedir was sent, bot stayed at 11%, `/matches/activate-match`
  was not called. [RUN] `work/r119.png`, 05:41:47Z.
- Wiki archive: Fandom content/HTML/full history partially saved (state for
  continuation), TFWiki FTF pages saved, author collection link recorded in
  `OPEN_QUESTIONS.md`. See `COVERAGE_WIKI.md`.
'''
open(p, "w", encoding="utf-8").write(s[:i] + new)
print("ok")
