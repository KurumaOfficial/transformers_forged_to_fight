# Prefight flow — provider registration and the null model

Status 2026-10-24. All addresses are RVAs in `libil2cpp.so` 9.2.0.
No Frida/gadget/patch was used.

## 1. The decisive registry snapshot

`InterfaceInjector` is initialized in `LoginManager._PostInit` ->
`InitializeGameData` (`0xFC5F3C`) -> `InitializeDefaultData` (`0xFC5FDC`).
It scans all `[InjectorClass]` classes into
`Dictionary<Type, List<Tuple<string, Type>>>`.

Live probe `work/dump_injector_names.py` resolved the 78 entries using the
`Il2CppTypeDefinition.nameIndex` -> `global-metadata.dat` string table:

| Index | Interface | Implementations |
|---|---|---|
| 0 | `EB.Ads.IAdsProvider` | `tform -> TFormIronSourceAdsModel`, `default -> IronSourceAdsModel` |
| 1..68, 70..77 | 77 other interfaces | `default` only |
| **69** | **`IPrefightDataProvider`** | **`default -> PrefightScreenData` only** |

Live `_currentTag` = `"tform"`. `_gameInterfaces` count = 78.
`_persistentInterfaces` = 1 (`IAdsProvider -> TFormIronSourceAdsModel`).

`PrefightScreenData` is the **only** class implementing
`IPrefightDataProvider` (dump.cs TypeDefIndex 11323). There is no second
story/arena/PvP variant.

## 2. `Get<T>` semantics (0x11E7640)

The generic `Get<T>` does:

1. `Type.GetTypeFromHandle(typeof(T))` (MethodInfo type handle);
2. `Dictionary.ContainsKey(type)` on `_gameInterfaces`
   (`0x1FFD7C8`, called at `0x11E7860`);
3. get the list (`Dictionary.get_Item`, `0x1FFD490`);
4. iterate the tuples:
   - compare `tuple.tag` with `_currentTag` (`[static+8]`, `0x11E7950`);
   - if no match, compare `tuple.tag` with the literal `"default"`
     (`0x11E7988`);
   - on a match load `tuple.implementationType` (`0x11E79DC`);
5. `Activator.CreateInstance(type)` (`0x11E79E8`);
6. return the new instance.

So there **is** a `default` fallback. If entry 69 is reached, it should
create `PrefightScreenData` even under `tform`. The observed null therefore
means one of:

- `ContainsKey(typeof(T))` is false (generic type identity mismatch between
  the call-site `T` and the type-definition key), or
- the call site is not `Get<IPrefightDataProvider>` (wrong interface), or
- `Activator.CreateInstance` returned null / threw and the caller stored null.

The call-site method-info slot is `0x2BE2870`; its runtime value is a
generic-method structure, not a direct `Type` pointer. Resolving its exact
generic argument is the next static step (A1 follow-up).

## 3. Sequence

```mermaid
sequenceDiagram
    participant LM as LoginManager
    participant II as InterfaceInjector
    participant GB as Gameboard
    participant AB as Action_Battle
    participant PS as PreFightScreen
    participant PD as PrefightScreenData

    LM->>II: InitializeGameData (0xFC5F3C)
    II->>II: scan [InjectorClass] (78 entries)
    Note over II: IPrefightDataProvider -> default/PrefightScreenData<br/>IAdsProvider -> tform+default
    Note over II: _currentTag = "tform"
    GB->>AB: battle action result
    AB->>AB: HideAllNodeCards, MoveTo, dialogue/wait
    AB->>GB: OpenPreFightScreen (0xA550A0)
    GB->>PS: WindowManager.Open("PreFightScreen")
    PS->>PS: SetupWindow -> CacheReferences (0xE38E4C)
    PS->>II: Get<IPrefightDataProvider> (0x11E7640)
    II-->>PS: null (observed)
    PS->>PS: _model = null (+0x98)
    Note over PS: UI still renders the empty VS shell
    PS->>PS: OnFight (0xE397BC)
    PS->>PS: ldr x20,[this+0x98]; cbz -> NRE
```

## 4. Who opens the screen (A3)

- `Gameboard.OpenPreFightScreen` (`0xA550A0`) builds
  `PreFightScreen.PreFightParams` and calls `WindowManager.Open`.
- It is called only from `Gameboard.Action_Battle..MoveNext`
  (`0xF83868`) and `Action_Ambush` (`0xF83370`).
- `OpenPreFightScreen` does **not** create `PrefightScreenData` and does not
  call `InterfaceInjector.SetInterface`; it only passes params.
- `PrefightScreenData..ctor` (`0xE3F734`) has **no direct BL call** in the
  binary (only the type/ctor metadata references), consistent with the
  injector's `Activator.CreateInstance` being the only creation path.
- Logcat before the FIGHT NRE contains no provider/Injector error at the
  default log level. One earlier warning was
  `Coroutine couldn't be started because the game object 'QuestboardHud'
  is inactive!` (16:35:21); its relation to the provider is unproven.
- The `/bugs` report contains the `PreFightScreen.OnFight` NRE stack; no
  earlier exception.

## 5. BOTS is not a working analog (A2)

`HeroesScreen` is a plain `Window`; it reads the roster through
`BCGHelper.GetHeroes` / `BCGManager.UserData.entities["bot"]`, not through
`InterfaceInjector.Get<T>`. It has no `_model` field and no provider
registration. Therefore BOTS cannot tell us why the injector returns null.

Better injector analogs, both `default`-only:

| Interface | Entry | Screen | Test |
|---|---|---|---|
| `ISettingsScreenDataProvider` | 73 | settings | open settings; if it works under `tform`, the `default` fallback works globally |
| `IPlayerProfileDataProvider` | 39 | `PlayerProfilePopup` | open a player profile; same test |
| `IQuestSelectModel` | 72 | quest select | already works indirectly? |

If these also fail under `tform`, the tag is the root cause. If they work,
the prefight call-site type/`ContainsKey` identity is the root cause.

## 6. Next actions

1. Resolve the `0x2BE2870` method-info generic argument (static metadata
   usage table) and compare it with the entry-69 key.
2. Open Settings/Profile under the live `tform` tag and probe
   `InterfaceInjector.Get` results.
3. A5: test the boss tile trigger with and without a `battle` action; record
   requests and the exact provider registry snapshot at map/prefight.
4. A6: variants cannot change a static registry; they can only change the
   trigger. Run a reduced matrix (battleEnemy/isFinalBoss/battleTower,
   progression fields, tile entity forms) and record provider presence.
