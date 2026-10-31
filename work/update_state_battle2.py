import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = r".\STATE.md"
s = open(p, encoding="utf-8").read()
start = s.index("Battle tile static/runtime")
end = s.index("## 4b.")
new = '''Battle tile static/runtime (2026-10-23):
- Exact NRE: `MapTile.Deserialize` reads `entities` via `Dot.Object`
  (`0x1485094`); `0x1485098 cbz x0,#0x1486508` jumps to the common
  null-reference throw block. A JSON array is not an `IDictionary`;
  `entities:{"enemy1":{...}}` fixed it.
- `MapTile` reads `builder.summary.bossTable` (`builder+0x28`,
  `summary+0x98`). `ActiveQuest..ctor` reads top-level `scaledBossTable`
  (`0xC39038/0xC39044`) and passes it to `Quests.Builder..ctor`
  (`0xC393E4`, `0xEF2D04`, field `+0x18`).
- Factory by `baseType`: `bcg|boss|tower` -> `BCGEntity`; `building` ->
  `Building`; `generator` -> `Generator`; else generic `Entity`.
  `characters` is `Dot.StringList` -> `List<string>`.
- Boss rendered (6★, 8888). [RUN] r86/r95/r117.
- **`battle` action is the right trigger.** `QuestActionResult..ctor`
  (`0xEA28BC`) reads `data["action"]` as IDictionary; `battle` fields:
  `x`, `y`, `isFinalBoss`, `battleEnemy` (id + BCGEntity/QuestBoss
  fields), optional `battleTower`. Action types 0..11 documented in
  `spec/quest_protocol.md` §2g.
- Live: after `quest-movedir/1/0`, the client opened the **prefight
  screen** “SELECT YOUR BOT” from the battle action. [RUN] battle3/pre2/s5.
- But local `team` is empty: `localPlayer.team` is a `List` with count 0
  in memory, even after sending `team` as a dictionary. Tapping “+”/FIGHT
  crashes in `PrefightScreenPresentation.GetNewScale(HeroData robot)` ->
  `NullReferenceException`; after base-blueprint change the screen says
  “YOUR BOTS ARE ALL KNOCKED OUT”. `/matches/activate-match` still not
  called. [RUN] work/read_prefight_state.py, logcat 14:35/14:46.
- `ActiveQuest.ActivateMatch` (`0x10A0038`) has no direct BL (0 hits);
  called via UI/delegate. It requires non-empty `progression.localPlayer.
  battleId` and `hero` (`No battle id!`/`No hero!`).
- Memory after response: version 3, currentPos (1,0), currentBattleId
  `battle1`, `localPlayer` exists, `localPlayer.team` count 0.
- Asset/portrait: `bumblebee_cin_dotm_2` accepted by roster; base asset
  pack is `bumblebee_cin_dotm`; prefight still loads `portrait_unknown.png`.

Next: fix the `team`/`QuestUserHero` container (dictionary shape and
required `hp`/`pi`/`sig_lvl`/`mods`), then press FIGHT and capture
`/matches/activate-match`. Do not use Frida/gadget/patches without consent.

'''
open(p, "w", encoding="utf-8").write(s[:start] + new + s[end:])
print("ok")
