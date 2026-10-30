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
LVL remains 0 and STORE remains locked at LEVEL 2. Next check: read the live
`LoginManager._loginData` dictionary keys and the exact `levelrewards` key
case/spelling; do not keep an unverified schema change.

## Verification

- Restart the server, force-stop/restart the app, reach home: still `LVL 0`.
- The BCG route split was verified separately by a fast smoke PASS after the
  restart.
- No client patch.
