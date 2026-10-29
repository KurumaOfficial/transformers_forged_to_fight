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

## Server-data experiment (reversible)

Added to `server/data/login_response.json` and
`server/data/account_data.json`:

```json
"user": {
  "level": 5,
  "levelrewards": {"level": 5, "types": []},
  "levelrewards_milestones": []
}
```

Backups: `server/data/*.pre_levelrewards` (local only, ignored by git).

Expected `[ASSUMED]`: home shows `LVL 5`; STORE no longer shows the LEVEL 2
lock. This is server data only, no client patch.

## Verification

- Restart the server, force-stop/restart the app, reach home, screenshot.
- If `LVL 5` and STORE opens: update `docs/systems_screens.md` and mark the
  level source confirmed.
- If not: revert the two JSON files from the backups and record the negative
  result; do not keep an unverified schema change.
