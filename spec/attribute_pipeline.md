# Attribute pipeline / hidden base stats (Step 2)

Status: **partial.** Field layout, JSON keys and the live-vs-server mismatch are
proven; the exact class/star growth formula is not fully decoded.

## Static chain

`BCGAttributeDataBase` (TypeDef 8303) fields and offsets:

| field | offset | JSONPaths key |
|---|---:|---|
| StatMods / SigMods / BuffMods | 0x10/0x18/0x20 | `stat_mods`/`sig_mods`/`buff_mods` |
| SpecialAttackCount | 0x28 | `special_attacks` |
| HPMax / HPMaxBase | 0x2C/0x30 | `hp_max`/`hp_max_base` |
| HP | 0x34 | `hp` (float default **1.0**) |
| Attack / AttackBase | 0x38/0x3C | `attack`/`attack_base` |
| Armor | 0x40 | `armor`/`arm` |
| CritChance / CritDamage | 0x44/0x48 | `crit_chance`/`cc`, `crit_damage`/`cd` |
| PerfectBlockChance | 0x4C | `perfect_block_chance`/`pbc` |
| BlockProficiency | 0x50 | `block_proficiency`/`bp` |
| ManaGain / ManaStart | 0x54/0x58 | `mana_gain`/`mg`, `mana_start`/`ms` |
| ResistMagic / ResistPhysical | 0x5C/0x60 | `resist_magic`/`rm`, `resist_physical`/`rp` |
| StunTime / StunChance | 0x64/0x68 | `stun_time`/`st`, `stun_chance` |
| HeroRating | 0x6C | `hero_rating` |
| HeroRatingHP / Attack | 0x70/0x74 | `hero_rating_hp`/`hero_rating_attack` |
| HeroRatingHPBase / AttackBase | 0x78/0x7C | `hero_rating_hp_base`/`hero_rating_attack_base` |
| isModified | 0x80 | `is_modified` |

`BCGAttributeData..ctor` (`0xC14864`) reads those paths with `Dot.Integer`/
`Dot.Single`; the HP default is 1.0 (`0xC149C0 fmov s0,#1.0`). Other floats
default 0.0, ints 0. `TFBCGAttributeData` adds `BuffType`/`SigBuffType`,
`CritRate` (0x8C), `ResistCritRate` (0x90), `ResistCritDamage` (0x94),
`SpecialBonus` (0x98), `ProjectileBonus` (0x9C), `ClassPower` (0xA0),
`ArmorPenetration` (0xA4), `BlockPenetration` (0xA8).

`AttributeManager.CreateStatAttributes` (`0xC9960C`) builds the live
`StatAttribute` dictionary (`BoolStatAttribute`, `DRStatAttribute`,
`MaxStatAttribute`, `StatAttribute`); `PlayerAttributes.Init` copies
`FighterData.Attributes` (`+0x38`) into `_attributes` (`+0x58`) and initializes
`_health`/`_mana`/`_attack`.

`BCGManager.clientCalculateHeroBaseAttributes` is at +0xD8 (boolean); when
true, the client recalculates base attributes from the catalog/growth data
instead of trusting the flat server `getBaseHeroData` values on the battle
path.

## Live values vs the flat response (`[RUN]`)

`docs/battle_memory_values.md`: HPMax 1050 and Attack 115 applied; Armor 0,
CritChance 0, CritDamage 0, BlockProficiency 0, ManaGain 0 despite the flat
`getBaseHeroData` sending 0.0/0.1/1.5/0.5/1.0. HP read 1.0 (the ctor default)
while HPMax was 1050. This proves the battle `BCGAttributeData` was not built
from the flat fields we supplied; the client's local calculation path supplied
or left those fields at defaults.

## Where defaults can live

1. `BCGAttributeDataBase` ctor defaults (HP=1.0, others 0) — `[STATIC]`.
2. `bcg_login_data.heroes[bid][rank]`:
   `attr_base`, `hp_ratio`, `attack_ratio`, `hero_rating_hp`,
   `hero_rating_attack`, `hp_mod`, `attack_mod`, `max_level`, `exp_growth`,
   `flat_growth`, `attack_ratio`, `hp_ratio`, `invest_*`.
3. `attributeGrowthDefs` + `curves` (our current data is placeholder).
4. `attackValues` (basic melee percent/crit/mana) and `damage_types`.
5. Class/star tables in `BCGAttributeGrowthInfo`/`BCGCurve` and the
   `BCGAttributeData` class modifiers.
6. `statMods`/`sigMods`/`synergyBonuses`/forge/relics.

## SOLVED [RUN]: player quest-battle hidden attributes (2026-10-27)

Root cause is **not** the client failing to parse the values; it is the quest
team payload being the player's battle-attribute source.

- `[STATIC]` `TeamData.RefreshHeroData` (`0x10DE4D0`) uses
  `HeroData.CreateForModes` (`0xE8A7D8`) when the team detail has
  `UserOwned=true` (`+0x38`); server-generated enemies use
  `HeroData.CreateWithServerGeneratedDetails` (`0xE8C098`).
- `[STATIC]` `HeroDataShared.get_attributes` (`0x12AD058`) returns
  `mUserTeamHero.AttributeData` (`BCGHeroDetailsBase+0x40`) when the team
  detail exists; otherwise it falls back to `mUserHero.AttributeData`
  (`BCGUserHeroBase+0x38`).
- `[STATIC]` The local upgrade path only copies HPMax/Attack/RatingHP/
  RatingAttack:
  `BCGUpgradeAttributesBase.UpdateFromBCGAttributeData` (`0xA60FC8`) and
  `UpdateBCGAttributeData` (`0xA61018`) touch only `+0x2c`, `+0x38`, `+0x6c`,
  `+0x70`, `+0x74`. It never copies Armor/Crit/Block/Mana from the catalog
  rank entry, so putting those keys only into `heroes[bid][rank]` is not
  enough for a player quest fight.
- `[RUN]` The player's `BCGHeroDetails` comes from the active team /
  `quest-begin` team payload, not from `/bcg/getBaseHeroData` (no
  `getBaseHeroData` request for the player was observed; only
  `sideswipe_gs` and `enemy1`).
- `[RUN]` Adding `armor`, `crit_chance`, `crit_damage`,
  `perfect_block_chance`, `block_proficiency`, `mana_gain`, `mana_start`,
  `resist_magic`, `resist_physical`, `stun_time`, `stun_chance` to each
  `quest["team"][bid]` and `teamData.updates.activeTeams[].heroes[bid]`
  object makes the live player `BCGAttributeData` non-zero:
  Armor 50.0, CritChance 0.1, CritDamage 1.5, BlockProficiency 0.5,
  ManaGain 1.0 (PerfectBlock/ManaStart remain 0 because 0 was sent).
- The same keys were added to the login `activeTeams[].heroes[]` entries so
  non-quest prefight/display paths see them too.

The values above are `[ASSUMED]` defaults, not retail per-bot stats. They
prove the pipeline and the data source; per-bot/star/rank values still need
wiki or retail evidence.

## What to check/do next

- Replace the assumed flat defaults with per-bot/per-rank values if the wiki
  or a later data source provides them.
- Confirm ManaStart/PerfectBlock/Resist/Stun non-zero by sending distinct
  values in the same team payload (pipeline is now proven).
- Wiki ability percentages are additive bonuses; compare after the base
  values are non-zero.
- `clientCalculateHeroBaseAttributes` is still not read live; it is not needed
  for the hidden-stat fix, but remains an open static question.

This is a **data/team-payload** problem, not a client patch.


## 2026-10-29 attackValues and zero-damage blocker [RUN]

`AttackLevel` enum is `None/Light/Medium/Heavy/Ranged/Special1..3/Special/
Normal`; `PlayerAttributes.kAttackLevelEnums` maps those to the exact strings
`Light`, `Medium`, `Heavy`, `Ranged`, `Special1/2/3`, `Special`, `Normal`.
`GetAttackPercent` (`0xDAD2E4`) looks them up in `BCGManager.AttackValueData`.
Our old table had only `basic_melee`, so the lookup returned 0. New entries
were added as `[ASSUMED]` percentages (Light 0.7, Medium 1.0, Heavy 1.5,
Ranged 0.7, Special1/2/3 1.0/1.5/2.0), plus the literal `attack_percent` key
that `BCGAttackValue..ctor` (`0xC145BC`) reads for `Percent`:

```
Doc.Single(data, "percent", "attack_percent", default=0)
```

After this, live `DamageRating` for a Light hit became **0.7** (was 0).

The final damage is still **0** because `PlayerAttributes._attack.Get()`
returns 0 while `_attack._value` (display) is 115: the plain value is set but
the `FastSafeFloat` safe value used by `Get()` is 0. `HitResultData.Damage`
is 0 while `DamageRating` is 0.7 and `Flags=129` (Hit+LastHit). This is the
current combat blocker; it is a client stat commit issue, not a missing
server field. Do not patch the client to bypass it.

## 2026-10-29 correction and damage formula [RUN]

- The earlier `_attack.Get()=0` claim was wrong (IL2CPP byte[] elements are
  inline at `+0x20`; safe value is 115, hash OK).
- `ArmorRatingConstant` was 0, so `GetArmorDR = armor/(armor+0)` = 1.0.
  Add `missionsconfig.configs["bcg-combat"]`:
  `armor_break=200`, `mana_gain=300`, `critTime=111` -> live 200/300/111.
- `GetDamageInflicted`: `clamp01(HitData.Damage) * GetAttackPercent *
  GetAttackBonusMultiplier * _attack.Get()` (+crit, +flat). Live Light hit:
  0.7 * 1 * 115 = 80.5; after armor DR 0.2: 64.4.
- `GetDamageReceived`: block/perfect-block, indestructible/invulnerable,
  armor DR, damage resistances, protection clamp, minHP clamp.
- `GetArmorDR`: `armor/(abs(armor)+ArmorRatingConstant) + up - break`.
- Win/loss -> resolve -> map: `docs/evidence/post_battle_2026-10-29/`.
