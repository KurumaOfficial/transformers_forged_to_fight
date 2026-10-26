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

## What to check/do next

- Read `BCGManager.Instance +0xD8` live to confirm the local-calculation flag.
- For one bot, dump `BCGAttributeData` immediately after `HeroData.Create` and
  compare with `getBaseHeroData` to see which ctor path is used.
- Fill `heroes[rank].attr_base`/`hp_ratio`/`attack_ratio` and
  `attributeGrowthDefs`/`curves` with wiki-derived values; re-run and read
  Armor/Crit/Block/Mana. Do not patch client code.
- Wiki ability percentages are additive bonuses; compare after the base values
  are non-zero.

This is a **data/growth-table** problem, not a client patch.
