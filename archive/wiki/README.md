# Wiki archive (Part B)

Sources:

- Fandom: https://transformers-forged-to-fight.fandom.com/api.php
- TFWiki mirror: https://tfwiki.duckdns.org/api.php (only Forged to Fight pages)

Layout:

- `meta/` — siteinfo, allpages per namespace, allredirects, allcategories,
  allimages, author collection metadata.
- `raw/<wiki>/revisions/<ns>/<title>.json` — every revision (`revid`,
  timestamp, user, comment, content) in the original order.
- `raw/<wiki>/html/<ns>/<title>.html` — rendered HTML (`action=parse`), plus
  `.meta.json` with categories/templates/links/images.
- `raw/<wiki>/files/` — original image binaries (partial; 403s are recorded).
- `state.json` — resumable state (`pages`, `files`, list continuations).
- `manifest.json` — path, sha256, size, UTC time, source URL, revid.
- `errors.json` — failed pages/files; retry after the main pass.
- `unparsed/pages.json` — every saved page with reason (parser pass not run).

The raw directory is intentionally excluded from git (`.gitignore`) because it
is large. The archive is personal preservation; keep the source URL and revid
for attribution (CC BY-SA 3.0 for TFWiki, Fandom site terms).

The parser pass into `data/wiki/*.json` has not been run. Do not invent values
to fill gaps; hidden base stats (crit, armor, block) may be absent from the wiki.

## Status 2026-10-23

- 3613 Fandom pages enumerated; 817/817 non-File pages saved with full
  history+HTML; 5 File pages too; 2796/2796 File descriptions saved.
- 694/2752 image binaries saved (priority: maps/missions/UI/tables).
- TFWiki: 8 FTF pages with full history+HTML.
- Backup: `archive/TFTF_wiki_archive_2026-10-23.zip`,
  SHA256 `14b714b8e7e1409a2e74c32847ad78c7ee1e4a72cde3debfe97c2892da029c17`.
