# Map validity rules (6.1)

## Static model

`Map.Deserialize` (`dump.cs` TypeDefIndex 12xxx) reads `gridDimension`,
`grid` as a **2D `MapTile[,]`**, `gridTiles`, `entities`, `walkableCount`,
`visibleWalkableCount`, `paths`, `startTile`, `endTile`. `MapTile` carries
`position`, `barrier`, `item`, `entities`, `links`, `visibleLinks`,
`incomingLinks`, `start`, `final`, `hidden`, render fields and buff lists.
`Map.SetupIncomingLinks()` builds `incomingLinks` from every tile's `links`.

The safe client-consumed shape is the one used by all 90 current quests:

```json
{
  "mapHash": "<qid>_map",
  "gridDimension": 3,
  "walkableCount": 9,
  "visibleWalkableCount": 9,
  "grid": [ [tile00, tile01, tile02], ... ],
  "startTile": ...,
  "endTile": ...
}
```

## Rules enforced

1. `gridDimension` is 3 and `grid` is exactly 3 rows x 3 columns (9 tiles).
2. Every tile's `position` equals its `(x, y)` index.
3. Every `links` entry is an in-bounds integer coordinate `0..2`.
4. Exactly one `start: true` and one `final: true` tile.
5. `walkableCount` equals the number of `walkable: true` tiles.
6. Each tile has `links`/`visibleLinks` arrays (never null).
7. `mapHash` is unique per qid.

`work/validate_maps.py` validates all 90 maps: **0 errors**
(`data/map_validation.json`).

## Why the 5-tile map failed

The earlier 5-tile/serpentine generator emitted a non-3x3 grid and tiles whose
`links` pointed outside the declared grid. `MapTile.Deserialize` stores the
links as `Vector2`; `Map.SetupIncomingLinks()` then indexes the 2D grid with
those coordinates, producing the observed `NullReferenceException`. The
9-tile full template removed the out-of-bounds links and the NRE.

## Different sizes

The static model allows any square `gridDimension` (the 2D array is
dimension-driven), but only 3x3 is **validated by a run** in this project.
A 4x4 map is a candidate experiment: generate a full 4x4 grid with in-bounds
links, one start and one final, and run the smoke flow. Do not use a 5-tile or
non-square grid until that run passes; the current safe default is 3x3.

## Current gaps

- The map entity on the final tile is still the template's placeholder; exact
  `QuestEnemyInfo` / boss entity fields are not mapped.
- `paths` are sparse; only `grid` is validated.
- Rewards/energy per tile are `[ASSUMED]`.
