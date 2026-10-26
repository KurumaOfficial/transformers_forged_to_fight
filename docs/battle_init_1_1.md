# PlayerAttributes.Init NRE — 1.1 static analysis (2026-10-26)

Status: **cause narrowed, exact instance still not caught.** No client patch;
all observations are read-only memory dumps or static disassembly.

## 1.1a `_blueprint` type and offset

`[STATIC]` `PlayerAttributes` (`dump.cs`, TypeDefIndex 8940):

| field | offset | type |
|---|---:|---|
| `_blueprint` | `0x48` | `BCGBlueprintBase` |
| `_baseAttributes` | `0x50` | `BCGAttributeData` |
| `_attributes` | `0x58` | `BCGAttributeData` |
| `_critChanceModifier` | `0xB8` | `StatAttribute` |

`PlayerAttributes` itself also has a field at `0xB8`, but it is
`_critChanceModifier`, **not** `Tags`. The `0xB8` in the failing instruction is
`BCGBlueprintBase.Tags` (`List<string>`, `dump.cs` TypeDefIndex 8313). The
claim "`[_blueprint+0xB8]` is Tags" was therefore correct, but the earlier
live-dump target was wrong: it checked `FighterData.Blueprint.Tags`, not the
blueprint of the instance that threw.

## 1.1b Where `_blueprint` comes from

`[STATIC]` `PlayerAttributes.Init` (`0xDAB16C`):

```
0xDAB4D8  str x22, [x19, #0x28]   ; Owner = owner
0xDAB4E0  ldr x8,  [x23, #0x30]   ; fighterData.BaseAttributes
0xDAB4E4  str x8,  [x19, #0x50]
0xDAB4E8  ldr x8,  [x23, #0x38]   ; fighterData.Attributes
0xDAB4EC  str x8,  [x19, #0x58]
0xDAB4F0  ldr x8,  [x23, #0x40]   ; fighterData.Blueprint
0xDAB4F4  str x8,  [x19, #0x48]   ; _blueprint
```

So `_blueprint == fighterData.Blueprint`. The chain is:

```
HeroData.mBlueprint (+0x48)
  -> FighterData.Blueprint (+0x40)      [PrefightScreenData.OnFight, 0xE3ED08]
  -> PlayerAttributes._blueprint (+0x48) [PlayerAttributes.Init]
  -> Tags (+0xB8) -> HashSet<string>     [0xDAC198]
```

`HeroData` gets `mBlueprint` from `BCGManager.Instance`'s blueprint dictionary
(`HeroData..ctor`, `0xE8A6F0..0xE8A720`, `Dictionary.TryGetValue`). A failed
lookup leaves the field null; it does not create a default blueprint.

## 1.1c All collection constructors in Init

`[STATIC]` direct calls in `0xDAB16C..0xDAC278`:

- `0xDAC198` — `new HashSet<string>(_blueprint.Tags)`.
  The called stub is `0x12A9D94` (`HashSet<string>..ctor(IEnumerable<string>)`),
  which tail-branches to the two-argument implementation `0x12A9DFC`.
- `0xDAC238` — **the actual failing path**: `DamageType..ctor` is called with
  `_blueprint.BaseRangedDamageType`. `DamageType..ctor` (`0xBB0B70`) itself
  tail-branches to `0x12A9D94` with that list. Because the caller is a tail
  call, the `DamageType..ctor` frame disappears and the managed stack shows
  `HashSet..ctor <- PlayerAttributes.Init`. `BaseRangedDamageType` was null
  for both fighters in the live dump.
- `0xDAC1C8` — `DamageTypeTable..ctor` (object creation, no collection from a
  list).
- `0xDAC238` — `DamageType..ctor`; its own constructor tail-calls
  `HashSet<T>..ctor(IEqualityComparer<T>)` (`0x12A9CD0`), which does **not**
  take an `IEnumerable` and cannot throw `ArgumentNullException("collection")`.
- `0xC9960C` / `0xC99938` — `AttributeManager.CreateStatAttributes` /
  `CreateResourceAttributes`; these build `Dictionary`/`List` objects and
  `StatAttribute`/`ResourceAttribute` instances, no `HashSet(IEnumerable)`.
- `0xE2FC8C` — `ResourceAttribute.Init`; no `HashSet(IEnumerable)`.
- `0xDAC27C` / `0xDAC3FC` — `GetStatAttribute` / `GetResourceAttribute`;
  dictionary lookups only.

Indirect calls: `0xDABB3C` and `0xDABBF8` are `blr` interface dispatches used
by `BCGBlueprintBase.IsIdealContender` / `BCGManager` buff lookups. They occur
**after** the HashSet construction and are not collection constructors.

Binary-wide scan for the exact ctor stub `0x12A9D94` found only two callers:
`StatModifierTypeGroup.StartMatch` and `PlayerAttributes.Init`. Since the
managed stack names `PlayerAttributes.Init`, the null collection is its
`_blueprint.Tags`.

## 1.1d Full managed stack

`[RUN]` `adb logcat -d -v long -s Unity:V` (2026-10-26 17:11:13.667,
PID 4675):

```
ArgumentNullException: Value cannot be null.
Parameter name: collection
  at System.Collections.Generic.HashSet`1[T]..ctor (IEnumerable`1[T] collection,
      IEqualityComparer`1[T] comparer)
  at PlayerAttributes.Init (PlayerController owner, AttributeManager manager,
      FighterData fighterData, FighterData opponentFighterData)
  at PlayerController.Init (BattleArbiter battleArbiter, Int32 id,
      FighterData fighterData, FighterData opponentFighterData, TowerData towerData)
  at BattleArbiterInitState.InitPlayer (Int32 id, GameObject player, Boolean isPlayer,
      Boolean mirror, FighterData fighterData, FighterData opponentFighterData,
      TowerData towerData)
  at BattleArbiterInitState+<>c__DisplayClass9_0.<InitCharacter>b__0 (Unity...
```

The Unity log line is truncated at 400 characters; no further BCL frames exist
above the HashSet frame. The two-argument signature is the tail-called
implementation of the one-argument constructor, which confirms
`collection == null` rather than a comparer problem.

## 1.1e Live dump contradiction

`[RUN]` `work/probe_fightdata.py` after the exception:

| fighter | FighterData | Blueprint | Tags |
|---|---|---|---|
| player | `0x7877a88ace00` | `0x7878df8acc60` `TFBCGBlueprintBase` | `List<string>` size **2**: `scout`, `autobot` |
| enemy | `0x7877a88acd90` | `0x7877ae879120` `TFBCGBlueprintBase` | `List<string>` size **2**: `scout`, `autobot` |

`[RUN]` `BattleArbiter.FightData.Fighters` points to the same two objects
(`0x7877a8944000`, `Fighters` array `0x7877a8895c80`). `_state` is still
`BattleArbiterInitState`; its `_fightData` is the same `FightData`.
`_fighters` is `PlayerController[2]` with both entries null.

`[RUN]` Heap scan (`work/scan_playerattrs.py`, class pointer
`0x787e1b478bd0`) found two live `PlayerAttributes` instances:

| object | Owner | `_blueprint` | Tags | other |
|---|---|---|---|---|
| `0x7877a88c7d80` | `0x7877a8889000` `PlayerController` | `0x7878df8acc60` Bumblebee | size 2 | health/mana/attack non-null |
| `0x7877a8889480` | null | `0x7877aee3e800` **plain `BCGBlueprintBase`** | **null** | default base/attributes; health/mana/attack null |

`[STATIC]` `PlayerAttributes..ctor` (`0xDAEAD0`) creates the second object's
state: a default `BCGBlueprintBase` (empty strings, `MaxRank=1`, all
collections null) and two default `BCGAttributeData` objects. The default
instance was therefore **not initialized by `Init`** (Owner is still null),
i.e. it is a fresh component, not the throwing one.

The throwing instance is no longer present in the scanned heap: Unity destroyed
the failed character object after the exception. The postmortem contradiction
is resolved as follows: the live `FightData.Fighters` are **not** the objects
that threw. A second `PlayerController` exists (`0x7877a8889240`) whose
attributes are the default component; the failed one was a transient object.

## 1.1f Root cause found (2026-10-26 18:2x)

The null collection is **`Blueprint.BaseRangedDamageType`**, not `Tags`.
`DamageType..ctor(List<string>)` tail-calls `HashSet<string>..ctor(collection)`;
a null list throws `ArgumentNullException("collection")` with
`PlayerAttributes.Init` as the visible parent frame. The earlier postmortem
contradiction is fully resolved: `Tags` was always non-null; the failing list
was `BaseRangedDamageType`, which the live dumps showed as `None` for both
fighters.

Fix applied in `server/data/bcg_login_data.json`:

- every `blueprints` and `characters` entry now has
  `base_damage` / `base_ranged_damage` (and the `baseRangedDamageType` alias);
- a `bumblebee_cin_dotm` blueprint alias was added because
  `HeroData.Create` logs `blueprint 'bumblebee_cin_dotm' does not exist`.

`[RUN]` after the fix: no `ArgumentNullException`; the battle reaches
`BattleArbiterMainState`, `_fighters[2]` is populated, the player is in
`PlayerHitReactState` and the enemy in `PlayerAttackState` /
`PlayerNewHeavyAttackState`. See `docs/battle_started.md`.

Remaining: the player stays at 1.0 HP and the hit-react loop does not finish
(the next blocker, not the init NRE).

## Evidence files

- `work/a9_attrs_init.txt` — full `PlayerAttributes.Init` disassembly.
- `work/a9_full_stack.txt` — logcat capture.
- `work/probe_fightdata.py` — FightData/Fighters tags dump.
- `work/scan_playerattrs.py` — heap scan for `PlayerAttributes`.
- `work/scan_playercontrollers.py` — heap scan for `PlayerController`.
- `work/a9_state.png` — screen state after the failure.
