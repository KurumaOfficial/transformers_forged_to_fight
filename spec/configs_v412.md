# `missionsconfig.configs` beyond `bcg-combat` (Step 8)

Status: **only `bcg-combat` has confirmed keys.** The other modes are present
as empty objects; their consumers check for null/empty and fall back to code
defaults. Filling guessed keys would be a silent behavior change.

## Confirmed

| mode | consumer | evidence | keys |
|---|---|---|---|
| `bcg-combat` | `TuningGameplay.OnConfigChanged` / `DeserializeData` | `0x14254BC`, `0x1425540`; live 300/200/111 | `armor_break`, `mana_gain`, `critTime` |

`spec/configs_catalog.md` has the full table and the outer `missionsconfig`
wrapper requirement.

## Consumers found, keys not decoded

| mode | consumer | what it likely controls | state |
|---|---|---|---|
| `user-base` | `BaseManager.get_defaultUserConfig` | user base building defaults | empty; no key confirmed |
| `alliance-base` | `BaseManager.get_defaultAllianceConfig` | alliance base defaults | empty |
| `ave` | `GameUtil.IsAwayMissionsEnabled`, `AwayTeamPopupPresentation.GetRefreshTimeout` | away missions/refresh | empty; AWAY is not in the FIGHT list |
| `pve` | `QuestUtils.CheckForMissionExclusivity` | PvE mission scaling/XP/rewards/energy | empty; keys not decoded |
| `user`, `alliance`, `base`, `ava`, `raid` | literals only | unknown | empty |

## Why not fill them

- No default value is exposed by the client code for these modes; the
  deserializers read `Dot` from a config dictionary that is absent.
- The `pve` consumer is a mission-exclusivity check, not a full scaling table;
  assuming it holds XP/reward keys would be invention.
- The 20-fight normal series and full smoke pass with these empty objects, so
  they are safe null fallbacks, not silent zeros in `bcg-combat`.

## Next static step

Disassemble `QuestUtils.CheckForMissionExclusivity` (`0x103FC34`) and
`BaseManager.get_defaultUserConfig` / `get_defaultAllianceConfig`
(`0x17369E0` / `0x1736954`) to resolve the actual `Dot` keys. Until then, keep
the modes empty and documented.
