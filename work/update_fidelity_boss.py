p = r".\FIDELITY.md"
s = open(p, encoding="utf-8").read()
i = s.index("### DEV-015")
new = '''### DEV-015 — боевой тайл (2026-10-22)

`entities` в `MapTile.Deserialize` — **словарь**, не массив. С
`entities:{"enemy1":{...}}` + `scaledBossTable` квест-карта грузится, босс
рендерится (6★, 8888). [RUN] `work/r86.png`, `work/r95.png`.

Ход на тайл с боссом: `moveto` уходит, но бот остаётся на (0,0), HUD 11%;
`/matches/activate-match` не вызван. Нужен `battle`-action с battleId/enemy.
Бой по-прежнему **0% подтверждён**. [RUN] `work/r96.png`.
'''
open(p, "w", encoding="utf-8").write(s[:i] + new)
print("ok")
