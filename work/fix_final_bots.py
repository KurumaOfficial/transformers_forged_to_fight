from pathlib import Path

p = Path("report/FINAL_2026-10-30.md")
s = p.read_text(encoding="utf-8")
s = s.replace(
    "6. **BOTS 59/59** — метрика неверна; нужен вертикальный скролл и rerun.",
    "6. **BOTS detail** — 57/59 info opens; 2 info errors on page 0; Starscream not shown.",
)
s = s.replace(
    "2. Вертикальный BOTS sweep + Starscream UI/бой.",
    "2. Starscream UI/бой и 2 info-ошибки BOTS.",
)
p.write_text(s, encoding="utf-8")
print("ok")
