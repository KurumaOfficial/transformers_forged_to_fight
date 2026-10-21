# BCG userData / roster — partial findings

Status: **blocked**. The client does not show a bot in `EDIT SQUAD` yet.
Everything below is either [STATIC] (read in `dump.cs`/disassembly) or [RUN]
(observed on the emulator). No original roster dump was available.

## 1. Where the client reads it

`BCGManagerBase.OnBCGData` (`RVA 0x168C7C4`) reads the top-level key
**`userData`** from the `/bcg/getLoginData` result and calls two virtual
handlers (`0x1690134`, `0x169016c`). [STATIC]

`BCGManagerBase.HandleUserDataUpdates` (`RVA 0x1695CC0`) reads: [STATIC]

- `activeTeams`
- `savedTeams`
- `inventory.f`
- `inventory.bp`
- `inventory.max`
- `heroes` — **array** (`Dot.Array`), each item is passed to `BCGUserHero..ctor`
- `heroesScreenList`
- `heroes_cta`

## 2. Hero item keys

`BCGUserHeroBase..ctor` (`RVA 0xA62348`) reads `JSONPaths` fields. The field
names at the offsets used by the constructor: [STATIC]

| JSONPaths field | Wire key | Used for |
|---|---|---|
| `entity_type` | `entity_type` | "hero" |
| `bid` | `bid` | blueprint id |
| `rank` | `rank` | rank |
| `level` | `level` | level |
| `sig_lvl` | `sig_lvl` | signature level |
| `required_xp` | `required_xp` | XP |
| `max_xp` | `max_xp` | XP cap |
| `stamina` | `stamina` | stamina |
| `stamina_ts` | `stamina_ts` | stamina timer |
| `stamina_full_ts` | `stamina_full_ts` | stamina timer |
| `stt` | `stt` | special team flag |
| `pvpb` | `pvpb` | PvP points boost |
| `exc` | `exc` | character exclusivity expiry |

The constructor then looks up `bid` in `BCGManager.Instance` blueprint data and
builds `BCGAttributeData`. If the blueprint is missing it logs
`HeroData.Create - blueprint '...' does not exist in BCG data`. [STATIC]

## 3. What was tried [RUN]

Payloads placed under `/bcg/getLoginData.result.userData`:

1. `heroes` as a dictionary keyed `"1"`, camelCase keys (`entityType`,
   `blueprint`, `rank`, `level`, ...) — `EDIT SQUAD` empty.
2. `heroes` as an array, snake_case keys (`entity_type`, `bid`, `rank`, ...) —
   `EDIT SQUAD` empty.
3. Same array plus `id`, `uid`, `hero`, `blueprint`, `modes`, `modesAvail`,
   `team_types` — `EDIT SQUAD` empty.

`/bcg/getUserData` was **not requested** on boot or in `EDIT SQUAD`. Opening
BOTS crashes before any roster fetch:

```text
NullReferenceException
  at HeroesScreen.SetFeaturedHeroData(Boolean state)
  at HeroesScreen.WindowEnter(Boolean isFirstEntry)
```

## 4. Hypotheses (all [ASSUMED] until proven)

- The `heroes` array items need an extra wrapper key (e.g. `"hero"` or `"data"`)
  that `BCGUserHero..ctor` unwraps.
- `userData` is applied only through a **sync/update** message, not through
  `getLoginData`, and the login payload must carry it in a different envelope.
- `HeroData.GetHeroes(modes)` filters the parsed hero out because the blueprint
  lacks a mode/team-type field; the roster is populated but invisible.
- `BCGManager.UserData` is populated, but `EditTeamModel` reads a different
  collection (`heroesScreenList`/`activeTeams`).

## 5. Next diagnostic

1. Fix the BOTS crash by supplying `featuredhero` data, then see whether BOTS
   calls `/bcg/getUserData` and renders the roster.
2. Or inspect `BCGManager.Instance.UserData.heroes.Count` at runtime via
   `/proc/<pid>/mem` / Frida after login.
3. Decode the `x27` key in `HandleUserDataUpdates` (`0x1695F60`); it selects the
   hero sub-object from each array item.
