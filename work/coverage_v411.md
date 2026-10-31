
## 2026-10-30 v4.11

- **Damage/config:** `ArmorRatingConstant` +0x20 from
  `missionsconfig.configs["bcg-combat"]` (`armor_break`/`mana_gain`/
  `critTime`); `docs/damage_fix.md`, `spec/configs_catalog.md`.
- **Tuning:** 242 live fields, 95 zero/empty; only `bcg-combat` is
  server-controllable. `spec/tuning_zero_audit.md`.
- **Post-battle:** a `battlecomplete` action shows the VICTORY screen;
  rewards/tile/progress are not applied. `docs/post_battle_flow.md`.
- **Level:** `/levelrewards/fetch` requested after async `sync`; status stays
  0; `_loginData` empty. `docs/level_lock.md`.
- **Stats:** catalog/battle use wiki HP/ATK and exact 1/1 rating; Bumblebee
  DOTM 1066/97, Sideswipe 5160/520, Windblade 5160/498/1381, Rhinox
  5940/396/1413. `docs/stat_ui_check.md`.
- **Starscream:** found in `characters/toc.txt` and
  `characters.assetbundle`; catalog patch added; BOTS grid not shown.
  `docs/starscream_search.md`.
- **Abilities:** blocked by missing Evade/Shield/Bleed stat enum and
  Buff/trigger schema. `spec/ability_schema.md`.
- **Tests:** 20/20 pre-stats (1 WON/19 LOST); final normal battle step
  COMPLETED/LOST; BOTS 59/59 metric invalid (horizontal swipe repeats page 0).
