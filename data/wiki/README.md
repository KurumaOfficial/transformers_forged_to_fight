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
