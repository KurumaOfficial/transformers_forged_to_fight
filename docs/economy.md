# Economy: known numbers, client placeholders, gaps (Step 8.2)

Status: **partial / blocked by missing source data.** The wiki pages retained in
`data/wiki/pages.json` describe the economy but contain almost no numeric
tables. The server catalog currently uses `[ASSUMED]` placeholders.

## Known numeric facts [WIKI]

Source pages: `Energon`, `Forge`, `Gold`; timestamps as saved in
`data/wiki/pages.json`.

### Energon

- Campaign stage completion: **10 Energon**, full exploration **+15**;
  Prime difficulty **15 / +20**.
- Login calendar, sixth day of each week: **10, 20, 30, 40** Energon.
- Ads: three videos per day, **5 / 4 Energon** per video.
- Raid Store: 10 bundles of **20 Energon for 3,000 Raid Chips** each,
  up to **200 Energon for 30,000 Raid Chips**.
- Arena opponent change: **5** Energon.
- Arena bot cooldown: **5, 10, 15, 30** Energon.
- Raid opponent change: **2, 6, 10, 14** Energon.
- Raid ticket refill: **10** Energon.
- Away Mission selection refresh: **5** Energon.
- Final-event spark prices (limit 21 each): T2 Alpha **80**,
  T3 Basic **40**, T3 Alpha **400**, T4 Basic **200**.
- Flash offers: **100–5,000** Energon.

### Forge

- Access: at least **13 Bots** or **8 Modules**, across more than one tier.
- Only lower-tier bots/modules can be consumed.
- Dupe-forging the same bot one tier below raises the target's max Forge
  Level from **75 to 100** (one-time).
- Class advantage boost: 2-star **75%–110%**, dupe-forged **125%**;
  3–5-star **100%–147/150%**, dupe-forged **167%**.
- Sharkticons give Sharkticon Crystal Shards instead of regular bot shards.

### Gold

- Uses: upgrade/rank-up Bots and Mods, Away Missions, Arena fights,
  Alliance Missions (formerly), Masteries.
- No numeric costs are present in the retained page text.

## Current client/server placeholders [STATIC]/[ASSUMED]

`server/data/bcg_login_data.json`:

- `evoCosts`: one entry `evo_cost_t1` (`rank=1`, `sc=1000`,
  `recipe=["evo_t1_basic"]`).
- `rarityProperties`: rarity 1 (`max_rank=2`, `max_level=20`),
  rarity 2 (`max_rank=3`, `max_level=30`).
- `staminaRegen`: `default.interval=300` seconds.
- `attributeGrowthDefs`: one linear def for `attack`/`health`;
  `curves.curve_linear` `a=1,b=1,c=0,exp=1,max=1000`.
- Quest list rewards are a repeated placeholder: `gold 2000` + `shards 100`
  for every mission; `masteryCompletionRewards`/`potentialCompletionRewards`
  are empty.

These values are **not** retail; they exist to keep the client parsing.

## Gaps (need original server data or a numeric wiki revision)

1. Rank-up and level-up Gold/XP costs per rank/level.
2. Evolution costs per tier/rank (`evoCosts` full table).
3. Forge XP curve and class-Ore payout formula.
4. Mastery costs and thresholds.
5. Mission first-completion, mastery and potential reward tables.
6. Energy per tile beyond the placeholder `1`; out-of-energy behavior.
7. Arena/Raid/Alliance entry costs and reward tables.
8. Store prices, gacha weights, crystal drop rates.

The wiki text alone cannot fill these without inventing numbers, so they stay
`[ASSUMED]`/empty and are listed in `OPEN_QUESTIONS.md`.

## What is already verified

- Quest energy and rewards are read from `quest_list.json` fields
  (`energyPerTile`, `firstCompletionRewards`, `masteryCompletionRewards`,
  `potentialCompletionRewards`) [STATIC/RUN].
- Persistence survives kill/restart for `quest_run`; energy/rewards are not
  yet exercised because the fight does not resolve (ODR blocker).
