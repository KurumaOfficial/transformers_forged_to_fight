# Persistence design (I2, design only)

No storage code is implemented yet. This document defines the intended model so
the stub can move from hard-coded JSON to a real save without changing the wire
protocol.

## Recommendation

Use **SQLite** for mutable player state and keep immutable game catalogs as
versioned JSON under `server/data/`. SQLite gives transactional updates for
match/move sequences, avoids rewriting a large JSON file on every request, and
keeps a single-file backup. JSON remains acceptable for a single-player
prototype, but only with atomic write + lock and a schema version.

## Entities

| Entity | Key | Important fields | Written by |
|---|---|---|---|
| account | uid | name, level, xp, stoken, created_at | auth/login, account |
| wallet | uid | gold, energon, crystals, arena_chips, shanix | quests, arena, rewards |
| roster | uid + bid | rank, level, sig_lvl, xp, stamina, stamina_ts, pvpb, forge_level | bcg/hero updates |
| hero_stats_cache | uid + bid | rating_hp, rating_attack, rating, max_hp, attack, source_ver | bcg/getBaseHeroData |
| active_team | uid + activity_id | type, modes, expire, heroes_json | bcg/setSavedTeam, quest-begin |
| saved_team | uid + team_id | heroes_json | bcg/setSavedTeam |
| quest_run | uid + qid + run_id | unique_id, mode, phase, start_time, expiry, team_json, state | quest-begin, move, quit |
| quest_progress | uid + qid | current_pos, cleared_json, revealed_json, current_fight_id, current_battle_id, current_battle_state, local_player_json | movedir, match-resolve |
| match | uid + match_id | match_type, qid, fighter_init_json, state, created_at, resolved_at, result_json | activate-match, match-loaded, resolve-match |
| inventory | uid + item_id | count, kind, expires_at | inventory, rewards |
| reward_ledger | id | uid, source, source_id, payload_json, applied_at | any reward grant |
| tutorial | uid | step, flags_json | tutorial |

`heroes_json`, `team_json` and `fighter_init_json` are opaque payloads in the
first version; they are validated only by the client parser. Later migrations
can normalize them.

## Endpoint access

Reads:

- `/bcg/getLoginData` -> account, roster, active_team, saved_team, inventory.
- `/account/data` -> account + privacy settings.
- `/quests/quest-list`, `quest-active`, `quest-progression` -> quest_run,
  quest_progress.
- `/quests/quest-detail` -> immutable catalog + quest_progress.
- `/inventory`, `/wallet` -> wallet, inventory.
- `/matches/match-loaded` -> match.

Writes:

- `/bcg/setSavedTeam` -> saved_team (transaction).
- `/quests/quest-begin` -> quest_run (create or resume), active_team link.
- `/quests/quest-movedir` -> quest_progress, wallet (energy), match (if battle).
- `/quests/quest-quit` -> quest_run.state = quit.
- `/matches/activate-match` -> match row, idempotent by client request id.
- `/matches/resolve-match` -> match.result, quest_progress, reward_ledger,
  wallet/roster (single transaction).

## Concurrency and idempotency

- Every mutating endpoint accepts an idempotency key (`requestId` or a hash of
  uid + endpoint + body). A repeated key returns the stored response.
- Quest moves are serialized per `uid + qid`; reject a move whose `(x,y)` is not
  adjacent to `current_pos`.
- Match resolve is one transaction: result row, rewards, wallet, quest actions.
  If the client retries after a timeout, return the stored result.
- Keep a monotonically increasing `state_version` per player; include it in
  responses where the client tolerates extra fields. Do not expose it in places
  where the parser is strict.

## SQLite sketch

```sql
PRAGMA journal_mode=WAL;
CREATE TABLE account(uid TEXT PRIMARY KEY, name TEXT, level INT, xp INT,
                     stoken TEXT, created_at TEXT);
CREATE TABLE wallet(uid TEXT PRIMARY KEY, gold INT, energon INT, crystals INT,
                    arena_chips INT, shanix INT);
CREATE TABLE roster(uid TEXT, bid TEXT, rank INT, level INT, sig_lvl INT,
                    xp INT, stamina INT, stamina_ts INT, forge_level INT,
                    pvpb_json TEXT, PRIMARY KEY(uid,bid));
CREATE TABLE active_team(uid TEXT, activity_id TEXT, type TEXT, modes_json TEXT,
                         expire INT, heroes_json TEXT,
                         PRIMARY KEY(uid,activity_id));
CREATE TABLE quest_run(uid TEXT, qid TEXT, run_id TEXT, unique_id TEXT,
                       mode TEXT, phase TEXT, start_time INT, expiry INT,
                       team_json TEXT, state TEXT,
                       PRIMARY KEY(uid,qid,run_id));
CREATE TABLE quest_progress(uid TEXT, qid TEXT, current_x INT, current_y INT,
                            cleared_json TEXT, revealed_json TEXT,
                            current_battle_id TEXT, current_battle_state INT,
                            local_player_json TEXT,
                            PRIMARY KEY(uid,qid));
CREATE TABLE match(uid TEXT, match_id TEXT, match_type TEXT, qid TEXT,
                   state TEXT, fighter_init_json TEXT, result_json TEXT,
                   created_at TEXT, resolved_at TEXT,
                   PRIMARY KEY(uid,match_id));
CREATE TABLE idempotency(uid TEXT, key TEXT, response_json TEXT,
                         created_at TEXT, PRIMARY KEY(uid,key));
```

## JSON fallback

If JSON is kept for the prototype:

- one file per uid under `server/state/<uid>.json`;
- write to `*.tmp`, `fsync`, then atomic replace;
- a per-uid file lock;
- a top-level `schema_version` and `updated_at`;
- never store raw APK/archive data in player state.

## Migration

1. Start read-only: load current `server/data/*.json` into the new store.
2. Dual-read/compare for one smoke run.
3. Switch writes to SQLite.
4. Keep the old JSON as a dated backup; do not overwrite it.

This is a design document only; no database or endpoint behavior is changed in
this task.

## Implementation status (2026-10-25)

`server/persistence.py` implements the schema above (schema version 1):
account, wallet, roster, active_team, quest_run, reward_ledger, match, plus
`schema_meta`. It uses WAL mode and `INSERT ... ON CONFLICT` upserts.

Opt-in: set `TFTF_DB=<path>` before starting `server/stub_server.py`. The server
then initializes the DB and persists `quest-begin` (team/phase) and
`quest-movedir` (current position). With `TFTF_DB` unset the server behaves
exactly as before (JSON only).

Tests: `tests/test_persistence.py` (5 tests: schema version, account upsert,
roster upsert, quest-run JSON round-trip, reward ledger).

Not wired yet: login/account bootstrap from SQLite, match rows, reward
application, and migrations beyond version 1.
