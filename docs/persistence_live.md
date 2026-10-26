# Live persistence / background / WebSocket (5.3)

## SQLite persistence (kill + restart)

`work/live_persistence_test.py` starts `server/stub_server.py 8099` with
`TFTF_DB=work/persist_live.db`, posts
`/quests/quest-begin/story_act1_ch1_m1` with `tm0=bumblebee_cin_dotm_2`,
terminates the server, restarts it, and posts again.

`[RUN]` results:

```
before kill   quest_run=1
after kill    quest_run=1
after restart quest_run=1
db bytes      69632
```

The row survives the restart; the table is `quest_run` (singular), not
`quest_runs`. `schema_meta` has version 1. Account/roster/wallet are empty
because this flow only persists a quest run.

## Background requests

`[RUN]` The client sends `/util/ping` every ~56 s while idle/battle
(`server/requests.jsonl`); the server answers with the normal Sparx envelope.
No background request was lost during the persistence restart because the
restart used a separate port (8099) and the client was on 8080.

## `/ws`

`[RUN]` `GET /ws` (or any request with `Upgrade: websocket`) returns
`HTTP/1.1 400 Bad Request`; the client logs
`WebSocketError: Invalid handshake response: HTTP/1.1 400 Bad Request` and
retries every ~1 s. This is the known `/ws` gap (Step 7.3), not a crash. A
minimal 101 implementation needs a real WebSocket frame loop; a fake 101 would
change client behavior, so it is left as a documented gap.

## Tests

`python -m unittest tests.test_persistence -q`: 5/5 PASS (account, quest run,
reward ledger, roster, schema version).
