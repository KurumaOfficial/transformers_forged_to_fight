from pathlib import Path

p = Path("report/FINAL_2026-10-30.md")
s = p.read_text(encoding="utf-8")
s = s.replace(
    "| BOTS sweep | **57/59 info opens, 0 NRE** | vertical rerun; Starscream not shown |",
    "| BOTS sweep | **59/59 info opens, 0 NRE** | vertical rerun; Starscream not shown |",
)
s = s.replace(
    "6. **BOTS detail** — 57/59 info opens; 2 info errors on page 0; Starscream not shown.",
    "6. **Starscream UI** — catalog entry exists, but the BOTS grid does not show it.",
)
s = s.replace(
    "2. Starscream UI/бой и 2 info-ошибки BOTS.",
    "2. Starscream UI/бой.",
)
p.write_text(s, encoding="utf-8")
print("ok")
