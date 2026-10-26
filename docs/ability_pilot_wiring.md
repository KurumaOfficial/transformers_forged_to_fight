# Ability pilot wiring (4.1–4.5) — status

## What is proven

- `[STATIC]` `statMods` is a catalog key (`bcg_login_data.statMods`); the
  verified sample is `stat_mod_attack_pct` with `id`, `var`, `modSource`,
  `growthTarget`, `growthCurve`, `ratingCurve`, `appearanceID`, `auth`,
  `growthConst`, `stackable`, `tier`, `heroRatingHP`, `heroRatingAttack`,
  `chance`, `modifier`, `duration`, `priority`, `triggerMod`.
- `[STATIC]` `statModAppears` supplies localization keys, not display text:
  `ability_title_id`, `short_string_id`, `long_string_id`, `simple_string_id`,
  `icon_texture`, `fx_profile`, callout colors/texts.
- `[STATIC]` `Buff` fields: `tintColour`, `id`, `iconTexture`, `_imagePath`,
  `modesAvail`, `scope`, `valueStr`, `_valueType`, `_localizedName`,
  `_localizedDesc`, `buffType`, `buffParams`, `group`; `BuffGroup` has
  `stackable`/`active_display`; `BuffsConfig` has `groups`.
- `[RUN]` The details screen shows `M1_SPECIAL_ATTACK_<BOT>.<n>`; a scan of
  `work/unpacked/assets` found no such localization key. The client is showing
  a **move/animation id**, not a missing localization string.

## Pilot data

`data/wiki/ability_pilot.json` contains the wiki ability text for Bumblebee,
Rhinox and Optimus Prime. It is `[WIKI]` source data only. It has **not** been
wired into `statMods` because the wiki text does not carry stable client
`statMod` ids, trigger enum values, or effect factories. Guessing those ids
would make the battle screen lie.

## Why wiring is blocked

- No per-bot `statMods` id table in the retained assets/localization.
- No per-bot move/ability name table; `M1_SPECIAL_ATTACK_*` is generated from
  the move set, and the move bundles are not all in the APK (ODR).
- The client accepts the existing catalog `statMods` sample without NRE, but
  the ability screen for the pilot bots is not reachable because the battle
  loading overlay (`FuseODRBlocker`) blocks the HUD.

## Synergies

`[STATIC]` The catalog has `synergyBonuses` (4 entries) and blueprints carry
`synergy_bonuses` (`syn_autobots` for Bumblebee/Sideswipe). The live screen
check is blocked by the same ODR overlay; the data shape is present and the
battle parser accepts it (live `Blueprint.SynergyBonuses` size 1).

## Next safe step

Wire only entries whose ids exist in the catalog and whose effects are
unambiguous (`stat_mod_attack_pct`-style), then verify on the bot details
screen once ODR is resolved. Keep the wiki text in
`data/wiki/ability_pilot.json` as provenance; do not synthesize ids.
