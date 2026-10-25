# Prefight flow — provider registration (2026-10-24) and the 2026-10-25 fix

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

## 12. A8/A9: prefight provider found and FIGHT now activates a match (2026-10-25)

**The earlier claim "`PreFightScreen._model` is null" was wrong.** A live dump of the
`PreFightScreen` object found through `WindowManager.windowStacks` shows all four
fields filled after `SetupWindow`/`WindowEnter`:

| field | value | class |
|---|---|---|
| `+0x88 _config` | non-null | `PreFightParams` |
| `+0x90 _presentationSCI` | non-null | `SharedComponentInstance` |
| `+0x98 _model` | non-null | `PrefightScreenData` |
| `+0xA0 _presentation` | non-null | `PrefightScreenPresentation` |

`CacheReferences` (`0xE38E4C`) has no early exit before
`Get<IPrefightDataProvider>` (`0xE38F08`); it stores the result at `+0x98`, then
only checks `_presentationSCI` for null. `SetupWindow` (`0xE38E24`) calls
`CacheReferences` unconditionally and then the base `Window.SetupWindow`.
`WindowEnter` (`0xE3915C`) runs the `InitializeData` coroutine, which calls
`_model.Init(config, this, callbacks)`; that call also succeeded.

**Actual cause of the OnFight NRE:** `PrefightScreenData.InitEnemy` (`0xE3CE64`)
builds the enemy hero from `QuestBoss.character`, and `QuestBoss.get_character`
(`0xEA469C`) returns `Entity.key` (`+0x30`), also comparable to `BCGEntity.key`.
Our `scaledBossTable.enemy1` had `"key": "enemy1"` while the blueprint was in
`"characters": ["rhinox_gs_voyager2014"]`. The BCG lookup therefore asked for
`enemy1`, returned no hero, left `_model._enemy` null, and `GetHeroDataForSide(1)`
returned null; `OnFight` dereferenced it.

**Data fix:** `server/data/quest_begin_response.json` (and the map copy in
`quest_detail.json`) now set `"key"` to the first entry of `"characters"`.
No client patch.

**Result [RUN]:** FIGHT is enabled; the screen shows Bumblebee 100 vs Rhinox 200,
both 1,050/1,050 HP. Pressing FIGHT sends
`POST /matches/activate-match/quests_fight` with
`{"hero":"bumblebee_cin_dotm_2","qid":"story_act1_ch1_m1","battleId":"battle1"}`.
This is the first captured `/matches/*` request; the body is in
`docs/evidence/a9/activate_match_request.json`.

**New blocker [RUN]:** the fight scene loads, then
`BattleArbiterInitState.InitPlayer` throws `NullReferenceException`; no
`/matches/match-loaded` request follows. Live `FightFlow.FightInitInfo` has both
`playerFighter` and `enemyFighter` non-null, both have `Blueprint`; the enemy
fighter's `TeamData` is null (player's is not). This is a separate battle-scene
init issue, not the prefight provider.

**QuestboardHud (1.3):** at prefight the `QuestboardHud` window is still present
in the same `WindowManager` layer stack below `PreFightScreen`; no
"Coroutine couldn't be started because ... QuestboardHud is inactive" warning
was produced in the successful runs. The one-off warning is therefore not
causal to the provider/FIGHT failure.

## 13. A5: default-only providers under tag `tform` (2026-10-25)

- Settings (`ISettingsScreenDataProvider` entry 73, default-only): **works**.
  ACCOUNT, SOUND and STORY tabs render; screenshots in
  `docs/evidence/a5/settings_*.png`.
- Objectives (`IGoalsModel` entry 58, default-only): screen opens with
  `[0/0] COMPLETE`; the screen is not NRE, only the server payload is empty.
- BOTS -> UPGRADE (`IUpgradeScreenModelBase` entry 77, default-only): screen
  opens; later NRE is in `BCGHeroBaseCommon.SetXPCurve` because the
  `/bcg/getHeroXPCurve` stub payload is empty, not because the provider is
  missing.
- Quest select/details and edit-squad paths use their default-only models and
  open (details available; edit-squad can NRE when the active team is empty).
- Profile (`IPlayerProfileDataProvider` entry 39) is not reachable in the
  current home build: the commander block is not wired, chat/friends are empty,
  and the gear opens Settings/account, not the profile popup.

Conclusion: the `default` fallback in `Get<T>` works under tag `tform` for
several independent interfaces. The prefight defect was **not** the tag or the
fallback; it was the enemy-key data described above.

## 14. A6: movement and battle are one request, not two (2026-10-25)

The client has no separate "battle" request. One `POST
/quests/quest-movedir/{qid}/{dx}/{dy}` is sent per move; the response's
`results[]` array may contain a `moveto` action and/or a `battle` action.
With a `moveto`-only response the character moves (11% -> 22% -> 33% -> 44% ->
55% explored) and tapping the final tile again sends nothing and never opens
prefight. The prefight is opened only when the server includes
`{"action":{"battle":...}}`; the client does not check that the tile is a boss
tile. This was reproduced with the runtime switch
`/__control?movedir_actions=moveto|battle|both`.
