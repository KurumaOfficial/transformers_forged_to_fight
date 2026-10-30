# 20-fight battle series (Step 7.1)

Status: **series in two halves.** The first 10/10 fights PASS the battle-step
contract (resolve-match, damage, HP drop). All ten ended in a loss under the
automatic attack loop; that is a gameplay/positioning result, not a protocol
failure.

## First half `[RUN]`

Source: `tests/smoke/battle_series_part1.json`, normal server data, no
`weak_enemy` flag.

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

Observations:

- `resolve_match=true`, `damage_nonzero=true`, `hp_decreases=true` for all 10.
- Enemy HP at the end ranges 43.75–607.25; the player damage range is
  442.75–1006.25. The fight is real, not a zero-damage stub.
- The automatic tap loop does not block/dodge well enough to win; the earlier
  normal win (HP 300.2, enemy 0, damage 1069.5) needed better timing.
- Series was split because the emulator/server stopped during the first
  20-fight run; the second 10-fight run continues from a fresh launch.
- Final combined file: `tests/smoke/battle_series_20.json` (merge via
  `work/merge_series.py`).
