from pathlib import Path

p = Path("report/FINAL_2026-10-31.md")
s = p.read_text(encoding="utf-8")
s = s.replace(
    "- `[RUN]` Нормальный battle step COMPLETED/LOST; `[RUN]` 6/6 full smoke\n"
    "  (v4.11 baseline); `check_all`/unit — в финальном ночном прогоне.",
    "- `[RUN]` Нормальный battle step COMPLETED/LOST (урон 271.6/1248, HP падает).\n"
    "- `[RUN]` `check_all` PASS 9/9, unit 32/32, full smoke 6/6 после v4.12-изменений.\n"
    "  Полный nightly с BOTS sweep не перегонялся: метрика 59 карточек не является\n"
    "  ID-покрытием (см. `docs/bots_grid.md`).",
)
s = s.replace(
    "| Full nightly v4.12 | **см. `report/FINAL_2026-10-31.md` / лог** | финальный прогон |",
    "| Full nightly v4.12 | **не перегонялся** | check_all 9/9, unit 32/32, smoke 6/6; BOTS sweep — count-only |",
)
s = s.replace(
    "- `[RUN]` 32/32 unit tests (v4.11); BCG split fast smoke PASS.",
    "- `[RUN]` 32/32 unit tests; BCG split fast smoke PASS.",
)
p.write_text(s, encoding="utf-8")
print("ok")
