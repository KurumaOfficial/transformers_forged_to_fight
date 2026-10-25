# Wiki economy gaps (W2, 2026-10-25)

`data/wiki/economy.json` is built only from already-saved wikitext
(`data/wiki/topics/{currencies,forge,progression,crystals,mods,relics,arena,events}.json`).
It keeps `as_of_2023` and `latest` sides separately and extracts numeric lines,
but the saved pages do not provide a complete typed cost table.

## What is present

- Currencies: Gold, Energon and related pages, with numeric lines where the
  page states them (e.g., flash-offer ranges).
- Forge, progression, crystals, mods, relics, arena and events: page-level
  records with URLs, revisions, timestamps and numeric lines.

## Gaps (not invented)

- Exact upgrade cost per level/rank per bot.
- XP required per level (the client `xp_curve` arrays are in the catalog; wiki
  economy pages do not list them all).
- Rank-up/evolution resource amounts and recipes.
- Forge cost/growth per forge level.
- Mod re-roll and relic upgrade costs.
- Crystal drop chances per star/rarity.
- Energy refill cost and regeneration timing.
- Arena/event reward tables per rank.

These require either the retail server data, a complete wiki table, or
observation; they are not guessed here. `[WIKI]` pages are the source;
absence is recorded as a gap. `[ASSUMED]` values are only in the stub payloads,
not in this file.
