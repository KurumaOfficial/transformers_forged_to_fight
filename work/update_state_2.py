import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = r".\STATE.md"
s = open(p, encoding="utf-8").read()
start = s.index("Battle tile static/runtime")
end = s.index("## 5. What is NOT verified")
new = '''Battle tile static/runtime (2026-10-23):
- Exact NRE: `MapTile.Deserialize` reads `entities` via `Dot.Object`
  (`0x1485094`); `0x1485098 cbz x0,#0x1486508` jumps to the common
  null-reference throw block. A JSON array is not an `IDictionary`, so
  `Dot.Object` returns null. `entities:{"enemy1":{...}}` fixed it.
- `MapTile` reads `builder.summary.bossTable` (`builder+0x28`,
  `summary+0x98`). `ActiveQuest..ctor` reads top-level `scaledBossTable`
  (`0xC39038/0xC39044`) and passes it to `Quests.Builder..ctor`
  (`0xC393E4`, `0xEF2D04`, field `+0x18`). The table must be in the
  top-level active-quest object, not in `data`/`map`.
- Entity factory is selected by **baseType**: `bcg|boss|tower` ->
  `BCGEntity`; `building` -> `Building`; `generator` -> `Generator`;
  otherwise generic `Entity` (`0xEF28CC`, `0x149B5D4`, `0x149B800`).
- `characters` is `Dot.StringList` (`0x1464E0C`) -> `List<string>`.
  `bumblebee_cin_dotm_2` is the accepted roster id; the asset pack is
  `bumblebee_cin_dotm` (`work/unpacked/assets/.../toc.txt`).
- Boss rendered on the map (6 stars, 8888). [RUN] work/r86.png,
  work/r95.png, work/r117.png.
- Asset scan: 3201 files, no real `scaledBossTable` sample; only metadata.
- Cheap experiment: added `currentFightId`, `currentBattleId`,
  `currentBattleBossId`, `currentBattlePos`, `localPlayer` to the movedir
  response. Client sent `/quests/quest-movedir/.../1/0`, but the bot stayed
  at (0,0), HUD 11%; `/matches/activate-match` was not called. Negative:
  progression-only is insufficient. [RUN] work/r119.png, 05:41:47Z.
- Memory after a normal move (without entity): `ActiveQuests=1`,
  `pendingProgressionCount=0`, `progression.version=2`, `currentPos=(1,0)`,
  `currentBattleId=null`. [RUN] work/adb_legacy_quest.py.

Next: a `battle` action with a full `battleEnemy`/`battleId` (or another
explicit trigger) must be tried; do not guess beyond one variant without
user approval. No Frida/gadget without consent.

'''
open(p, "w", encoding="utf-8").write(s[:start] + new + s[end:])
print("ok")
