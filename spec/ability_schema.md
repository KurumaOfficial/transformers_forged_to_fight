# Ability / stat-mod schema (verified subset)

Status: **partial**. The client has no single `Ability` JSON class; abilities
are composed from `statMods`, `Buff`, `BCGStatModifierAppearance` and
`attackValues`, plus per-blueprint damage floats.

## `statMods` (catalog key, `bcg_login_data.statMods`)

Observed keys in the stub entry `stat_mod_attack_pct`:

| key | type | meaning |
|---|---|---|
| `id` | string | modifier id |
| `var` | string | target attribute (`attack`, ...) |
| `modSource` | string | passive / trigger source |
| `growthTarget` | string | curve target |
| `growthCurve`, `ratingCurve` | string | curve ids (`curve_linear`) |
| `appearanceID` | string | key into `statModAppears` |
| `auth` | list<string> | blueprint ids allowed to use it |
| `growthConst` | float | curve constant |
| `stackable` | int | stack flag |
| `tier` | int | tier |
| `heroRatingHP`, `heroRatingAttack` | float | rating weights |
| `chance` | float | proc chance |
| `modifier` | float | numeric modifier |
| `duration` | float | 0 = permanent |
| `priority` | int | ordering |
| `triggerMod` | float | trigger threshold |

`statModAppears` supplies `ability_title_id`, `short_string_id`,
`long_string_id`, `simple_string_id`, `icon_texture`, `fx_profile`,
`callout_*` colors/texts. These are localization keys, not raw display text.

## `Buff` (TypeDef 6945)

Fields: `tintColour` 0x10, `id` 0x20, `iconTexture` 0x28, `_imagePath` 0x30,
`modesAvail` 0x38, `scope` 0x40, `valueStr` 0x48, `_valueType` 0x50,
`_localizedName` 0x58, `_localizedDesc` 0x60, `buffType` 0x68,
`buffParams` 0x70, `group` 0x78.

`BuffGroup` (6941): `stackable` 0x10, `active_display` 0x11.
`BuffsConfig` (6942): `groups` dictionary.

## `attackValues`

`basic_melee`: `percent`/`p` 1.0, `mana_gain`/`m` 0.05,
`crit_chance`/`c` 0.05, `crit_damage`/`d` 1.5, `crit_pierce` 0.0.
The blueprint `special_1_damage`, `special_2_damage`, `special_3_damage` are
floats (1.0/1.5/2.0 for Bumblebee).

## Special-attack localization

The details screen shows `M1_SPECIAL_ATTACK_<BOT>.<n>`. A scan of
`work/unpacked/assets` found **no** `M1_SPECIAL_ATTACK`, `SPECIAL_ATTACK_<BOT>`
or `<BOT>` key for Wheeljack; `global-metadata.dat` contains only generic
`ID_SPECIAL_ATTACK` / `ID_SPECIAL_ATTACK_DESCRIPTION` keys. The raw string is
therefore an **animation/move id**, not a localization key present in the
retained tables. Fixing it needs the missing per-bot move-name table, not a
server alias alone.

## Pilot data

`data/wiki/ability_pilot.json` collects the wiki ability text for Bumblebee,
Rhinox and Optimus Prime. It is `[WIKI]` source data only; it is not yet wired
into `statMods` because the wiki text has no stable client stat-mod ids.

## Missing schema pieces

- Full trigger/condition enum table and `StatModifier` factory branch list.
- Per-bot special-attack name table.
- Exact `Buff` JSON path list and stack/refresh rules.
- `BCGStatModifier` ctor keys (only the sample entry above is verified).

## 2026-10-30 Step 5 pilot assessment

The wiki numbers are available (data/wiki/ability_pilot.json), but the
client schema cannot represent the three pilots as statMods alone:

| wiki effect | client representation | status |
|---|---|---|
| Bumblebee Melee Evade 24-34% | StatModifierAttributes has no Evade entry; PlayerAttributes._evadeMelee is a separate field | no statMod var |
| Bumblebee Critical Rate Buff | CritChance exists, but the buff is 3 stacks removed on hit | needs Buff/trigger graph |
| Bumblebee Shield Break + Shock | Buff class exists; no decoded uffParams/trigger JSON | blocked |
| Rhinox Shield 6 stacks | Buff class exists; no decoded shield/stack JSON | blocked |
| Rhinox Bleed / Power Lock | no Bleed/PowerLock stat enum; needs Buff | blocked |
| Optimus Prime | wiki text not yet mapped to a client factory | blocked |

The only verified statMods entry is stat_mod_attack_pct
(id, ar: attack, modSource: passive, modifier: 0.1,
uth: [bumblebee_cin_dotm_2]). Adding a permanent crit_chance modifier
would not reproduce the wiki's stack/removal rules, so it was not applied.
No invented ability definitions were added.

To author the pilots, the missing pieces are the Buff JSON path/trigger
graph (uffParams, groups, BuffTriggerFactory) and a stat enum for
Evade/Shield/Bleed. These are static-code gaps, not wiki-number gaps.
