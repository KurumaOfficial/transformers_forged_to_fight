# Damage pipeline: zero-damage root cause and full loop (2026-10-29)

Status: **fixed for damage and post-battle return; results/rewards UI still
needs the correct async/response schema.**

## Root cause of zero damage

`PlayerAttributes.GetArmorDR` (`0xDAD7A4`):

```
armor = _armorRating.Get()
const = TuningGameplay.Instance.ArmorRatingConstant
up    = _armorUpModifier.Get()
break = _armorBreakModifier.Get()
dr = armor / (abs(armor) + const) + (up - break)
```

`TuningGameplay.ArmorRatingConstant` was **0**, so armor 50 gave
`50 / (50 + 0) = 1.0` (100% damage reduction). The enemy's hits were reduced
to 0; the player's attacks missed/never landed in that run.

The config value is loaded by `TuningGameplay.OnConfigChanged` only when
`ConfigManager` delivers a config with mode **`bcg-combat`**. The stub's
`missions_config.json` had no such config, so the serialized SafeFloat stayed
0 even though the code default is 200.

Fix (server data only): add `missionsconfig.configs["bcg-combat"]` with the
keys `TuningGameplay.DeserializeData` reads (literal JSON paths) and the code
defaults:

| TuningGameplay field | key | value |
|---|---|---:|
| `ManaPerSpecial` | `mana_gain` | 300.0 |
| `ArmorRatingConstant` | `armor_break` | 200.0 |
| `CritRatingConstant_A` | `critTime` | 111.0 |

After the config is delivered, live values are 300/200/111 (and
DefenderManaModifier 1.25, blocked 0.35, AttackChainResetTime 0.75,
EvadeMeleeSpeed 100).

## Observed damage `[RUN]`

- Player `GetDamageInflicted` with `DamageRating=0.7` and attack 115 returns
  **80.5** (`0.7 * 1.0 * 115`), and `GetDamageReceived` returns **64.4**
  against armor 50 (DR 0.2): `80.5 * (1 - 0.2)`.
- `HitResultData`: `Flags=129` (Hit + LastHit), `AttackLevel=1`,
  `DamageRating=0.7`, `Damage=64.4`, `IsDeathBlow=1` in the KO hit.
- A normal attack run reduced the enemy from 1050 to 124.25 HP (11.8%).
- With `work/weak_enemy.flag` (server test-only HP=1), one hit killed the
  enemy: player HP 1033.6, enemy HP 0, `results={"result":"WON"}`.

## Post-battle loop `[RUN]`

Both outcomes reached `/matches/resolve-match/quests_fight`:

- LOSS: player HP 0, enemy HP 1050, `enemyHealth=1`, K.O. screen, return to
  map 22%.
- WIN: player HP 1033.6, enemy HP 0, `enemyHealth=0`, return to map.
- Evidence: `docs/evidence/post_battle_2026-10-29/`, `work/dmg1.png`,
  `work/ko2.png`, `work/winA.png`, `work/winB.png`.

The current `match_resolve_response.json` does not mark the battle tile
cleared or show rewards. The client returned to the map, but the map still
shows 22% and the boss node. The response needs the real quest progression /
results / async payload; see `docs/post_battle_quests.md`.

## Correction to the earlier safe-value claim

The earlier claim that `_attack.Get()` returned 0 was **wrong**: IL2CPP
arrays store their elements inline at `+0x20`, not behind a pointer at
`+0x20`. Reading the bytes correctly gives `_attack.Get()=115`, hash OK.
The zero was entirely in `GetDamageReceived` via
`ArmorRatingConstant=0`.

## Test-only switch

`work/weak_enemy.flag` makes server-generated enemy details HP/attack = 1;
it is evaluated at server import and is **off** unless the file exists.
Remove the file for normal tests. This is a harness switch, not client data.
