# BCG / Fighter schema (verified subset) — 2026-10-25

This is the schema used by the prefight/fight path. It is **not** a complete
dump of every client field; every entry below was read from `dump.cs` or from
live memory. Keys marked `[RUN]` were observed on the wire or in memory.

## BCGBlueprintBase (`TFBCGBlueprintBase`, TypeDef 8313/8380)

| field | offset | JSON path (verified/assumed) | type | null behavior |
|---|---:|---|---|---|
| Blueprint | 0x10 | `blueprint` / `id` | string | required |
| CharacterData | 0x18 | resolved from `character` | BCGCharacterData | null if lookup fails |
| EntityType | 0x20 | `entity_type` / `type` | string | `"hero"` |
| Character | 0x28 | `character` | string | required for asset load |
| FriendlyName | 0x30 | `friendly_name` / Loc | string | empty |
| FriendlyNameShort | 0x38 | `friendly_name_short` | string | empty |
| ModelID | 0x40 | **`m`** (`JSONPaths.m`) | string | empty -> character asset load fails |
| EvoBlueprint | 0x48 | `evo_blueprint` | string | empty |
| MapAssetID | 0x50 | `map_asset` | string | empty |
| HeroColour | 0x58 | `hero_colour` | string | empty |
| MaxRank | 0x60 | `max_rank` | int | 0 |
| Rarity | 0x64 | `rarity` | int | 0 |
| HeroClass | 0x68 | `class` / `hero_class` | enum | 0 |
| AttributeBaseType | 0x70 | `attribute_base_type` | string | empty |
| BCGCurveValues | 0x78 | `bcg_curve_values` | dict | empty |
| GachaReveal | 0x80 | `gacha_reveal` | string | empty |
| StaminaRegen | 0x88 | `stamina_regen` | string | empty |
| BaseDamageType | 0x90 | `base_damage` | list<string> | null/empty |
| BaseRangedDamageType | 0x98 | `base_ranged_damage` | list<string> | null/empty |
| Special1/2/3Damage | 0xA0/A4/A8 | `special_1_damage` etc. | float | 0 |
| MaxSpecialAttacks | 0xAC | `max_special_attacks` | int | 0 |
| AttackBonus | 0xB0 | `attack_bonus` | float | 0 |
| Tags | 0xB8 | **`t`** / `tags` | list<string> | null -> `HashSet` ctor throws |
| ImgID | 0xC0 | `imgID` | string | empty |
| S3ImgID | 0xC8 | `s3imgID` | bool | false |
| GachaFeaturedImg | 0xD0 | `gachaFeaturedImg` | string | empty |
| S3GachaFeaturedImg | 0xD8 | `s3GachaFeaturedImg` | bool | false |
| SynergyBonuses | 0xE0 | `synergy_bonuses` | list<string> | empty |

## BCGCharacterData (TypeDef 8314)

Fields: `Character` 0x10, `FriendlyName` 0x18, `FriendlyNameShort` 0x20,
`ModelID` 0x28, `MapAssetID` 0x30, `BaseDamageType` 0x38,
`BaseRangedDamageType` 0x40, `_imgID` 0x50, `_s3ImgID` 0x58,
`_gachaFeaturedImg` 0x60, `_s3GachaFeaturedImg` 0x68.
`get_ModelID` (0xC165DC) returns `ModelID` if `_characterData` exists; otherwise
it looks up `BCGManager` by `Character`. `ModelID` empty is fatal for the
battle prefab load.

## BCGHeroDetailsBase / BCGHeroDetails (TypeDef 8317/8388)

`Blueprint` 0x10, `Rank` 0x18, `Level` 0x1C, `SigLevel` 0x20, `HPRating` 0x24,
`HPMax` 0x28, `AttackRating` 0x2C, `Attack` 0x30, `Special` 0x34,
`UserOwned` 0x38, `AttributeData` 0x40, `ActiveSynergyBonuses` 0x48,
`PVPPointsBoosts` 0x50, `ForgeLevel` 0x58.

## FighterData (TypeDef 8671)

`Id` 0x10, `PlayerName` 0x18, `PlayerTag` 0x20, `IsBoss` 0x28,
`BaseAttributes` 0x30, `Attributes` 0x38, `Blueprint` 0x40, `SigLevel` 0x48,
`AttackBonus` 0x4C, `AIProfile` 0x50, `OverrideAIPersonality` 0x58,
`TeamData` 0x60.

## BCGAttributeDataBase (TypeDef 8303)

`StatMods` 0x10, `SigMods` 0x18, `BuffMods` 0x20, `SpecialAttackCount` 0x28,
`HPMax` 0x2C, `HPMaxBase` 0x30, `HP` 0x34, `Attack` 0x38, `AttackBase` 0x3C,
`Armor` 0x40, `CritChance` 0x44, `CritDamage` 0x48, `PerfectBlockChance` 0x4C,
`BlockProficiency` 0x50, `ManaGain` 0x54, `ManaStart` 0x58,
`ResistMagic` 0x5C, `ResistPhysical` 0x60, `StunTime` 0x64, `StunChance` 0x68,
`HeroRating` 0x6C, `HeroRatingHP`/`Attack`/bases around 0x70–0x7C.

## PlayerAttributes.Init (0xDAB16C) — current NRE

At `0xDAC198` it constructs `HashSet<string>` from `_blueprint.Tags`
(`[_blueprint+0xB8]`). The live `FighterData.Blueprint.Tags` for the player and
enemy is non-null (count 2), so the observed `ArgumentNullException(collection)`
still needs an exact instance/breakpoint. The method also copies:
`FighterData+0x30 -> +0x50`, `+0x38 -> +0x58`, `+0x40 -> +0x48`,
`+0x48 -> +0x38`, `+0x60 -> +0x30`; it creates `AttributeManager`
stat dictionaries, class/signature values, and `_health/_mana/_attack` etc.

## Activation / response

`PrefightScreenData.OnFight` (`0xE3ECDC`) builds the player and enemy
`FighterData` from `HeroData`/`BCGEntity`; `Blueprint` is copied at
`+0x40`, `BaseAttributes` at `+0x30`, `Attributes` at `+0x38`, `TeamData` at
`+0x60`. The `match_activate_response` is still `[ASSUMED]`; it is not the
source of the prefight `FighterData` fields observed on the wire.
