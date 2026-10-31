import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = r".\FIDELITY.md"
s = open(p, encoding="utf-8").read()
i = s.index("### DEV-015")
new = '''### DEV-015 — боевой тайл (2026-10-23)

Точная NRE-ветка: `MapTile.Deserialize` читает `entities` через
`Dot.Object` (`0x1485094`); `0x1485098 cbz x0,#0x1486508` — общий throw.
Массив не является `IDictionary`; словарь `entities:{"enemy1":{...}}`
проходит. [STATIC]+[RUN]

`MapTile` берёт таблицу из `builder.summary.bossTable` (`builder+0x28`,
`summary+0x98`); верхнеуровневый `scaledBossTable` передаётся в
`Quests.Builder..ctor` (`0xC393E4`, `0xEF2D04`, `+0x18`). `baseType`
`bcg|boss|tower` -> `BCGEntity`; `characters` — `List<string>`.
Босс рендерится (6★, 8888). [RUN] `work/r86.png`, `work/r95.png`,
`work/r117.png`.

Ход на тайл с боссом: movedir уходит, бот остаётся на (0,0), HUD 11%.
Дешёвый опыт с `currentBattleId + localPlayer` в `progression` —
**отрицательный**, `/matches/activate-match` не вызван. [RUN]
`work/r119.png`, 05:41:47Z. Бой по-прежнему **0% подтверждён**.
'''
open(p, "w", encoding="utf-8").write(s[:i] + new)
print("ok")
