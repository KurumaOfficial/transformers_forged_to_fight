# Tuning zero audit (Step 1.2)

Status: **static/live audit, no blind filling.** The complete live dump is
`spec/tuning_live.md` (242 fields, 95 zero/empty). Most zeros are intentional
feature flags or UI anchors. Only server-controllable `bcg-combat` keys are
safe to fill; other `Tuning` fields come from the client prefab, not from
`missionsconfig`.

## Method

- `Tuning.Instance` is read live through `0x2BC9268`; `work/dump_tuning_live.py`
  parses all 242 fields from `dump.cs` and reads their current values.
- `TuningGameplay` is read through `0x2BE0348`; known values are in
  `spec/tuning_values.md`.
- A zero is not a bug by itself. The table below lists fields whose name
  indicates battle/AI/quest/energy/reward/XP/UI use and whose zero can change
  behavior.

## Functional candidates

| field | type/offset | live | what a zero can break | source / safe value |
|---|---|---:|---|---|
| `AwayTeamSuccessPercentTier0` | float 0x58 | 0 | If the away-mission success roll uses this tier, success is 0%. AWAY MISSIONS is not in the current FIGHT list, so not observed. | Wiki away-mission table; not confirmed. Leave 0, `[ASSUMED]` only. |
| `ClassDisadvantageSelectionBias` | float 0x104 | 0 | AI opponent class selection bias; 0 means no bias, which is a valid value, not a missing default. | `[CLIENT]` live; no change. |
| `StartingArenaTOD` | int 0x168 | 0 | Arena starting time-of-day; ARENAS is locked at this account state. | `[ASSUMED]`; do not change while arena is locked. |
| `BaseRelicYPosition` | float 0x32C | 0 | Base relic UI anchor; a zero may place the relic at the origin. No NRE observed. | `[CLIENT]` prefab; UI-only. |
| `QuestRelicYPosition` | float 0x338 | 0 | Quest relic UI anchor; UI-only. | `[CLIENT]` prefab. |
| `HideCrystalsIfEmpty` | bool 0x219 | false | CRYSTALS tab stays visible with `No crystals available`; this matches the live screen. | `[CLIENT]`; intentional. |
| `LimitGachaPerDay` | bool 0x228 | false | No daily gacha limit; gacha is not implemented. | `[CLIENT]`; leave false. |
| `GachaLimitTimezoneOffset` | int 0x22C | 0 | Only relevant if `LimitGachaPerDay` is true. | `[CLIENT]`; leave 0. |
| `CurrencyShowLevels` | array 0x390 | empty | Top bar shows all currencies; empty means no level gate. Observed UI matches. | `[CLIENT]`; no change. |
| `ODRForceDownloadAll` | bool 0x360 | false | ODR does not force a download; bundle exists. | `[CLIENT]`; leave false. |
| `MeleeRangeMod` (`TuningGameplay`) | SafeFloat 0x50 | 0 | No melee range modifier; combat works. | `[CLIENT]`; leave 0. |
| `MinVisibleHitStreak` (`TuningGameplay`) | int 0x88 | unknown | Hit-streak UI threshold; not read live yet. | `[CLIENT]` prefab; not server. |

## `TuningGameplay` zeros / unknowns

Live known values: 300/200/111, DefenderMana 1.25, blocked 0.35, chain reset
0.75, evade 100, melee range 0. The other fields (knockback, gravity,
projectile speeds, curves, tutorial triggers, colors) are prefab values; they
are not read from `bcg-combat` and must not be invented in server JSON.

## Server-controllable keys

Only `missionsconfig.configs["bcg-combat"]` is confirmed server data:
`armor_break`, `mana_gain`, `critTime`. All three are nonzero in the live
client. `spec/configs_catalog.md`. Other config modes are empty and the
consumers fall back to code defaults; the 20-fight series and full smoke pass
with that state.

## Verification

- `[RUN]` `work/dump_tuning_live.py`: 242 fields, 95 zero/empty, instance
  present.
- `[RUN]` `work/probe_tuning_gameplay.py`: 300/200/111/1.25/0.35/0.75/100/0.
- `[RUN]` 20/20 battle series and 6/6 full smoke with the current config.
