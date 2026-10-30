# Home level and STORE lock (Step 6)

Status: **static chain found; live test pending the next server restart.**

## Why the home shows `LVL 0` and STORE says LEVEL 2

`[STATIC]` chain:

1. `LevelLockWidget.Awake` (`0xF0DF9C`) registers with
   `LevelLockManager` (`0xF0D028`).
2. `LevelLockManager.OnLoggedIn` (`0xF0DA28`) calls
   `GameResourceUtils.GetPlayerLevel` (`0xA43580`) and stores the result in
   `_playerLevel`.
3. `GetPlayerLevel` returns `LevelRewardsManager.Level` (`0x1271818`).
4. `LevelRewardsManager.Connect` (`0x12733A0`) reads
   `Hub.User + 0x38` and the key **`levelrewards`** (metadata string index
   18415). If the field is absent, `_level` stays 0.
5. `LevelRewardsStatus` (`0x1271E70`) reads `level` and `types`;
   `LevelRewardsManager.OnLevelData` (`0x1271D64`) copies `Level` into
   `_level`.

So the account level at `login_response.user.level` (5) is not the value the
lock uses. The lock uses `user.levelrewards.level`.

## Server-data experiment (reversible, negative)

Tried in `server/data/login_response.json` and
`server/data/account_data.json` (both top-level and under `user`):

```json
"levelrewards": {"level": 5, "types": []},
"levelrewards_milestones": []
```

with `level`, `Level`, `types`, `Types` variants. The home still showed
`LVL 0` after a full server/app restart, so the field placement or schema is
not accepted. **The changes were reverted**; the two JSON files are back to
their original content. Backups were kept locally as
`server/data/*.pre_levelrewards` (not committed).

Result `[RUN]`: the `levelrewards` hypothesis is **not confirmed**. The home
LVL remains 0 and STORE remains locked at LEVEL 2.

## Live probe of the login dictionary `[RUN]`/`[STATIC]`

A read-only `/proc/pid/mem` probe (`work/probe_login_data.py`) followed
`Hub.Instance -> Hub+0x40 LoginManager -> LoginManager+0x38 _loginData`.
The object is a `System.Collections.Hashtable`; its live header was:

```
buckets=0x...  count=0  occupancy=0  loadsize=12  loadFactor=0.72  version=0
```

So `_loginData` is **empty at the home screen**, even though `/auth/login`
returned `user`, `level`, and the test `levelrewards` field. Adding
`levelrewards` to the login/account JSON does not populate this hashtable.
`LevelRewardsManager.Connect` therefore sees no `levelrewards` entry and leaves
the level at 0. The client did not request `/levelrewards/fetch` in the
verified flow; that endpoint is likely called only from the level-rewards UI.

Conclusion: the home LVL / STORE lock is a client-fetch gap, not a missing
server field we can fill blindly. The JSON changes were reverted. Next step
would be to trigger the level-rewards screen or find the exact code that
populates `_loginData`; no client patch.

## Verification

- Restart the server, force-stop/restart the app, reach home: still `LVL 0`.
- The BCG route split was verified separately by a fast smoke PASS after the
  restart.
- No client patch.

## 2026-10-30 level fetch path found, payload still not accepted

- `LevelRewardsAPI.FetchStatus` (`0x1271694`) calls **`/levelrewards/fetch`**
  (metadata string index 1298).
- `LevelRewardsManager.Async` (`0x1273494`) handles **`level-up`** (calls
  `OnLevelUp`) and **`sync`** (calls `FetchStatus`).
- Sending async `sync` from `/bcg/getLoginData` with components
  `levelrewards`, `LevelRewardsManager`, `levelrewardsmanager`,
  `levelRewards` caused a real **`GET /levelrewards/fetch`** `[RUN]`.
- The endpoint is now served with
  `result.levelrewards={last_awarded_level:5, types:[]}` plus top-level
  duplicates; `levelrewards_milestones=[]`.
- Despite the request and a 200 response, live
  `LevelRewardsManager._status.Level` stayed **0**; the status has a default
  `types` array of length 6. The fetch is real, but the response schema is not
  accepted (or the status object is the prefab default and `OnFetch` is not
  applying it).
- Home `LVL 0` and STORE LEVEL 2 lock remain.

Next static step: read the exact `LevelRewardsStatus..ctor` field set and the
live `Response`/`OnFetch` path; test a `types` array schema, not an empty one.
The `sync` probe is kept behind the login async for now; it is harmless (one
extra fetch) and documented as `[ASSUMED]`.
