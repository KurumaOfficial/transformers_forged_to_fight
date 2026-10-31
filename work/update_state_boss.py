p = r".\STATE.md"
s = open(p, encoding="utf-8").read()
start = s.index("Battle tile static/runtime")
end = s.index("## 5. What is NOT verified")
new = '''Battle tile static/runtime (2026-10-22):
- `MapTile.Deserialize` (`RVA 0x1484C04`) reads `entities` with `Dot.Object`
  (`0x1485094`) — it is an **IDictionary**, not an array. An array caused the
  NRE; `entities:{"enemy1":{...}}` fixed it.
- `scaledBossTable` is read by `ActiveQuest..ctor` (`0xC38BC8`, key `0xC38DE8`)
  from the active quest object (`activeQuests[qid].scaledBossTable`).
- `entityType:"boss"` + `characters:["bumblebee_cin_dotm_2"]` accepted; boss
  rendered on the map (6 stars, 8888). [RUN] work/r86.png, work/r95.png.
- Asset scan: 3201 files, no real `scaledBossTable` sample; only metadata.
- Moving onto the boss tile: `moveto` sent, bot stays at (0,0), HUD 11%;
  `/matches/*` not called. A `battle` action with battleId/enemy is likely
  required. [RUN] work/r96.png.
- Memory after a normal move (without entity): `ActiveQuests=1`,
  `pendingProgressionCount=0`, `progression.version=2`, `currentPos=(1,0)`,
  `currentBattleId=null`. [RUN] work/adb_legacy_quest.py.

Next: add a `battle` action for the boss tile with `battleId`/`battleEnemy`
(or set `progression.currentBattleId` + `localPlayer`) and capture
`/matches/activate-match`. No Frida/gadget without user consent.

'''
open(p, "w", encoding="utf-8").write(s[:start] + new + s[end:])
print("ok")
