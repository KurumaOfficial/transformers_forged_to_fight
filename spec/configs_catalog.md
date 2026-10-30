# Config catalog: `missionsconfig.configs` (Step 1.1)

Status: **partial but evidence-based.** The client accepts a dictionary of
config modes; only the modes below have confirmed consumers or keys. Empty
objects are the safe default for unconfirmed modes: the client falls back to
its code defaults, and the fast smoke + 20-fight series pass with them.

## How the client reads configs

- `ConfigManager.GetConfig(string mode)` (`0x1559CEC`) returns
  `configs[mode]` or null.
- `ConfigManager.OnData` (`0x15597F8`) parses
  `missionsconfig.configs` into `Config` objects (`versionHash`, `mode`,
  `data`).
- `TuningGameplay.OnConfigChanged` (`0x14254BC`) handles the **`bcg-combat`**
  mode directly (not through `GetConfig`).
- Do not replace the outer `missionsconfig` wrapper:
  `{"missionsconfig": {"configsHash": "...", "configs": {...}}}`. Replacing it
  with the inner `configs` caused a `QuestsManager.RefreshUserBase` NRE.

## Modes

| mode | confirmed consumer | evidence | keys in our stub |
|---|---|---|---|
| `bcg-combat` | `TuningGameplay.OnConfigChanged` / `DeserializeData` | `0x14254BC`, `0x1425540`; live 300/200/111 | `armor_break`, `mana_gain`, `critTime` |
| `alliance-base` | `BaseManager.get_defaultAllianceConfig` | `GetConfig` xref `0x1736954`, slot resolves to `alliance-base` | `{}` |
| `user-base` | `BaseManager.get_defaultUserConfig` | symmetric `GetConfig` xref `0x1736960`; literal `user-base` at `0x2D7B198` | `{}` |
| `ave` | `GameUtil.IsAwayMissionsEnabled` / `AwayTeamPopupPresentation.GetRefreshTimeout` | `GetConfig` xrefs `0xA4DF68`, `0xC11348` | `{}` |
| `pve` | `QuestUtils.CheckForMissionExclusivity` | `GetConfig` xrefs `0x103FC34`, `0x10402E8` | `{}` |
| `base`, `user`, `alliance`, `ava`, `raid` | not yet confirmed | literals exist; current stub `{}` | `{}` |

The ten mode literals are in `work/il2cpp_dump/stringliteral.json`:
`user-base`, `alliance-base`, `user`, `alliance`, `base`, `pve`, `ava`, `ave`,
`raid`, `bcg-combat`.

## `bcg-combat` keys

| key | JSON type | field | code default | live | source/evidence |
|---|---|---|---:|---:|---|
| `armor_break` | float | `TuningGameplay.ArmorRatingConstant` (+0x20) | 200.0 | 200.0 | `[CLIENT]` `DeserializeData` `0x1425540`; `docs/damage_fix.md` |
| `mana_gain` | float | `TuningGameplay.ManaPerSpecial` (+0x18) | 300.0 | 300.0 | `[CLIENT]` `DeserializeData`; live probe |
| `critTime` | float | `TuningGameplay.CritRatingConstant_A` (+0x28) | 111.0 | 111.0 | `[CLIENT]` `DeserializeData`; live probe |

Other `TuningGameplay` fields are populated from their serialized prefab
defaults or other paths, not from `bcg-combat`; see `spec/tuning_values.md`.

## Why the other modes stay empty

No other key was confirmed by static code or a live diff. Guessing keys would
create silent behavior changes. The current empty objects are **not** silent
zeros in the code path: the consumers above check for a null config and use
their defaults; the observed UI/combat behavior is unchanged. If a mode is
later proven to need a key, add it with a `[CLIENT]`/`[WIKI]` default and a live
diff.

## Related: level rewards is not in `missionsconfig`

`levelrewards` is read from `LoginManager.LoginData` by
`LevelRewardsManager.Connect` (`0x12733A0`); its inner key is
**`last_awarded_level`** (resolved from the metadata slot), not `level`.
The live `_loginData` hashtable is empty at the home screen, so this field does
not reach the manager in the current flow. `docs/level_lock.md`.
