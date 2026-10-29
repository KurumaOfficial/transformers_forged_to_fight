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


## All `TuningGameplay` fields (static)

The class has 30 serialized fields plus `Instance` and
`_tutorialTriggerCount`. Only the fields below have a decoded live value;
the rest are listed as unknown rather than guessed.

| field | offset | type | live/default | note |
|---|---:|---|---|---|
| `ManaPerSpecial` | 0x18 | SafeFloat | 300 | `mana_gain` |
| `ArmorRatingConstant` | 0x20 | SafeFloat | 200 | `armor_break` |
| `CritRatingConstant_A` | 0x28 | SafeFloat | 111 | `critTime` |
| `DefenderManaModifier` | 0x30 | SafeFloat | 1.25 | live |
| `DefenderManaBlockedModifier` | 0x38 | SafeFloat | 0.35 | live |
| `AttackChainResetTime` | 0x40 | SafeFloat | 0.75 | `attackPhaseTimeLength` |
| `EvadeMeleeSpeed` | 0x48 | SafeFloat | 100 | live |
| `MeleeRangeMod` | 0x50 | SafeFloat | 0 | live |
| `DefaultAnimatorScale` | 0x58 | float | unknown | |
| `UnstoppableKnockbackFactor` | 0x5C | float | unknown | |
| `GrenadeGravity` | 0x60 | float | unknown | |
| `ProjecticleMinMeleeKnockback` | 0x64 | float | unknown | spelling is the client's |
| `DefaultProjectileSpeed` | 0x68 | float | unknown | |
| `MinProjectileSpeed` | 0x70 | SafeFloat | unknown | |
| `MaxProjectileSpeed` | 0x78 | SafeFloat | unknown | |
| `MaxQueuedActionTime` | 0x80 | SafeFloat | unknown | |
| `MinVisibleHitStreak` | 0x88 | int | unknown | |
| `MinSpecialGlowQuality` | 0x8C | enum | unknown | |
| `GlobalStatMods` | 0x90 | string[] | unknown | affects all fighters |
| `PlayerDashCurve` | 0x98 | VelocityCurve | unknown | |
| `PlayerDodgeCurve` | 0xB0 | VelocityCurve | unknown | |
| `PlayerSidestepCurve` | 0xC8 | VelocityCurve | unknown | |
| `TutMaxTotalPerFight` | 0xE0 | int | unknown | |
| `TutMaxUniquePerFight` | 0xE4 | int | unknown | |
| `TutMinTimeBetween` | 0xE8 | float | unknown | |
| `TutAttacksToTrigger` | 0xF0 | string | unknown | |
| `SlowAnimStartLvl` | 0xF8 | SafeInt | unknown | |
| `SlowAnimEndLvl` | 0x100 | SafeInt | unknown | |
| `AOESelfEdgeColor` | 0x108 | Color | unknown | UI |
| `AOEOpponentEdgeColor` | 0x118 | Color | unknown | UI |

`TuningGameplay.DeserializeData` (`0x1425540`) reads the `bcg-combat` config;
`OnConfigChanged` (`0x14254BC`) only calls it for that mode. The full `Tuning`
component has 242 fields (`spec/tuning_keys.md`); most consumers are still
unmapped. This table is [STATIC] from `dump.cs` plus [RUN] live values.
