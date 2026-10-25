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

## R1 v2 (2026-10-25): corrected parser + separability

`work/fit_stat_growth_v2.py` parses columns by header name, strips HTML/scoped
headers, and fixes dot-thousands (`20.520` -> 20520). This removes the Hot Rod
7,267 RMSE artifact. 39 bots / 250 rows parse.

The linear `stat = a*rank + b*level + c` is still a poor model (HP worst:
Shockwave 3,280, Galvatron 2,928, Starscream 2,051). The log-additive global
model `log(stat) = intercept + rank + level + bot` fits Attack to ~3.5% and HP
to ~7.7% (log RMSE 0.035 / 0.074). However, the wiki's rows pair rank `r` with
level `10*r`, so the rank and level effects are **collinear**: the recovered
"rank" and "level" multipliers are the same ladder
(1.43, 1.64, 1.87, 2.13, 2.33). The data cannot separate rank from level.

Consequence: a common growth ladder can be reconstructed for the observed
tiers, but the per-bot intercept `h(bot)` is only identifiable for bots that
have at least one table row (39). The 47 bots with no stat table cannot be
derived from this model; their level-1 values stay `[ASSUMED]`.

`attributeGrowthDefs` in the stub catalog is a single linear definition
(`level`, `curve_linear`, attack+health, rounded); `curves` contains only
`curve_linear` (`a=1,b=1,c=0,exp=1,max=1000`). The real per-tier curves are not
present in the stub and must be supplied as server data if exact growth is
required.

Proposed server growth table:

```json
{
  "curves": {
    "hp_tier":  {"a": 1.0, "b": 1.0, "c": 0.0, "exp": 1.0},
    "atk_tier": {"a": 1.0, "b": 1.0, "c": 0.0, "exp": 1.0}
  },
  "attributeGrowthDefs": [
    {"level_key": "level", "curve_key": "hp_tier",  "attribute_keys": ["health"]},
    {"level_key": "level", "curve_key": "atk_tier", "attribute_keys": ["attack"]}
  ],
  "blueprints": {
    "<bid>": {"base_hp": 0, "base_attack": 0, "growth_multiplier": 1.0}
  }
}
```

## Growth table example (R1 3.3)

`data/wiki/growth_table_example.json` is the server-side shape:
`curves` (a,b,c,exp,max) + `attributeGrowthDefs` (`level_key`, `curve_key`,
`rounded`, `attribute_keys`) + per-blueprint `base_hp`/`base_attack`. The client
accepts this shape via `bcg_login_data.attributeGrowthDefs`; exact retail
constants are not in the stub and remain `[ASSUMED]`.
