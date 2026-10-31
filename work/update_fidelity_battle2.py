import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = r".\FIDELITY.md"
s = open(p, encoding="utf-8").read()
i = s.index("### DEV-015")
new = '''### DEV-015 — боевой тайл и префайт (2026-10-23)

Точная NRE-ветка: `entities` — словарь, а не массив
(`MapTile.Deserialize 0x1485094/0x1485098`). Босс рендерится (6★, 8888).
`battle`-действие (`QuestActionResult..ctor 0xEA28BC`) — правильный
триггер: после movedir клиент открыл префайт «SELECT YOUR BOT».
[RUn] `work/battle3.png`, `work/pre2.png`.

Локальная команда пустая: `localPlayer.team` — `List` count 0; «+»/FIGHT
даёт NRE в `PrefightScreenPresentation.GetNewScale(HeroData robot)`.
`/matches/activate-match` не вызван; бой **0% подтверждён**.
[RUN] `work/read_prefight_state.py`, logcat 14:35/14:46.
'''
new = new.replace("[RUn]", "[RUN]")
open(p, "w", encoding="utf-8").write(s[:i] + new)
print("ok")
