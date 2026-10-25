# Deterministic quest map generator (Q2)

Source: `work/build_quest_list_full.py`. Every quest in
`server/data/quest_list.json` gets a `QuestMaps[qid]` entry and a
`mapHash = "<qid>_map"`.

## Layout

The current layout is a fixed 3x3 serpentine path (layout is `[ASSUMED]`; the
wiki gives mission names and bosses, not the exact retail grid):

```
(0,0) -> (1,0) -> (2,0)
                   |
                 (2,1)
                   |
                 (2,2)
```

`walkable=true` only on those five tiles. `links`/`visibleLinks` follow the
path. The final tile gets `final=true` and, if a boss id is known, one entity:

```json
{"id": "<boss_client_id>", "hero": "<boss_client_id>", "level": 1,
 "rank": 1, "team": "enemy", "ai": "default"}
```

## Determinism

`qid` alone determines the map: the same id always produces the same grid,
path and boss tile. There is no RNG. This is intentional so repeated
`quest-begin`/`quest-detail` responses are stable and the client cache never
sees a changed map for the same quest.

## Bosses

`finalBoss.id` and the final-tile entity use `boss_client_id` from
`data/quests_real.json` (wiki match, high confidence where available). If the
wiki match is missing or ambiguous, the map has no boss entity and
`finalBoss` is `null`; the client still opens the mission. Quest 1.1 uses
`rhinox_gs_voyager2014`.

## Next

- Replace the serpentine layout with per-act maps once real layouts are
  available.
- Add gates/barriers/items per act.
- Keep `mapHash` stable when only rewards/descriptions change.
