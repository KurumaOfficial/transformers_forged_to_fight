# Battle enums and string selectors (Step 1.7)

Everything below is `[STATIC]` from `dump.cs` unless marked `[RUN]`.
`data/battle_enum_audit.json` validates the current catalog/quest data;
`blueprint_bad`, `character_bad`, `quest_bad` are empty.

## Damage types

`Blueprint.BaseDamageType` / `BaseRangedDamageType` are **`List<string>`**, not
enums. The getter reads `BCGCharacterData +0x40/+0x48`; allowed strings are the
keys of `bcg_login_data.damage_types`: **`kinetic`, `energy`**. A null list
crashes `DamageType..ctor` (see `docs/battle_init_fix.md`); `[]` is safe.

## CharacterMetaData.Class (TypeDef 8404, flags)

| name | value |
|---|---:|
| none | 0 |
| braw | 1 |
| tact | 2 |
| scou | 4 |
| demo | 8 |
| warr | 16 |
| tech | 32 |
| generic | 64 |
| superior | 128 |
| basic | 256 |
| alpha | 512 |
| off | 65536 |
| def | 131072 |
| uti | 262144 |

The catalog `blueprints.class` values are **numeric flags** (`1`, `2`, `4`, ...
or sums), not names. `BCGBlueprintBase.HeroClass` at +0x68 is this enum.
`BCGAttributeData` has class modifiers at +0x80/+0x84.

## AttackLevel (TypeDef 8943, flags)

`None=0`, `Light=1`, `Medium=2`, `Heavy=4`, `Ranged=8`, `Special1=16`,
`Special2=32`, `Special3=64`, `Special=112`, `Normal=15`.
`AttackType`: `Melee=1`, `Ranged=2`.

## BuffTypeCategory (TypeDef 8382, flags)

`None=1`, `Offensive=2`, `Defensive=4`, `Utility=8`.

## TransformersFaction (TypeDef 8379, flags)

`Neutral=1`, `Autobot=2`, `Decepticon=4`, `Maximal=8`, `Predacon=16`.
Character `faction` values in the catalog are numeric (`1` = Autobot for
Bumblebee/Sideswipe); the `tags` list uses `autobot`/`decepticon` strings.

## CharacterMetaData.StatModifierAttributes (TypeDef 8405)

`None=0`, `HP=1`, `Attack=2`, `Mana=3`, `ManaGain=4`, `BlockProficiency=5`,
`PerfectBlockChance=6`, `MaxHP=7`, `CritChance=8`, `CritDamage=9`,
`StunChance=10`, `Armor=11` (the enum continues in `dump.cs`; these are the
combat-relevant first eleven).

## AI selectors

`TuningAI` (TypeDef 9464) has `Profiles` (`AIProfile[]`), `DefaultProfile`,
`Personalities` (`AIPersonality[]`), `DefaultPersonality`.
- `GetAIProfile(string profileName)` 0x14242E4 does a name lookup; unknown/null
  returns the default profile (`TuningAI.GetAIProfileByIndex` logs and returns
  Default).
- `GetAIPersonality(string personalityName, bool allowNull=false)` 0x142456C.
- `AIProfile` (TypeDef 8616) and `AIPersonality` (TypeDef 8615) are
  ScriptableObjects; `AIProfile._statMods`/`AIPersonality._statMods` are
  `List<string>` and have the same null-list risk as damage types.
- Default behavior tree path: **`Gameplay/AIBehavior/AIBehavior-Default`**
  (`AIController.kAIBehaviorTreePath`).
- The `FighterData` fields are `AIProfile` (+0x50) and
  `OverrideAIPersonality` (+0x58). The server `scaledBossTable.enemy1` fields
  are `aiType`, `aiString`, `aiPer`; `aiType` is not the profile name.
  `aiString`/`aiPer` are the string selectors. `FinalizeFightResults` logs and
  falls back if either is null.

`[RUN]` For `story_act1_ch4_m2` the live enemy `FighterData.AIProfile` and
`AIPersonality` were non-null; the player `AIProfile` was non-null and
`AIPersonality` null (human-controlled). The quest data used
`aiString="default"`, `aiPer="aggressive"`, `aiType=1`; no fallback warning
appeared.

## Entity selectors

`Entity.type`/`baseType`/`key` are strings at +0x20/+0x28/+0x30.
`BCGEntity` extends `QuestBoss`; `QuestBoss.character` is `Entity.key`.
The current quest `scaledBossTable.enemy1` uses `type="boss"`,
`baseType="boss"`, `key=<blueprint id>`. Valid `key` must be a **blueprint**
id, not a character id (`bumblebee_cin_dotm` was fixed to
`bumblebee_cin_dotm_2`).

## Data audit

`work/audit_battle_enums.py` checks:
- blueprint/character damage lists against `damage_types`;
- blueprint class values (numeric or name);
- character faction/subgroup/generation/ai_personality;
- quest `aiString`/`aiPer`/`type`/`baseType`.

Result: **0 bad values** in the current catalog and 90 quests. Numeric class
values are valid flags; do not turn them into names.

## Open

- Exact `AIProfile`/`AIPersonality` asset names are inside the `TuningAI`
  ScriptableObject, not string literals; a live/asset dump is needed to list
  all profiles beyond `default`/`aggressive`.
- The `aiType` integer semantics are not decoded; use `aiString`/`aiPer`.
