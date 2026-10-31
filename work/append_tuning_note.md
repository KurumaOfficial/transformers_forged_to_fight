
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
