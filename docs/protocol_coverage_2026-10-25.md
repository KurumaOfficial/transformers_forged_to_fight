# Protocol coverage addendum — 2026-10-25

The older `docs/protocol_coverage.md` is the 2026-10-21 snapshot and still says
`/matches/*` was not observed. This addendum supersedes that row.

## `/matches/*` — first capture

`POST /matches/activate-match/quests_fight` was captured after the prefight
fix:

```json
{"hero":"bumblebee_cin_dotm_2","api":3,"nonce":"...",
 "qid":"story_act1_ch1_m1","battleId":"battle1"}
```

Full request: `docs/evidence/a9/activate_match_request.json`.
No `match-loaded` or `resolve-match` request followed; the client NREs in
`BattleArbiterInitState.InitPlayer`. The response is still the `[ASSUMED]`
`server/data/match_activate_response.json`.

## Endpoint groups (C1)

| group | endpoints seen/known | status |
|---|---|---|
| login | `/auth/init`, `/auth/enumerate`, `/auth/prelogin`, `/auth/login`, `/account/data` | observed; login/account bodies ASSUMED |
| catalog | `/bcg/getLoginData`, `/bcg/getBaseHeroData`, `/bcg/getUserData`, `/bcg/setSavedTeam`, `/bcg/getHeroXPCurve` | observed; catalog keys mostly mapped |
| account/data | `/ds/{uid}`, `/userprofile/`, `/inventory`, `/wallet` | observed; empty/ASSUMED |
| tuning | `/tuning` | observed; only 4 keys verified |
| gamestats | `/gamestats/get-login-data`, `/gamestats/check-login-achievements` | empty/accepted |
| tutorial | `/tutorial/get-login-data`, `/tutorial/*` | observed; all completed |
| objectives | `/objectives` (autorefresh) | empty; screen `[0/0]` |
| gacha | `/autorefresh/gacha/refresh`, `/gacha` | generic/empty |
| store | `/autorefresh/gamestore/refresh`, `/store` | locked level |
| redeemer | `/redeemer/refresh` | empty |
| events | `/events/refresh` | empty |
| offers | `/offers/getLoginData` | empty |
| pvp | `/pvp/get-login-data` | empty; locked |
| base | `/base/active` | observed; `pathData` real, rest ASSUMED |
| away | `/away/*` | not reached; locked |
| ds/chat/push | `/ds/{uid}`, `/chat/data`, `/push/token` | observed; empty |
| quests | list/detail/begin/movedir/progression/quit | observed; list now 90 missions |
| matches | activate-match | observed; match-loaded/resolve not reached |

## Empty endpoints and the keys the client reads (C2)

The stub returns `{}`/`[]` for `/gamestats/get-login-data`,
`/offers/getLoginData`, `/pvp/get-login-data`, `/redeemer/refresh`,
`/events/refresh`, `/chat/data`, `/userprofile/`, `/ds/10001`. The client
accepts these without an NRE, so the exact required keys are not proven. Known
client-side consumers from `dump.cs`:

- `UserProfile` (`/userprofile/`): `uid`, `name`, `tag`, `level`, `xp`,
  `strongestHero`, `currentPos`, `currentBattleId`, `currentBattleState`,
  `currentBattlePos`, `team`, `usedConsumableCount`, `battleLockExpiry`.
- `QuestUserInfo` (`/ds`): `uid`, `name`, `tag`, `strongestHero`, `team`
  (dict of `hp`, `pi`, `sig_lvl`, `stat_mods`, `sig_mods`).
- Chat: `messages`, `channels`, `blocked`, `friends`, `requests`.
- Events/offers/redeemer: `items`, `offers`, `events`, `rewards`, `expiry`.
These are **candidates**; empty responses do not prove which keys are
mandatory.

## TuningManager (C3)

`TuningManager` stores an `IDictionary` and applies values by field name
(`Apply(instance, field, name)`, `GetInt/GetFloat/GetBool/GetString`). It is
not a fixed schema; keys live on client classes.

Verified defaults (`server/data/tuning_client_defaults.json`):

| key | type | default |
|---|---|---|
| `heroRatingAttackWeight` | float | 1.0 |
| `heroRatingMaxHPWeight` | float | 0.2 |
| `sigLvlMax` | int | 100 |
| `ratingPrecision` | int | 0 (stub) / 1 in the catalog header |

All other keys are intentionally absent from the stub and must be discovered
from class fields/`Apply` call sites. `not_verified` in the JSON says this
explicitly.

## C4

Already explained: 7869 localization keys; 3315 stat strings exact; 3332 is a
legacy broad-scan artifact (17 unaccounted).
