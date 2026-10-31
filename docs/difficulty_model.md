# Difficulty model: test vs calibrated (Step 5)

Status: **model defined; 20+20 series not completed.** The battle pipeline
supports both modes, but only the normal pipeline has a long series.

## Two explicit modes

| mode | trigger | enemy stats | use |
|---|---|---|---|
| `test` | `work/weak_enemy.flag` present | `sideswipe_gs` / `enemy1` HP=1, ATK=1 | pipeline, rewards, tile/progress checks only |
| `calibrated` | flag absent (normal) | boss `rank`/`level` from the quest; stats from `server/wiki_stats.py` | balance/reporting; no forced wins |

The weak flag is **test-only** and must be removed after the run. It is not a
balance claim.

## Calibrated source `[WIKI]`/`[DERIVED]`

- `server/routes/quests.py:scaled_boss` emits `rank`, `level`, `sig_lvl`,
  `characters=[bid]` from `quest_list.json`.
- `server/routes/bcg.py:base_hero_data` calls
  `wiki_stats.stats_for(bid, rank, level)`; the same helper feeds the catalog,
  the quest team and the boss table.
- `wiki_stats.stats_for` uses the wiki rank/level fit (`stat_growth_fit.json`)
  and the exact 1/1 rating row when available; bots without a fit use the
  level-1 anchor + median growth (`[DERIVED]`, ~12% uncertainty), otherwise the
  old placeholder (`[ASSUMED]`, ~40%).
- `recommendedPartyPI` is read from the quest; it is not used to overwrite the
  boss stats.

## Results so far

- `[RUN]` 20-fight normal series (pre-wiki stats): 1 WON / 19 LOST; this is the
  old series, not a post-wiki calibration.
- `[RUN]` Post-wiki normal battle step: COMPLETED/LOST, player damage
  67.9-271.6, enemy damage 1248-1497; HP decreases and resolve-match works.
- `[RUN]` Weak-enemy wins used for post-battle checks (VICTORY/PERFECT
  screens); no 20-fight weak series yet.
- `[RUN]` 3-fight weak series started 2026-10-31; result file is
  `tests/smoke/battle_series.json` when it finishes.

## What is not proven

- 20 wins/losses in **both** modes with duration/damage/HP curves.
- Boss rating growth across acts 1.1, 2.x, 3.x.
- A balance target. The current normal result is a loss with the real wiki
  numbers; that is recorded, not tuned away.
