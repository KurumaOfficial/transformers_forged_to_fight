# Sparx sync/async message catalog (observed + static)

## Envelope

`server/stub_server.py::make_sparx_response` [STATIC, parsed from
`EB.Sparx.Response`/`EndPoint`]:

```json
{
  "ts": 1792880000,
  "result": {},
  "sync": {},
  "async": [],
  "error": "message",
  "fatal": false,
  "retry": false
}
```

`sync` and `async` are omitted unless present. `error` is accompanied by
`fatal`/`retry`. Every observed endpoint returns `200` with this envelope;
`/auth/enumerate` returns `result: []`.

## Async entries

The client-side expected shape is `{component, message, payload, id, channel}`
(from `QuestsManager.Async`/`MatchManager` static code). No async entry has
been observed on the wire yet because the battle does not reach
match-loaded/resolve.

| component | message | payload (expected) | status |
|---|---|---|---|
| `quests` | `match-activated` | match id/type, fighter data | NOT OBSERVED |
| `quests` | `match-resolved` | result, rewards, progression | NOT OBSERVED |
| `quests` | `avx-update` | AvxEvent, ActiveQuest, Player | NOT OBSERVED |
| `quests` | `sync` | progression delta | NOT OBSERVED |

## Observed request-side identifiers

- `nonce`: `6add…` hex, client-generated.
- `api`: 1/3/6/11 depending on subsystem.
- `stoken`: `sess_tf_stub_token_12345` (fixture).
- `sig`/`sver`/`ts`: query signature fields; the stub ignores them.
- `qid`, `battleId`, `hero` in `/matches/activate-match/quests_fight`.

## Sync payloads

`/bcg/getLoginData` uses `result.userData` plus `updates`/`deletes`; the
`/quests/quest-begin` result is `{activeQuests: {qid: quest}}` with
`teamData` inside. `/ds/{uid}` is a profile/data-sync dict. `/account/data`
uses the account schema. These are the only sync families exercised.

## Next

Capture the real async entries after match-loaded/resolve; add them to
`docs/evidence/` and to this table with `[RUN]`.
