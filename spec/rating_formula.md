# Rating formula — client static decode (R2.1)

Source: `GameUtil.CalculateModifiedHeroRating` at `0xA4814C`
(`dump.cs` TypeDefIndex unknown; RVA verified by disassembly). All labels
`[STATIC]`; live weights `[CLIENT]` from `bcg_login_data.json` /
`tuning_client_defaults.json`.

## Inputs

The function reads a `BCGAttributeData` at `+0x70` (`HeroRatingHP`, int),
`+0x74` (`HeroRatingAttack`, int), `+0x7C` (`HeroRatingAttackBase`, int) and
`+0xA0` (`ClassPower`, float, from the TF specialization). It also reads a
`BCGHeroClass` entry selected by `BCGBlueprintBase.HeroClass`:

| config field | offset | use |
|---|---:|---|
| `AttackBonus` | `0x20` | multiplier when the contender is ideal |
| `AttackPenalty` | `0x24` | multiplier otherwise |

`BCGManagerBase` instance weights:

| key | offset | value |
|---|---:|---:|
| `heroRatingMaxHPWeight` | `+0x108` | **0.2** |
| `heroRatingAttackWeight` | `+0x10C` | **1.0** |
| `ratingPrecision` | `+0x110` | **1.0** |

(The offsets are the three consecutive float reads at `0xA48264`,
`0xA4834C`, `0xA485B8`; the symbolic names follow the only consecutive
rating weights in `BCGManagerBase` and the key values in the login payload.
The exact field-name-to-offset order is `[ASSUMED]` until a live read is
recorded, but the values 0.2/1.0/1.0 are known from the payload.)

Function arguments:

- `x20` — `BCGAttributeData` (rating fields above)
- `x21`, `x23` — two `BCGBlueprintBase` objects (self/opponent)
- `x22` — optional `BCGAttributeData` supplying `ClassPower`
- `w19` — bool gate for the weight branch
- `s8` — float rating modifier (0 = unmodified)

## Operation order

```
hp        = (float)attributes.HeroRatingHP
atk       = (float)attributes.HeroRatingAttack
atkBase   = (float)attributes.HeroRatingAttackBase
classPwr  = attributes.ClassPower            // or 1.0 if x22 is null
classCfG  = heroClasses[blueprint.HeroClass]
bonus     = classCfg.AttackBonus             // ideal branch
penalty   = classCfg.AttackPenalty           // non-ideal branch

// branch 1: IsIdealContender(self, opponent) == true
extra = atkBase * bonus * classPwr * heroRatingAttackWeight

// branch 2: otherwise
extra = atkBase * penalty * classPwr * ratingPrecision

// common tail (0xA48728)
hpPart = hp * (1.0 - modifier * heroRatingMaxHPWeight)
rating = hpPart + atk + extra
return Mathf.CeilToInt(rating)
```

`Mathf.CeilToInt` is `0x1B58158` (`Gradient::public static int CeilToInt` in
the call map; the symbol is a generic-sharing thunk). There is **no**
`pow`, `sqrt`, or `RoundToInt` in the function. All arithmetic is float32;
the final conversion is ceiling to int.

## What the client does *not* do

The function never reads raw `HPMax` or `Attack`. `HeroRatingHP`,
`HeroRatingAttack` and `HeroRatingAttackBase` are **server-provided** fields
(`BCGAttributeData`), so the retail rating depends on the original server's
rating computation. The stub currently fills them with placeholders
(`rating_hp = int(hp*0.1)`, `rating_attack = int(atk*0.5)` in
`/bcg/getBaseHeroData`), which is why the UI rating is not the wiki rating.

## Consequences for R2.2/R2.3

- Fit the **server-side rating inputs** (`rating_hp`, `rating_attack`,
  `rating_attack_base`) from wiki rows, not the raw HP/ATK directly.
- If the wiki "Rating" is exactly `rating_hp + rating_attack` (plus a class
  bonus when the opponent is an ideal contender), the integer-exact test
  should be done on those inputs.
- The wiki star rows (`data/wiki/rating_rows.json`, 142 rows) have no
  rank/level, so they can only validate the final sum; the 236 rank/level
  rows are the primary fit set.

## Tests

`tests/test_rating_formula.py` implements the function above and asserts:

1. `modifier = 0`, `extra = 0` -> `ceil(hp + atk)`.
2. `modifier = 1`, `heroRatingMaxHPWeight = 0.2` -> `ceil(0.8*hp + atk)`.
3. ideal/non-ideal branch uses `AttackBonus`/`AttackPenalty` respectively.
4. no rounding before the final `ceil`.

The test is a direct transcription of the disassembly; it is not a claim that
the stub's current `rating_hp/rating_attack` values are correct.

## R2.2/R2.3 data fits (2026-10-26)

`data/wiki/rating_rows.json`: 236 stat rows, 221 with rating; 142 star rows.
`data/wiki/rating_fit_v2.json` records the fits.

| model | n | RMSE | integer exact |
|---|---:|---:|---:|
| HP + ATK + const | 221 | 920.7 | 1/221 |
| HP + ATK + rank + level + const | 221 | 873.0 | 0/221 |
| sqrt(HP*ATK) + const | 221 | 926.5 | 1/221 |
| star HP + ATK + const | 142 | 435.8 | 0/142 |
| leave-one-bot-out (linear) | 221 | mean 750.2 | - |

The log-log form is ill-conditioned (HP/ATK collinear) and is diagnostic only.
The 4 flagged outliers are `Ironhide (ROTF)` rank 6, `Ironhide` rank 1
(rating == HP, a likely level/column artifact), `Shockwave` rank 6 and
`Starscream` rank 6. No integer-exact formula exists on raw HP/ATK, which is
expected: the client formula consumes server-provided `HeroRatingHP`,
`HeroRatingAttack` and `HeroRatingAttackBase`, not raw stats.

Alignment rule used: HP, Attack and Rating are read from the same wiki row;
rows whose rating deviates by >=3 sigma are flagged, not silently dropped.
The next R2 step is to recover the server-side rating split, not to tune the
raw-stat regression further.

## R2.2/R2.3 LP result (2026-10-26)

`work/rating_lp.py` imposes the client interval for every wiki row:
`rating-1 < a*HP + b*ATK + c <= rating` (and a second model with rank/level).
Result: **infeasible** for all three LP models (stat, star, rank/level), and
infeasible per rank (1–6) and per level (1,10,20,30,40,50,60). L1 slack fit:
218/221 rows need a violation; the largest are Starscream R6, Ironhide R1
(rating == HP), Shockwave R6, Ironhide (ROTF) R6.

`data/wiki/rating_lp.json` records the feasible flags and the strongest
contradictions. Raw HP/ATK cannot produce the wiki Rating with any global
linear constants, including rank/level terms. This does **not** contradict the
client formula: the client consumes server-provided `HeroRatingHP`,
`HeroRatingAttack`, `HeroRatingAttackBase` and class weights, which are not in
the wiki rows. No tuning constants are recorded as `[DERIVED]`.

Parser sample (`work/parser_audit.py`, 20 random pages, seed 42):
**0 numeric misparses**; 2 empty rows (Mixmaster R5, Megatron ROTF R3) are
skipped. Header order is respected (`Attack, Health, Rating` pages included).
The parser is not the cause of the LP infeasibility.

## R2.4 UI check

Not performed: the bot-details screen is behind the global `FuseODRBlocker`
(`docs/odr_flow.md`). The client formula is proven, but there is no reliable UI
rating to compare until the blocker is cleared.

## R2.3 equivalent decomposition (2026-10-26)

`data/rating_table.json` contains one row per wiki stat/star row (363 rows).
For each row:

```
hero_rating_hp = round(rating * HP / (HP + ATK))
hero_rating_attack = rating - hero_rating_hp
client(hero_rating_hp, hero_rating_attack, extra=0, mod=0) = rating
```

This is an **equivalent proportional decomposition**, not the retail server
split. It is labelled `[DERIVED]` and is only for making the client formula
reproduce the wiki rating; do not use it as evidence of the original
`HeroRatingHP/Attack`. The LP result in `data/wiki/rating_lp.json` still shows
that raw HP/ATK alone cannot produce the rating with global constants.

UI verification is blocked by `FuseODRBlocker`; the bot details reachable during
the 59/59 sweep could be used later, but no rating readout was captured.
