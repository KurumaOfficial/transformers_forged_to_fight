from pathlib import Path

p = Path("docs/systems_screens.md")
s = p.read_text(encoding="utf-8")
marker = "## 2026-10-30 follow-up [RUN]"
i = s.index(marker)
new = """## 2026-10-30 follow-up [RUN]

- Tapping the top-left Commander block opens the BOTS roster; there is no
  separate profile screen or KABAM ACCOUNT/LOGIN OPTIONS popup at this point.
  Evidence `work/pf.png`.
- The FIGHT mode list shows STORY, RAIDS, SPECIAL (locked), ARENAS (locked),
  ALLIANCE (locked); no AWAY MISSIONS entry. Evidence `work/home.png`.
- Home still shows `LVL 0` although `login_response.user.level` and
  `account_data.user.level` are 5; the displayed level source is not the
  account level field. This is why STORE stays locked at LEVEL 2.

## 2026-10-30 level-lock chain (static)

`LevelLockWidget` -> `LevelLockManager.OnLoggedIn` (`0xF0DA28`) ->
`GameResourceUtils.GetPlayerLevel` (`0xA43580`) ->
`LevelRewardsManager.Level` (`0x1271818`). `LevelRewardsManager.Connect`
(`0x12733A0`) reads `Hub.User + 0x38` key **`levelrewards`**; if it is absent,
the level is 0. The min level for a lock (STORE = 2) comes from the client
`TuningLevelLocks.levelLocks` prefab, not from the server.

A reversible server-data experiment adds
`user.levelrewards={"level":5,"types":[]}` and
`user.levelrewards_milestones=[]` to `login_response.json` and
`account_data.json`. Live verification is pending the next restart:
`docs/level_lock.md`.
"""
p.write_text(s[:i] + new, encoding="utf-8")
print("ok")
