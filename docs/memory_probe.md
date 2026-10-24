# IL2CPP memory probe without Frida (A3)

Read-only probe via `/proc/<pid>/mem` on the emulator (`su 0 dd`); no Frida,
gadget, agent, or client patch. Script: `work/read_bcg_memory.py`.

## Resolving BCGManager

`BCGManager.get_Instance` (`0xA5C688`) uses a generic-static chain, not the
simple `static_fields + 8` form used by `QuestsManager`:

```text
base = libil2cpp rw-p base
slot = base + 0x2BC1C68
p1 = u64(slot)
p2 = u64(p1)
p3 = u64(p2 + 0x18)
p4 = u64(p3 + 0xC0)
p5 = u64(p4)
static_fields = u64(p5 + 0xB8)
BCGManager = u64(static_fields)
```

The missing `p5 = u64(p4)` step was why earlier probes saw nonsense. Verified:
`BCGManager` at `0x77987eb47f00`, `BCGUserData` at `0x77987eb3d480`.

## Layout used

`BCGUserData` (`TypeDefIndex 8336`):

| Offset | Field |
|---|---|
| `+0x10` | `heroes` (`BCGUserHeroDict`) |
| `+0x28` | `savedTeams` (`BCGUserSavedTeamDict`) |
| `+0x30` | `activeTeams` (`BCGUserActiveTeamDict`) |

`BCGUserActiveTeam`:

| Offset | Field |
|---|---|
| `+0x10` | `ActivityID` (string) |
| `+0x18` | `Type` (string) |
| `+0x20` | `Modes` (`List<string>`) |
| `+0x28` | `TeamHeroes` (`BCGHeroDetailsList`) |
| `+0x30` | `EstimatedExpire` (int) |

`BCGHeroDetailsBase`:

| Offset | Field | Type |
|---|---|---|
| `+0x10` | `Blueprint` | string |
| `+0x18` | `Rank` | int |
| `+0x1C` | `Level` | int |
| `+0x20` | `SigLevel` | int |
| `+0x24` | `HPRating` | int |
| `+0x28` | `HPMax` | int |
| `+0x2C` | `AttackRating` | int |
| `+0x30` | `Attack` | int |
| `+0x34` | `Special` | int |
| `+0x38` | `UserOwned` | bool |
| `+0x40` | `AttributeData` | `BCGAttributeData` |
| `+0x58` | `ForgeLevel` | int (derived class) |

`QuestProgression.localPlayer` is at `+0x80`; `QuestUserInfo.team` is a
`List<QuestUserHero>` at `+0x68`.

## Observed 2026-10-23 (live client, prefight open)

```text
activeTeams:
  'story_act1_ch1_m1' -> aid=story_act1_ch1_m1 type=story TeamHeroes count=1
  'story'              -> aid=story              type=story TeamHeroes count=1
    hero blueprint=bumblebee_cin_dotm_2 rank=1 level=1 sig=0
         hpRating=50 hpMax=1050 atkRating=50 atk=115 owned=01
  'story_act_1'        -> added from the client's setId, same hero
savedTeams: teamID '0' is present
heroes: keys 'bumblebee_cin_dotm_2' and 'bumblebee_cin_dotm'
QuestsManager: qid='story_act1_ch1_m1', mode='story'
localPlayer: Player object, team List count=1
```

This corrects the earlier "team count 0" statement: the active BCG team and
the quest-team list are non-empty with the current stub. The remaining empty
prefight is therefore **not** a missing `activeTeams` key or a missing hero
entry; it is downstream of that (TeamData construction/cache or the prefight
presentation's `HeroData` lookup).

## Reproduce

```powershell
python work/read_bcg_memory.py
```

The probe prints the BCG manager, active/saved teams, hero fields, the active
quest and `localPlayer.team`. It only reads memory. No Frida/gadget.

## 2026-10-24: injector probe recipe

The libil2cpp load base must be computed from the **rw-p mapping with
file offset 0x2a97000**: `BASE = rw_start - 0x2AA7000`. Using the first
rw-p line can give a wrong base. InterfaceInjector:

```text
slot = BASE + 0x2C33650
p1 = u64(slot)          # pointer to the Il2CppClass
cls = u64(p1)           # 0x... InterfaceInjector
sf = u64(cls + 0xB8)    # static fields
tag = ilstr(u64(sf + 8))
gameInterfaces = u64(sf + 0)
persistent = u64(sf + 0x18)
```

At 2026-10-24: tag `tform`, gameInterfaces count 78, persistent count 1
(`IAdsProvider -> TFormIronSourceAdsModel`). Entry 0 has tags
`tform/default`; all other entries are default-only. The dictionary
entries array starts at `entries + 0x20`; Entry is 24 bytes
(hash/next 8, key Type 8, value List 8). Each List item is a
`Tuple<string,Type>`; item1 is the tag string, item2 the implementation
Type. [RUN]
