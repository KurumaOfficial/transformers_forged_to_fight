# Buff / trigger schema (Step 7) - static anchors

Status: **partial; combat Buff authoring is still blocked by the missing
effect/trigger schema.** Wiki numbers alone are not enough.

## Factories `[STATIC]`

| class | RVA / fields | role |
|---|---|---|
| `BuffTriggerFactory` | `0x?`; fields `_customFactories`, `Instance`; methods `CreateBuffTrigger(BCGStatModifier)` / `ParseConditions` | builds a trigger from a stat modifier and a condition string |
| `BuffTriggerParams` | struct `Param` (object), `Buff` | trigger payload |
| `BuffGroup` | `stackable`, `active_display` | group flags from `BuffsConfig.groups` |
| `BuffsConfig` | `Dictionary<string, BuffGroup> groups` | config root |
| `Buff.Scope` | `Unknown/Global/User` | scope enum |
| `Buff.ValueType` | `Unknown/Percent/Absolute/String` | value enum |
| `BCGStatModifier` | `var`, `modSource`, `growthCurve`, `appearanceID`, `auth`, `chance`, `modifier`, `duration`, `priority`, `triggerMod` | the only authored effect unit found in the server schema |

## What is missing

- No class named `Bleed`, `Shock`, `Burn`, `Poison`, `Shield`, `Evade`,
  `PowerLock`, `ArmorBreak`, `Fury` or `PowerSteal` was found in the combat
  effect area; effects are represented as **stat modifiers + trigger
  conditions**, not one class per effect.
- `StatModifierAttributes` has no Evade/Shield/Bleed/Power Lock entries.
- The JSON path from `BCGStatModifier` to `BuffTriggerFactory` needs the
  `trigger`/condition string format and the list of allowed `var` names; it is
  not decoded yet.
- No Buff prefab/ScriptableObject table was identified in the character
  bundles (`work/bundle_inventory.json` has animation/GameObject/MonoBehaviour
  names, not buff assets).

## Consequence

The Bumblebee/Rhinox/Optimus pilot is **not authored**: a permanent
`crit_chance` stat modifier would not reproduce the wiki stack/removal rules
and would be an invented schema. `spec/ability_schema.md` keeps the wiki
numbers and the gap list.

## Next static steps

1. Disassemble `BuffTriggerFactory.CreateBuffTrigger` and
   `ParseConditions`; resolve the condition regex and the `var` switch.
2. Find all `BCGStatModifier` `var` strings and the consumer switch.
3. Search the UI/localization dump for ability effect names and map them to
   `var`/trigger pairs before adding any catalog entry.
