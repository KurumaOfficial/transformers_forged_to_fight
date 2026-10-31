p = r".\MASTER_PROMPT.md"
s = open(p, encoding="utf-8").read()
s = s.replace("# MASTER_PROMPT v3 -", "# MASTER_PROMPT v3.2 -")
s += '''

## 14. v3.2 — боевой тайл и вики-архив (2026-10-22)
- `MapTile.Deserialize` reads `entities` via `Dot.Object` — it is a **dictionary**
  keyed by entity id, not an array. An array caused the NRE.
- `scaledBossTable` is read by `ActiveQuest..ctor` (`0xC38BC8`, key `0xC38DE8`)
  from `activeQuests[qid].scaledBossTable`.
- `entityType:"boss"` + `characters:["bumblebee_cin_dotm_2"]` accepted; boss
  rendered (6 stars, 8888). [RUN] `work/r86.png`, `work/r95.png`.
- Asset scan (3201 files): no real `scaledBossTable` sample; only metadata.
- `moveto` onto the boss tile is sent, but the bot stays at (0,0), 11%;
  `/matches/*` not called. Need a `battle` action with battleId/enemy.
- Wiki archive: see `archive/wiki/`, `COVERAGE_WIKI.md` and `OPEN_QUESTIONS.md`.
'''
open(p, "w", encoding="utf-8").write(s)
print("ok")
