# Parser sample audit (Step 3.3 / 9.3)

Random seed 42; 20 pages with stat tables.

| page | parsed rows | header | flags |
|---|---:|---|---|
| Galvatron | 6 | ['Rank/Level', 'Health', 'Attack', 'Rating'] | ok |
| Barricade | 7 | ['Rank/Level', 'Health', 'Attack', 'Rating'] | ok |
| Mixmaster | 6 | ['Rank/Level', 'Health', 'Attack', 'Rating'] | r5l50: bad hp/atk |
| Megatron | 6 | ['Rank/Level', 'Health', 'Attack', 'Rating', 'Sig'] | ok |
| Megatron (ROTF) | 6 | ['scope="col"|Rank/Level', 'scope="col"|Health', 'scope="col"|Attack', 'scope="col"|Rating'] | r3l30: bad hp/atk |
| Hot Rod | 6 | ['Rank/Level', 'Health', 'Attack', 'Rating', 'sig', 'forge'] | ok |
| Drift | 6 | ['Rank/Level', 'Health', 'Attack', 'Rating', 'Sig/forge'] | ok |
| Cliffjumper | 7 | ['Rank/Level', 'Health', 'Attack', 'Rating'] | ok |
| Motormaster | 7 | ['Rank/Level', 'Health', 'Attack', 'Rating'] | ok |
| Jetfire | 7 | ['Rank/Level', 'Health', 'Attack', 'Rating'] | ok |
| Wheeljack | 7 | ['Rank/Level', 'Health', 'Attack', 'Rating'] | ok |
| Arcee | 6 | ['Rank/Level', 'Health', 'Attack', 'Rating', 'forge'] | ok |
| Bludgeon | 6 | ['Rank/Level', 'Health', 'Attack', 'Rating'] | ok |
| Starscream | 7 | ["Rank'Level", 'Health', 'Attack', 'Rating'] | ok |
| Windblade | 7 | ['Rank/Level', 'Health', 'Attack', 'Rating'] | ok |
| Mirage | 6 | ['Rank/Level', 'Health', 'Attack', 'Rating'] | ok |
| Necrotronus | 7 | ['Rank/Level', 'Health', 'Attack', 'Rating'] | ok |
| Shockwave | 7 | ['Rank/Level', 'Health', 'Attack', 'Rating', 'Sig'] | ok |
| Waspinator | 6 | ['Rank/Level', 'Attack', 'Health', 'Rating', 'sig'] | ok |
| Rhinox | 6 | ['Rank/Level', 'Attack', 'Health', 'Rating'] | ok |

Flags: 2

## Interpretation

- Header order is respected; pages with `Attack, Health, Rating` are not
  treated as `Health, Attack, Rating`.
- `rating==hp` on Ironhide rank 1 is the known suspicious row (Step 3.2 outlier).
- `rating<attack` or non-numeric HP/ATK indicates a wiki/row issue, not a
  valid rating; those rows are excluded from the rating LP.
- 20 pages sampled; the parser reads by header name, so a shifted wiki table
  would show as a flag here.
