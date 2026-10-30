# 20-fight battle series (Step 7.1)

Status: **20/20 COMPLETED** on the battle-step contract (resolve-match,
damage, HP drop): **1 WIN, 19 LOSS** under the automatic attack loop; no
weak-enemy test data was used. Old files say PASS for the same mechanic
completion; the new report fields are completed + outcome.

## Results `[RUN]`

Sources: `tests/smoke/battle_series_part1.json` (fights 1-10) and
`tests/smoke/battle_series.json` (fights 11-20), merged into
`tests/smoke/battle_series_20.json`.

| # | result | player HP | enemy HP | player damage |
|---:|---|---:|---:|---:|
| 1 | LOST | 0 | 607.25 | 442.75 |
| 2 | LOST | 0 | 567.0 | 483.0 |
| 3 | LOST | 0 | 526.75 | 523.25 |
| 4 | LOST | 0 | 285.25 | 764.75 |
| 5 | LOST | 0 | 406.0 | 644.0 |
| 6 | LOST | 0 | 285.25 | 764.75 |
| 7 | LOST | 0 | 43.75 | 1006.25 |
| 8 | LOST | 0 | 285.25 | 764.75 |
| 9 | LOST | 0 | 325.5 | 724.5 |
| 10 | LOST | 0 | 567.0 | 483.0 |
| 11 | LOST | 0 | 245.0 | 805.0 |
| 12 | LOST | 0 | 325.5 | 724.5 |
| 13 | LOST | 0 | 3.5 | 1046.5 |
| 14 | LOST | 0 | 204.75 | 845.25 |
| 15 | LOST | 0 | 204.75 | 845.25 |
| 16 | LOST | 0 | 446.25 | 603.75 |
| 17 | **WON** | **166.8** | **0** | **1127.0** |
| 18 | LOST | 0 | 245.0 | 805.0 |
| 19 | LOST | 0 | 204.75 | 845.25 |
| 20 | LOST | 0 | 365.75 | 684.25 |

## Observations

- `completed=true`, `damage_nonzero=true`, `hp_decreases=true` for all 20.
- Outcome: **1 WON** (fight 17, HP 166.8/0, damage 1127) and **19 LOST**.
- Enemy HP at the end ranges **3.5-607.25**; player damage ranges
  **442.75-1127.0**. The fight is real, not a zero-damage stub.
- Fight 17 is a **normal win without test data**: player HP 166.8, enemy HP 0,
  player damage 1127.0. This is the second independent normal win (the first
  was 300.2 / 0 / 1069.5).
- The auto-loop usually loses because it does not block/dodge well; the win
  proves the full win path is reachable with normal data.
- The series was split into two 10-fight runs because the emulator/server
  stopped during the first 20-fight attempt; both halves used a fresh launch.
- The merge is reproducible with `work/merge_series.py`.
