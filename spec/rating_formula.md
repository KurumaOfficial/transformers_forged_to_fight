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
