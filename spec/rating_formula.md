# Hero rating formula — static findings (C2)

Status: **partial** `[STATIC]+[DERIVED]`; no runtime numeric validation yet.

## Entry point

`GameUtil.CalculateModifiedHeroRating` — RVA **0xA4814C**:

```
CalculateModifiedHeroRating(
    BCGBlueprintBase targetBlueprint,
    BCGBlueprintBase opponentBlueprint,
    BCGAttributeData targetAttributes,
    BCGAttributeData opponentAttributes,
    float healthPct = 1,
    bool useSelectionBias = false)
```

The method reads target attributes at `+0x70` (HP rating), `+0x74` (attack
rating), `+0x7c`, `+0xa0`, and class/manager data. It calls
`BCGManager.get_Instance()` and reads weights at manager instance
`+0x108` and `+0x10c`. The dump names these properties:

- `BCGManagerBase.heroRatingAttackWeight`
- `BCGManagerBase.heroRatingMaxHPWeight`
- `BCGManagerBase.ratingPrecision`

`server/data/tuning_data.json` currently supplies:

```json
{"heroRatingAttackWeight": 1.0, "heroRatingMaxHPWeight": 0.2,
 "sigLvlMax": 100, "ratingPrecision": 0}
```

These four values are the only ones marked `[CLIENT]` in
`server/data/tuning_client_defaults.json`; they are **defaults/placeholders**
until a full TuningManager field scan is done.

## Shape of the arithmetic

At `0xA48728`–`0xA48744` the final expression is:

```text
hpPart   = float(HP_rating) - (1 - healthPct) * float(HP_rating) * maxHPWeight
attackPart = classAttackBonus * baseAttack * attackModifier * attackWeight
raw      = hpPart + attackPart
rating   = CeilToInt(raw)
```

The exact binding of the middle operands (`[targetAttributes+0x7c]`,
`[targetAttributes+0xa0]`, `[classData+0x20]`) is not proven; treat the
pseudocode as `[DERIVED]`, not a final formula. The `CeilToInt` call and the
health-percentage subtraction are directly observed.

## Cross-check material

Wiki pages carry `Max Rating` for 2★–4★ (for example Bumblebee:
2★ 566, 3★ 1,299, 4★ 3,499). Those values can bound the formula once
`HeroRatingHP`/`HeroRatingAttack` for the same bot/rank are dumped. Until then
they are only a monotonic sanity check, not a derivation.

## What is still needed

- A runtime dump of `BCGAttributeData` fields `+0x70/+0x74/+0x7c/+0xa0`.
- The actual `heroRatingAttackWeight`/`heroRatingMaxHPWeight` from
  `/tuning` or TuningManager, not the stub defaults.
- `ratingPrecision` semantics (rounding/truncation) and whether
  `useSelectionBias` changes the weight.
