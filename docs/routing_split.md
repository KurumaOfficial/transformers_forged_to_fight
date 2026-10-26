# Routing split (T1) — status

## Current

- `server/routes/quests.py`: quest detail/begin builders (already split).
- `server/routes/__init__.py` exists.
- Auth/BCG/account/tuning/matches/ODR/ws handlers are still inline in
  `server/stub_server.py` (`dispatch`).

## Target modules

| module | responsibility |
|---|---|
| `routes/auth.py` | `/auth/init`, `/auth/enumerate`, `/auth/prelogin`, `/auth/login` |
| `routes/bcg.py` | `/bcg/getLoginData`, `/bcg/getBaseHeroData`, `/bcg/getUserData`, `/bcg/setSavedTeam`, `/bcg/getHeroXPCurve` |
| `routes/quests.py` | list/detail/begin/movedir/moveto/quit/progression |
| `routes/matches.py` | activate-match, match-loaded, resolve-match |
| `routes/odr.py` | `/odr/get-manifest`, `/odr/get-published-manifests`, `/cdn/*` |
| `routes/misc.py` | account/tuning/autorefresh/gacha/store/base/pvp/tutorial |
| `routes/common.py` | `send_sparx`, request logging, `load_data_json` |

Each module should expose `handle(handler, path, query, headers, body) -> bool`
and use the existing envelope; `stub_server.dispatch` calls them in order and
falls back to the current unknown endpoint only if none handles the path.

## Behavior contract

- Same 200/Sparx envelope on every known path.
- Golden 9/9 and fast smoke PASS after each move.
- No route is deleted until a test covers its path.
- Unknown fallback stays last.

## Status

**Partial.** Quests are split; the rest is a planned refactor. It is not done
in this session because the ODR/battle blocker has higher priority and a large
move without per-route tests risks the working login/quest flow.
