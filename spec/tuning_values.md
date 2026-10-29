# Tuning values and effects (Step 8.2, partial)

Status: **partial.** The complete field list is in `spec/tuning_keys.md`.
This file records the values we have decoded from the client and the
`bcg-combat` config, plus the effects proven by a live battle.

## Current `/tuning` payload

`server/data/tuning_data.json`:

```json
{
  "heroRatingAttackWeight": 1.0,
  "heroRatingMaxHPWeight": 0.2,
  "sigLvlMax": 100,
  "ratingPrecision": 0
}
```

These are BCG/rating keys, not `Tuning` component fields.

## `TuningGameplay` (mode `bcg-combat`)

`TuningGameplay.OnConfigChanged` (`0x14254BC`) calls `DeserializeData`
(`0x1425540`) only when `ConfigManager` delivers mode **`bcg-combat`**. The
config is under `missions_config.json`:
`missionsconfig.configs["bcg-combat"]`.

The keys are the literal JSON paths used by the constructor; several are
generic names (`armor_break`, `mana_gain`, `critTime`).

| field | key | code default | live after fix | effect |
|---|---|---:|---:|---|
| `ManaPerSpecial` | `mana_gain` | 300.0 | 300.0 | mana per special (client-side) |
| `ArmorRatingConstant` | `armor_break` | 200.0 | 200.0 | armor DR denominator; 0 => 100% reduction, **zero damage** |
| `CritRatingConstant_A` | `critTime` | 111.0 | 111.0 | crit-rating constant |
| `DefenderManaModifier` | (multi-path) | 1.25 | 1.25 | defender mana multiplier |
| `DefenderManaBlockedModifier` | (multi-path) | 0.35 | 0.35 | defender mana on block |
| `AttackChainResetTime` | `attackPhaseTimeLength` | 0.75 | 0.75 | attack-chain reset time |
| `EvadeMeleeSpeed` | (path) | 100.0 | 100.0 | melee evade speed |
| `MeleeRangeMod` | (path) | 0.0 | 0.0 | melee range modifier |
| other fields | unknown | unknown | unknown | `TuningGameplay` has 30 public fields; not all keys/defaults decoded |

Live `TuningGameplay` values were read with `work/probe_tuning_gameplay.py`
(300/200/111/1.25/0.35/0.75/100). The probe is read-only.

## Proven effects

- `ArmorRatingConstant=0` made `GetArmorDR(50) = 50/(50+0) = 1.0`, so every
  hit on the armored fighter was reduced to 0. With 200, DR = 0.2 and a Light
  hit did 64.4 instead of 0. `[RUN]` `docs/damage_pipeline.md`.
- Normal win after the fix: player HP 300.2, enemy 0, player damage 1069.5.
  `[RUN]` `docs/evidence/post_battle_2026-10-29/resolve_win_normal.json`.

## `Tuning` ODR fields (read-only live)

| field | live | note |
|---|---:|---|
| `ODRForceDownloadAll` | 0 | data-only |
| `ODRAllowNative` | 1 | data-only |
| `ODRShowProgressMB` | 1 | UI |
| `ODRShowTimeEstimate` | 1 | UI |
| `ODRForceDownloadAssetListPreTutorial` | 0 | data-only |

Not changed; `spec/tuning_keys.md` has the full 242-field table.

## Not decoded

- Defaults/effects for the remaining 23 `TuningGameplay` fields.
- Consumers of most of the 242 `Tuning` fields.
- Which tuning keys affect rating/stat screens beyond the four BCG keys.
