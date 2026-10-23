# data/wiki

Parsed from `archive/wiki/raw/fandom/revisions/0/` (raw is authoritative and
untouched).

- `bots.json` — 44 bot pages: infobox, star stats, rank/level tables,
  abilities, signature tables, special attacks, synergy. Each entry carries
  `source.page`, `source.revid`, `source.url`, `[WIKI]`.
- `pages.json` — 252 other content pages (classes, status effects, modules,
  relics, crystals, currencies, missions, events, story, arena, raids, away
  missions, ...) with generic sections/tables and the same source metadata.
- `unparsed/pages.json` — content not represented structurally (Sharkticon,
  layout template) and metadata-only namespaces.

Missing cells stay missing. Hidden base stats (crit, armor, block) are not
invented; only values present in the saved wikitext/tables are stored.

## Additional analysis (2026-10-23)

- `bot_matrix.json` — 44 bots x fields, counts and missing lists.
- `id_map.json` — 59 client packs (52 bots + 7 Sharkticon variants) <-> wiki
  pages; 44 stat pages; 5 wiki-only.
- `versions.json` + `versions/<page>.json` — as_of 2023-01-13 and latest
  revision per page; 96 changed, 11 created after cutoff.
- `unparsed/pages.json` — pages not structurally parsed.
