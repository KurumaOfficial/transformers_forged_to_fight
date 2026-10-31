
## 2026-10-31 v4.12: LevelRewards payload shapes tried

`LevelRewardsStatus..ctor` (`0x1271E70`) reads `last_awarded_level` and
`nextLevelXp` (literal keys resolved), plus a `types` list
(`LevelRewardsType` fields: `Name`, `Level`, `NextResourceThreshold`,
`PreviousResourceThreshold`). `LevelRewardsManager.OnLevelData` (`0x1271D64`)
constructs the status and stores it at `+0x28`; `Level` is the int at `+0x10`.

`/levelrewards/fetch` was changed to return both:

```json
{"status": {"last_awarded_level": 5, "nextLevelXp": 1000,
  "types": [{"name": "commander", "level": 5,
             "nextResourceThreshold": 1000,
             "previousResourceThreshold": 0}]},
 "levelrewards": {same}, "levelrewards_milestones": []}
```

After a full restart the live `LevelRewardsStatus` was still
`Level=0`, `IsEnabled=false` (`work/probe_level.py`). The status object exists
but is the default, not the fetched one. The first `Dot.Object` key in the
ctor could not be resolved to a string; it may be a `JSONPath`/`status`
sub-object. The endpoint is requested, so the remaining gap is the exact
result root/path, not the route.

This is the third level attempt; it is recorded as blocked and the next
independent items take priority. Do not claim a working account LVL/STORE.
