# Ability pilot: why the wiki text is not wired yet

Status: **blocked** for 5.1 (pilot definitions) and 5.2 (wiki->definition
converter). 5.3 (special-attack localization key builder) is done in
`docs/special_attack_localization.md`.

## What the client actually accepts

There is no `Ability` class. A bot ability is composed from:

- `statMods` entries (`BCGStatModifier`, TypeDef 8306), keyed by an id and
  attached to a hero by `auth: [blueprint ids]`;
- `Buff`/`BuffGroup` definitions for shields, bleed, shock, power lock, etc.;
- `attackValues` for basic/special damage.

`BCGStatModifier` fields [STATIC]:

`ID`, `Type`, `TypeMod`, `Trigger`, `UITrigger`, `TriggerModStr`,
`TriggerRate` (`BuffTriggerRate`), `Stat`
(`CharacterMetaData.StatModifierAttributes`), `Target` (`BuffTargetTypes`),
`ModType` (`BuffModTypes`), `Var`, `ModSource`, `GrowthTarget`,
`GrowthCurve`, `RatingCurve`, `AppearanceID`, `Auth`, `GrowthConst`,
`Stackable`, `Tier`, `HeroRatingHP`, `HeroRatingAttack`, `Chance`,
`Modifier`, `Duration`, `Priority`, `TriggerMod`.

Useful enums [STATIC]:

- `StatModifierAttributes`: None, HP, Attack, Mana, ManaGain, BlockProficiency,
  PerfectBlockChance, MaxHP, CritChance, CritDamage, StunChance, Armor.
- `BuffModTypes`: none, buff, debuff, passive, passive_buff, passive_debuff.
- `BuffTargetTypes`: none, self, opponent, owner, tower, opp_tower.
- `BuffTriggerRate`: none, update, once, repeat.
- `BuffTriggerConstants`: `onStart`, `onPreStart`, `onAbilityActivate`,
  `onAbilityExpiry`, `onTypeActivate`, `onTypeExpiry`, `onBuffImmune`.

## Why the wiki text is not enough

The wiki describes **outcomes**, not the client's `statMod` id/trigger graph:

- Bumblebee: melee evade, stacking crit-rate buffs removed on hit, shield
  break + shock. This needs `Buff`/trigger definitions, not one stat mod.
- Rhinox: 6 shield buffs, recharge timer, burn/shock resistance, bleed on
  chaingun, power drain/lock. There is no `burn_resist`/`shock_resist` value
  in `StatModifierAttributes`; it must be a `Buff`/damage-type resistance.
- Optimus Prime: armor/melee/willpower buffs; the exact trigger and stacking
  rules are not in the wiki text.

The client's `statMods`/`Buff` ids are **server catalog data** (the original
Kabam server sent them in `/bcg/getLoginData`). They are not in the APK
assets or metadata; only the schema and generic localization keys remain.
Inventing ids/triggers would create plausible-looking but false behavior, so
the pilot stays `[WIKI]`-only.

## What was checked

- `data/wiki/ability_pilot.json`: Bumblebee/Rhinox/Optimus text and rank
  tables (`[WIKI]`).
- `server/data/bcg_login_data.json`: `statMods` has one placeholder
  (`stat_mod_attack_pct`), no per-bot ability definitions.
- `work/unpacked/assets`: no per-bot ability/stat-mod table.
- `global-metadata.dat` / `dump.cs`: schema and enums above; no values.
- `spec/ability_schema.md`: verified fields/RVAs.

## What would unblock it

1. A capture of the original `/bcg/getLoginData` `statMods`/`buf`/`attackValues`
   tables (or a later APK/server dump that includes them).
2. Or a deterministic inference pipeline: map each wiki effect to a
   `BCGStatModifier`/`Buff` with a **proven** trigger/stat/var from the client
   code, and validate on the bot details/battle screen.
3. For special-attack names: the original per-bot move-name/loc table; the
   builder is known (`BCGHelper.GetSpecialAttackNameLocString` `0xC1B154`,
   description `0xC1B21C`), the keys are absent.

Until then, the honest state is: schema known, data missing, no invented
abilities.

## 2026-10-29 correction: keys exist

`work/localization_all.json` contains 3307 `ID_STAT_*` keys, 8 `D_STAT*`
keys and 390 `ID_SPECIAL_ATTACK_*` keys (65 bot/move tokens). They are
**localization keys**, not the numeric `statMods`/`Buff` definitions.
Rhinox has the strongest key coverage (31 keys); Bumblebee has no
`ID_STAT_BUMBLEE_*` ability keys; Windblade has no special-attack keys.
`spec/buff_catalog.md` now lists the families, bot tokens and effect-token
matches. The pilot stays blocked on numeric definitions/triggers, not on the
absence of keys.
