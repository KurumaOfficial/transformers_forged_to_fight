# Stat growth fit — HP/Attack vs rank and level

Status: **partial, [DERIVED]**. Source: `data/wiki/bots.json`
`stat_tables` (36 bots with >=3 rows). Script: `work/fit_stat_growth.py`;
raw fit: `data/wiki/stat_growth_fit.json`.

## Model tested

`stat = a*rank + b*level + c` (ordinary least squares, per bot, HP and Attack
separately). Rows are the wiki's sparse `Rank/Level` table points
(e.g. `1/1`, `1/10`, `2/20`, ...).

## Result

- 36 bots had at least 3 usable rows.
- The simple linear model is **rejected** for most bots: HP RMSE is often
  ~700–1,000 and reaches >2,000–7,000 on some 5-star tables; Attack RMSE is
  usually 50–250. Rank-ups and level-ups are not additive in this space.
- Best fits (lowest combined error): Mixmaster (HP RMSE 457 / ATK 24.9),
  Waspinator/Rhinox have low HP error but very high Attack error (their
  table layout/columns differ; parser needs a per-bot column check).
- Worst fits: Hot Rod (HP RMSE 7,267), Shockwave (3,280), Galvatron (2,928).
- Conclusion: the original growth is a curve/table lookup, not a single
  linear rank+level plane. The client's `curves` / `attributeGrowthDefs`
  data should be used instead of a fitted line.

## Consequences

- Do **not** use this fit to claim wiki stats for the 47 bots without a
  star-1 table. Their rank-1 values remain `[ASSUMED]` (1000 HP / 120 ATK)
  or must be reconstructed from the client curve data, not from this model.
- Next: fit piecewise per-rank curves (`level` only) and per-rank
  multipliers, using the wiki rows; inspect `curves` and
  `attributeGrowthDefs` in `bcg_login_data.json` for the real constants.
- The parser should detect column position by header, because some tables
  put Attack/HP in a different order (`Waspinator`, `Rhinox`).

## Source labels

- Wiki rows: `[WIKI]`.
- Fit and errors: `[DERIVED]`.
- Bots without tables: `[ASSUMED]` until curve data is resolved.
