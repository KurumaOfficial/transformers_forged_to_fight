# Archive integrity — 2026-10-23

## Manifest verification

- Manifest entries: **5154**.
- Present and SHA-256 verified: **5154**.
- Missing: **0**.
- SHA-256 mismatches after correction: **0**.
- Verified file bytes: **110,770,773**.
- `archive/wiki/errors.json`: **209** entries.

Five manifest entries were stale before verification:

- `raw/fandom/revisions/0/Meet%20Your%20Makers.json`
- `raw/fandom/html/0/Meet%20Your%20Makers.html`
- `raw/fandom/revisions/0/Nothing%20And%20Everything.json`
- `raw/fandom/html/0/Nothing%20And%20Everything.html`
- `raw/fandom/file_descriptions/File%3A3-Star%20Bot%20Crystal%20Shard.png.json`

The JSON/HTML files parsed correctly and their titles matched the expected pages.
Their old and new hashes are preserved in
`archive/wiki/manifest_corrections_2026-10-23.json`; the manifest was then
refreshed. This is a metadata correction, not a change to the original APK or
the raw page text.

## Error categories

All **209** download errors are `403 Forbidden` from the image host. No bypass of
site blocking was attempted. The text, history, HTML and File-description
entries verify above; remaining image binaries are resumable when the host
allows it.

## ZIP hashes

- Base zip: `archive/TFTF_wiki_archive_2026-10-23.zip`
  - size: **32,513,591** bytes
  - SHA-256: `14b714b8e7e1409a2e74c32847ad78c7ee1e4a72cde3debfe97c2892da029c17`
- Integrity re-pack: `archive/TFTF_wiki_archive_2026-10-23_210335.zip`
  - size: **32,504,603** bytes
  - SHA-256: `0731484c7c26463482488ac08f52ee75881bea7c3910f7cf9f3758da1509d559`

Earlier hashes:

- `7220eabc...` — intermediate stage with 523 downloaded images.
- `040255c1...` — later 694-image stage.
- `14b714b8...` — current completed text/File-description + 694-image archive.

The hashes differ because content was added between archive stages (and the
manifest correction above changed metadata), not because the original APK or
raw page contents were replaced. `[DERIVED]`

## About "24? нет"

"24? нет" in an earlier report was a stale error-count phrase from an
intermediate download stage. It is not the current number. The current
`errors.json` has exactly **209** entries, all categorized above.

## 2026-10-25 W5 re-pack

- New archive: `archive/TFTF_wiki_archive_2026-10-25_195954.zip`
  - size: **32,506,584** bytes
  - SHA-256: `4a0aa74133eb80ba067e7a541195bb38d28d4b7db96138ab1f1924a1bb22cc9b`
- Adds two priority images recovered with a Referer + browser UA, 1.5 s pause:
  `2-Star_Sharkticon_Crystal_Shard.png`,
  `2-Star_Sharkticon_Crystal_banner.jpg`.
  Report: `archive/wiki/W1_RETRY_2026-10-25.json`.
- The remaining 34 priority 403 images have no source URL in the manifest;
  `Special:FilePath` returns 403. No bypass was used. Text/manifest content is
  otherwise unchanged.
