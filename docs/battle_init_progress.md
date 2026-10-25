# Battle init progress — 2026-10-25

Status: **still blocked**, but the null chain moved forward and is now much
narrower. No client patch; all changes are server data.

## 1. First NRE was not TeamData

`BattleArbiterInitState.InitPlayer` did not fail on `enemy.TeamData` or on the
arena. The live `BattleArbiter` existed, its `_state` was
`BattleArbiterInitState`, `StateMachine` was non-null, and the static
`FighterStartPositions/Rotations/ReferenceScales` arrays had count 2. The
character prefab was not loaded because `FighterData.Blueprint.ModelID` was
empty (`CharacterDB.CharacterObject` uses `get_ModelID`).

## 2. `JSONPaths.m` is the model id key

`BCGBlueprintBase.get_ModelID` (`0xC165DC`) returns
`_characterData.ModelID` (`+0x28`) when present. The parser uses the
`JSONPaths` static paths; reading those fields at runtime showed:

- `JSONPaths.m` = `"m"`
- `JSONPaths.t` = `"t"`
- the fallback at `0x2358` = `"tags"`

Adding `"m": "<model id>"` to `blueprints` and `characters` fixed the live
`_modelID` and `_mapAssetID` for both Bumblebee and Rhinox. `map_asset` was
also needed for `ModelID`/`MapAssetID` in `BCGCharacterData`.

Adding `"t"`/`"tags"` to blueprints, characters and hero-detail dictionaries
made the live `Blueprint.Tags` lists non-null (count 2 for both fighters).

## 3. Current exception: PlayerAttributes.Init

With model id and tags fixed, the stack changed from `InitPlayer`'s direct
NullReference to:

```
ArgumentNullException: Value cannot be null. Parameter name: collection
  at System.Collections.Generic.HashSet`1[T]..ctor(IEnumerable`1 collection, ...)
  at PlayerAttributes.Init(PlayerController owner, AttributeManager manager,
                           FighterData fighterData, FighterData opponentFighterData)
  at PlayerController.Init(...)
  at BattleArbiterInitState.InitPlayer(...)
```

The only `HashSet` in `PlayerAttributes` is `BlueprintTags` (`+0x40`), built at
`0xDAC198` from `[_blueprint+0xB8]`. The live `FighterData.Blueprint.Tags` for
both fighters is non-null with count 2, so either a different `PlayerAttributes`
instance is being initialized with a blueprint whose tags are null at that
instant, or the null collection is another nested initialization that the
stripped stack does not show. Confirming this needs a breakpoint/watchpoint,
which is not available without instrumentation.

## 4. What was tried

1. Live `PreFightScreen` dump via `windowStacks` (completed earlier).
2. Live `FightFlow.FightInitInfo` field-by-field dump; both fighters/blueprints
   non-null, enemy `TeamData` null (not causal).
3. Data fixes: enemy `key`, `model_id`/`m`, `map_asset`, `tags`/`t` across
   blueprints, characters and hero details. Each moved the NRE forward.
4. Live `BattleArbiter`/`FightData.Fighters` dump: both fighter blueprints have
   tags count 2; `_fighters` remain null because `InitPlayer` fails before
   `SetFighter`.

Three substantive attempts on the battle-init item are used. The next step is
instrumentation (a read-only breakpoint on `0xDAC198` and on
`HashSet..ctor`), which is outside the current no-Frida/no-patch rules.

## 5. What is proven

- `[RUN]` The prefight provider and FIGHT path work; `activate-match` is sent.
- `[RUN]` The character prefab is loaded from `ModelID`; empty `ModelID` was a
  real blocker and is fixed by `"m"`.
- `[RUN]` `tags`/`t` populate `Blueprint.Tags` (count 2).
- `[RUN]` The next failure is `PlayerAttributes.Init`'s `HashSet` collection,
  not `TeamData`, arena spawn points, camera, or a missing asset pack.
- `[RUN]` No `/matches/match-loaded` is sent yet.

Evidence: `work/battle_tags2_logcat.txt`, `work/dump_battlearbiter.py`,
`work/dump_fightflow.py`, `work/a9_initplayer.txt`, `work/a9_playerattrs*.txt`.
