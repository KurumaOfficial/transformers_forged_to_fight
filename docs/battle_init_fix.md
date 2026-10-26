# BaseRangedDamageType NRE — fix record (Step 0.1)

## What was wrong

`[STATIC]` `PlayerAttributes.Init` at `0xDAC238` calls
`DamageType..ctor(blueprint.BaseRangedDamageType)`. `DamageType..ctor`
(`0xBB0B70`) tail-branches to `HashSet<string>..ctor` (`0x12A9D94`), so the
`DamageType` frame disappears from the managed stack and the exception appears
as `HashSet..ctor <- PlayerAttributes.Init`. The null was **not** `Tags`
(`0xDAC198`); it was `BaseRangedDamageType`.

| item | value |
|---|---|
| field on blueprint | `BCGBlueprintBase._baseRangedDamageType` / property `BaseRangedDamageType` |
| blueprint offset | `0xB8` is `Tags`; `BaseRangedDamageType` is **not** used directly by the getter |
| getter | `BCGBlueprintBase.get_BaseRangedDamageType` `0xC169E4` |
| getter source | `_characterData` (+0x18); falls back to `BCGManager.Instance.CharacterData[Character]` (0x0A5C688, dict at +0x58) |
| returned field | `BCGCharacterData.BaseRangedDamageType` **+0x48** (TypeDef 8314) |
| character list field | `BCGCharacterData.BaseDamageType` +0x40 |
| failing ctor | `DamageType..ctor` `0xBB0B70` -> `HashSet<string>..ctor` `0x12A9D94` |
| call site | `PlayerAttributes.Init` `0xDAC238` |

The field is a `List<string>`, **not an enum**. Allowed values are the keys in
`bcg_login_data.damage_types`: `kinetic`, `energy` (the catalog also has
`name`). The parser uses string lists, so a null list is fatal; an empty list
is safe. The corrected data uses `["energy"]` for ranged and the existing
melee value for `base_damage`.

## Why the earlier Tag hypothesis was wrong

`[RUN]` live `FightData.Fighters` after the crash had `Blueprint.Tags` size 2
for both fighters, while `BaseRangedDamageType` was `None`. The heap scan
found one initialized Bumblebee `PlayerAttributes` (Tags 2) and one default
uninitialized component; the throwing instance was the enemy, whose
`BaseRangedDamageType` was null. The visible stack only showed `HashSet..ctor`
because `DamageType..ctor` is a tail call.

## Data changes

- `[RUN]` `server/data/bcg_login_data.json`: every `characters` entry now has
  `base_damage` and `base_ranged_damage` (the getter reads the character list);
  every `blueprints` entry also has the same keys for completeness and
  `baseRangedDamageType` alias.
- `[RUN]` Added a `bumblebee_cin_dotm` blueprint alias with the same fields as
  `bumblebee_cin_dotm_2`, because `HeroData.Create` logged
  `blueprint 'bumblebee_cin_dotm' does not exist in BCG data`.
- `[STATIC]` `base_damage` is the melee list; `base_ranged_damage` is the
  ranged list. Both are `List<string>`; empty is allowed, null is not.

## Evidence

### Before

`work/stop_probe.txt` (2.5–3.0 s after activate-match):

```
player fighter: ... Blueprint = TFBCGBlueprintBase
  BaseDamageType ptr=... List`1 size=1 ['energy']
  BaseRangedDamageType ptr=None class=None
```

`work/stop_logcat.txt` / `work/a9_full_stack.txt`:

```
ArgumentNullException: Value cannot be null.
Parameter name: collection
  at System.Collections.Generic.HashSet`1[T]..ctor (IEnumerable`1 collection, ...)
  at PlayerAttributes.Init (...)
  at PlayerController.Init (...)
  at BattleArbiterInitState.InitPlayer (...)
```

### After

`[RUN]` no `ArgumentNullException` in the 18:14–18:35 logcat;
`BattleArbiter._state = BattleArbiterMainState`; `_fighters` length 2; player
`PlayerHitReactState`, enemy `PlayerAttackState`/`PlayerNewHeavyAttackState`.
See `docs/evidence/battle_init/mainstate.txt` and
`docs/evidence/battle_init/logcat_after.txt`.

### Live character list after fix

The getter reads `BCGCharacterData + 0x48`; the blueprint's own `+0x98` may
remain null and is not consulted when `_characterData` is present. The fix is
in the **character** entry, which is why adding only blueprint keys did not
stop the NRE in the first attempt.

## Requests

`[RUN]` `server/requests.jsonl` has the activate request:

```
POST /matches/activate-match/quests_fight
{"hero":"bumblebee_cin_dotm_2","qid":"story_act1_ch4_m2","battleId":"battle1"}
```

No `/matches/match-loaded` line exists, so the client never sent it and there
is no response to show. See `docs/evidence/battle_init/requests.txt`.

## Next blocker

The ODR blocker/loading state, not this NRE. See `docs/odr_flow.md` and
`docs/battle_started.md`.
