from pathlib import Path

p = Path("report/FINAL_2026-10-30.md")
s = p.read_text(encoding="utf-8")
s = s.replace(
    "- `[RUN]` `check_all` PASS 9/9, 32/32 unit tests; golden shapes re-recorded\n  after the stat/post-battle changes. Full nightly rerun in progress.",
    "- `[RUN]` Full nightly **PASS** (2026-10-30 21:13): check_all 9/9, fast smoke\n  PASS, BOTS 59/59, battle step PASS (COMPLETED/LOST, player damage 203.7,\n  enemy 1289.6). Log `work/nightly/nightly_2026-10-30_211332.log`.",
)
s = s.replace(
    "| Full nightly после изменений | **нет** | последний PASS 2026-10-29 |",
    "| Full nightly после изменений | **PASS** | 2026-10-30 21:13, check_all/smoke/BOTS/battle step |",
)
s = s.replace(
    "8. **Полный nightly** — не перегонялся после текущих изменений.",
    "8. **Полный nightly** — PASS 2026-10-30 21:13; см. лог.",
)
p.write_text(s, encoding="utf-8")
print("ok")
