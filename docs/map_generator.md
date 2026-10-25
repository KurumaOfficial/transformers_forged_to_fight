# Deterministic quest map generator (Q2)

Source: `work/build_quest_list_full.py`. Every quest in
`server/data/quest_list.json` gets a `QuestMaps[qid]` entry and
`mapHash = "<qid>_map"`.

## Current implementation (2026-10-25)

The client's `MapTile.Deserialize` is strict about the 9-tile graph. The
generated `grid` initially caused a NullReferenceException for a custom
5-tile/serpentine graph, so the generator now returns the **already-validated
9-tile template** from `server/data/quest_detail.json`, changing only
`mapHash`. This is deterministic per qid and keeps the client parser happy.

The template has 9 walkable tiles, a start at `(0,0)`, a final at `(2,2)`,
the original branch links and the template's map entity. The boss used by the
prefight is **not** the map entity: it comes from `finalBoss` /
`scaledBossTable` (`rhinox_gs_voyager2014` for 1.1, `sideswipe_gs` for 1.4.2).
A future pass can replace the template entity with the per-quest boss once
the exact `Entity` fields required by `MapTile.Deserialize` are known.

## Determinism

`qid` alone determines the map object. There is no RNG, so repeated
`quest-begin`/`quest-detail` responses are stable.

## Bosses

`finalBoss.id` and `scaledBossTable.enemy1.key` use `boss_client_id` from
`data/quests_real.json` where the wiki match is high-confidence. If the match
is missing/ambiguous, `finalBoss` is null and the map has no per-quest boss.
`data/boss_map.json` lists all 90 entries (60 with a client id).

## Next

- Replace the template entity with the per-quest boss after mapping the
  `Entity` fields exactly.
- Add per-act layouts, gates, barriers and items.
- Keep `mapHash` stable when only rewards/descriptions change.
