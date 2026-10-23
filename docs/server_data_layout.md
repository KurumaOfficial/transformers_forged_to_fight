# Server data layout (I1, current state)

`server/stub_server.py` still owns routing and a few computed envelopes. Most
large response bodies already live in `server/data/`. The next refactor should
move the remaining inline dictionaries into data files without changing the
wire shape.

## Data files

| File | Used by | Notes |
|---|---|---|
| `login_response.json` | `/auth/login` | auth envelope |
| `account_data.json` | `/account/data` | profile |
| `bcg_login_data.json` | `/bcg/getLoginData`, quest teamData | catalog + userData wrapper; contains active team clones |
| `quest_list.json` | `/quests/quest-list` | quest list |
| `quest_active.json` | `/quests/quest-active` | active quest |
| `quest_progression.json` | `/quests/quest-progression` | progression |
| `quest_detail.json` | `/quests/quest-detail` | map/tiles |
| `quest_begin_response.json` | `/quests/quest-begin` | active quest template; team replaced per request |
| `match_activate_response.json` | `/matches/activate-match` | **assumed**; no real request captured |
| `match_resolve_response.json` | `/matches/resolve-match` | **assumed** |
| `tuning_data.json` | `/tuning` | four values |
| `tuning_client_defaults.json` | docs/tests | only verified defaults |
| `bot_catalog_real.json` | catalog/reference | 59 client packs + wiki data |
| `missions_config.json` | `/autorefresh` | empty placeholder |

## Inline blocks still in `stub_server.py`

- quest-begin: builds `teamData` and the `team` dictionary from the request.
- movedir: builds `progression`, `localPlayer`, `results[]`, boss entity.
- activate-match / match-loaded / resolve-match: stub envelopes.
- auth/init/enumerate/prelogin and several empty auto-refresh responses.
- websocket `/ws` returns 400 (not used by the verified flow).

## Refactor order

1. Extract the movedir progression/localPlayer template to
   `server/data/movedir_template.json`; substitute `currentPos`, `cleared`,
   `battle` action.
2. Extract quest-begin `teamData` construction to a helper
   (`build_team_data`) with a data-driven team object.
3. Extract empty auto-refresh responses to
   `server/data/autorefresh_empty.json`.
4. Keep `/ws` behavior unchanged.
5. Run `work/smoke_test.py` and `work/golden_regression.py` after each step.

No behavior change was made in this documentation-only pass; the full refactor
is still open.
