# Tutorial protocol and switch (R6)

## Observed client calls

| endpoint | body | current stub |
|---|---|---|
| `POST /tutorial/get-login-data` | `{}` (or `tid`/`bid` on actions) | `server/data/tutorial_data.json`, all `completed` |
| `POST /tutorial/start` / `start-branch` / `complete` | `tid`, `bid` | generic `completed` response |

The client treats the per-branch `s`/`state` values as the tutorial state. All
branches in the current payload are `completed`, so the original FTE flow never
starts.

## Switch

The stub has a runtime switch (no client patch):

```
GET /__control?tutorial_mode=completed   # default, current behavior
GET /__control?tutorial_mode=original    # reset FTE/fte branches to not_started
GET /__control?reset                     # reset all experiment switches
```

`original` is `[ASSUMED]`: it sets `s/state=not_started`, `current_bid=fte`,
and leaves the branch graph intact. It was **not verified end-to-end**, because
the emulator became unstable and starting the FTE flow would change the whole
login path. The switch is opt-in and does not affect the default smoke/golden
runs.

## Remaining work

- Confirm the exact first branch the client expects (`FTEIntroCutScene`,
  `FTEIntroFight`, `Shields`) against a clean account.
- Capture `/tutorial/start*` and `/tutorial/complete*` request/response bodies
  in original mode.
- Decide whether the switch should persist per account instead of per server
  process.
