# Debug / dev / test modes (static audit, 2026-10-25)

Status: **no data-only activation found**. No client patch was made and none is
planned. All findings are `[STATIC]` from `work/il2cpp_dump/dump.cs` and
`libil2cpp.so`; asset presence is `[RUN]` (binary string scan of
`work/unpacked/assets`).

## Candidates and what they do

| Class | TypeDef | Role | Activation | Can start a fight / change state without server? |
|---|---|---|---|---|
| `TransformersDebugMenu` | 9445 | IMGUI menu registration; `Awake` marks `DontDestroyOnLoad` and calls `AddMenus` | a scene component must exist; `AddMenus` only sets `AddedMenus=true` | no. It adds debug menu entries, not a match. |
| `FuseDefaultDebugMenus` | 7646 | Sparx default menus | scene component | no |
| `SandboxDebugMenus` | 8415 | sandbox menus | scene component | no evidence of a fight starter |
| `FightTuningDebugSubmenu` | 8414 | reflects over tuning fields and edits floats/ints/bools | drawn by a parent debug menu | no; edits tuning only |
| `AddUIDebugMenu` | 6259 | old UI debug menu registration | scene component | no |
| `WindowManagerDebug` | 4933 | window stack debug overlay | scene component | no |
| `FlowManagerDebug` | 8499 | flow stack text overlay | scene component | no |
| `DebugFlow` | 8481 | placeholder flow | opened by debug menu/flow name | no; empty enter/exit |
| `DebugHudOverlay` | 9862 | in-fight debug overlay | prefab/window; a serialized bundle contains the name | no; visual overlay |
| `Misc.DebugSettings` | 5010 | static flags (`LoadEmptyStage`, `StopOnPlayerLoad`, ...) | code only; no JSON/tuning mapping | no; can stop loads, not start a match |
| test screens (`BusyBlockerTestScreen`, `EventTestScreen`, `FontSizeTestingScreen`, ...) | 9539+ | UI test windows | window prefabs, dev scenes | no |

## Asset evidence

The class names appear in `assets/bin/Data/globalgamemanagers.assets` (Unity
type registry) and in `global-metadata.dat`. `DebugHudOverlay` additionally
appears in one serialized bundle (`assets/bin/Data/6398d994...`). There is no
scene/config key that instantiates any of these components in the retail
build, and no `TuningManager`/`account/data` flag was found that loads them.

## Data-only activation attempts

No safe data key exists to open these menus. The only way to use them would be
to add a component to a scene or patch the client, both forbidden. Therefore
4.2 is **not attempted**; there is nothing to enable from the server.

## Static requests

Because the modes are not instantiated, they make no requests in our runs. No
endpoint needs silencing for them. The only persistent background requests
remain `/autorefresh/grouprefresh` and `/autorefresh/ads/refresh`.

## Conclusion

The debug/dev classes are retail-dead code or dev-scene components. They do not
provide an offline fight path or a server-free state change. The battle path
remains the normal `/matches/*` flow.
