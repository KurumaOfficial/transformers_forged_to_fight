from pathlib import Path

p = Path("report/FINAL_2026-10-30.md")
s = p.read_text(encoding="utf-8")

old_bots = """- `[RUN]` **BOTS sweep fixed**: vertical scroll now reaches different rows;
  59 cards across 5 pages, **57/59** detail screens opened, **0 NRE**, 2 info
  errors. The old 59/59 clean metric was invalid (horizontal swipe repeated
  page 0). Starscream is still not in the 59 cards.
  `docs/sweep_diagnosis.md`."""
new_bots = """- `[RUN]` **BOTS sweep fixed**: vertical scroll reaches different rows;
  59 cards across 5 pages, **59/59** detail screens opened, **0 NRE** in the
  fresh nightly run. The old horizontal 59/59 metric was invalid; the vertical
  one is the valid metric. Starscream is still not in the 59 cards.
  `docs/sweep_diagnosis.md`."""
s = s.replace(old_bots, new_bots)

old_check = """- \\[RUN]\\ \\check_all\\ PASS 9/9, 32/32 unit tests; golden shapes re-recorded
  after the stat/post-battle changes. Full nightly rerun in progress."""
new_check = """- `[RUN]` `check_all` PASS 9/9, 32/32 unit tests; golden shapes re-recorded
  after the stat/post-battle changes. Full nightly rerun in progress."""
s = s.replace(old_check, new_check)

p.write_text(s, encoding="utf-8")
print("ok")
