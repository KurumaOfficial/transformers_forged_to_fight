# Routing split (Step 9.1, partial -> T1)

Status: **partial but functional.** Behavior is unchanged; the smoke/golden
contracts are the guard.

## Modules

| module | contents | notes |
|---|---|---|
| `server/routes/auth.py` | `/auth/init`, `/auth/enumerate`, `/auth/prelogin`, `/auth/login`, `/account/data` builders | no side effects; login fallback lives here |
| `server/routes/matches.py` | activate/match-loaded/resolve builders | data files loaded by the caller |
| `server/routes/odr.py` | get-manifest/published-manifests builders | stub data unchanged |
| `server/routes/quests.py` | quest list/detail/begin/movedir builders (from v4.8) | already in use |
| `server/stub_server.py` | HTTP loop, request logging, remaining routes, dispatch | still contains bcg/quests inline dispatch |

## Why not a full dispatch split yet

The HTTP handler still owns `self.send_sparx`, request logging, `EXPERIMENT`,
`ACTIVE_POS`, and persistence. Moving dispatch would require a handler
interface and a larger regression pass; the current split removes the static
payload builders without changing the wire. The remaining inline routes are
mostly BCG catalog logic, which is coupled to `load_data_json` and the quest
team builder.

## Verification

- `python work/golden_regression.py` PASS (9 shapes, regenerated after the
  hidden-stat data change).
- 32 unit tests PASS.
- Fast smoke can reach activate-match; navigation is still state-dependent
  (the START tap can race the map and open NODE INFO). This is a test-harness
  issue, not a server response change.
- No push, no client patch.

## Next

- Extract BCG builders (`getBaseHeroData`, `setSavedTeam`) behind the same
  pattern once their shared helpers are isolated.
- Add a handler interface if the remaining `self.send_sparx` coupling is
  worth the risk.
