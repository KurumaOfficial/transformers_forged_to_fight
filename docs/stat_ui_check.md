# Bot stats from wiki: catalog, battle, UI (Step 4)

Status: **catalog and battle now use wiki-derived HP/ATK; rating is exact for
rank 1/level 1 when the wiki stat table has a row.** The BOTS list and the
upgrade screen use separate client fields and are still open.

## Implementation

- `server/wiki_stats.py` loads:
  - `data/wiki/stat_coverage.json` (client_id -> wiki page, level1 HP/ATK);
  - `data/wiki/stat_growth_fit.json` (per-bot `a_rank*rank + b_level*level + c`);
  - `data/wiki/bots.json` (exact `1/1` rating row).
- Some fit entries had HP/ATK swapped (Rhinox); the helper detects this by
  comparing the fit at 1/1 with the wiki level1 anchor and swaps them.
- `server/routes/bcg.py` uses it for `getBaseHeroData` and `setSavedTeam`;
  `server/stub_server.py` uses it for `team_data` and `hero_details`.
  `bcg/loginData` and `bcg/userData` are enriched in memory.
- `/bcg/getHeroXPCurve` now returns the hero XP curve array, fixing the
  `BCGHeroBaseCommon.SetXPCurve` NRE seen when opening the upgrade screen.

## Values `[RUN]`/`[WIKI]`

| bot | live/catalog HP | ATK | rating | wiki source |
|---|---:|---:|---:|---|
| Bumblebee (DOTM, live team) | 1066 | 97 | 155 `[ASSUMED]` | `stat_coverage` level1; no wiki stat table |
| Bumblebee (classic) | 4860 | 444 | 1353 `[WIKI]` | 1/1 row |
| Sideswipe (live enemy) | 5160 | 520 | 1426 `[WIKI]` | 1/1 row |
| Windblade | 5160 | 498 | 1381 `[WIKI]` | 1/1 row |
| Rhinox | 5940 | 396 | 1413 `[WIKI]` | 1/1 row |
| Arcee | 5340 | 516 | 1397 `[WIKI]` | 1/1 row |
| Barricade | 5160 | 520 | 1377 `[WIKI]` | 1/1 row |
| Optimus Prime (MV1) | 6720 | 507 | 1427 `[WIKI]` | 1/1 row |

Bots without a stat table use the level1 anchor + median growth (`[DERIVED]`,
~12% uncertainty); bots without any wiki row keep the placeholder (`[ASSUMED]`,
~40% uncertainty). The source is stored per hero as `stat_source` and
`rating_source`.

## Live battle `[RUN]`

`work/battle_step.py` with the new stats:

- player Bumblebee (DOTM): HP start **1066**, attack 97;
- enemy Sideswipe: HP start **5160**, attack 520;
- player damage **67.9**, enemy damage **1206.4**, result **LOST**,
  resolve-match and HP decrease still true.

This is the real-number balance result, not tuned to force a win. The player is
rank1/level1 DOTM Bumblebee against a rank1/level1 Sideswipe whose wiki HP is
5160; the loss is expected with the current auto-loop.

## UI gaps

- The BOTS **list** still shows a flat `300` rating for visible bots even
  though the login payload now carries 1381/1426 etc. The list uses a separate
  client field/prefab value; open.
- The **UPGRADE** screen shows `HP 0`, `ATK 0`, `LEVEL 1/10`, `RANK 1/5`.
  The battle and login payloads carry 1066/97/5160/520, and the XP-curve NRE
  is fixed, but the upgrade presentation reads another path. Open.
- The bot **INFO** detail screen was not recaptured after the change; the
  earlier detail screen showed the old 826/102. Do not claim a UI match for
  every bot yet.

## Balance note

The queue asked for real numbers without forcing a win. The current result is
a loss; the damage/resolve loop is intact. Further balance work belongs to
ability/stat mods, not to faking HP/ATK.
