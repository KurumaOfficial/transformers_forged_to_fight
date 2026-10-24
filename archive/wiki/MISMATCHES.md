# Manifest corrections and HTML/title mismatches (2026-10-24)

`manifest_corrections_2026-10-23.json` lists five stale hashes.  They were
corrected after the raw archive was re-fetched; the current bytes match the
corrected hashes.  However, two of the five HTML files are **not the article
for the title in their path**:

| Path | Old size | New size | Observation |
|---|---|---|---|
| `raw/fandom/revisions/0/Meet%20Your%20Makers.json` | 18046 | 18409 | revision JSON is the full "Meet Your Makers" article |
| `raw/fandom/html/0/Meet%20Your%20Makers.html` | 54970 | 1060 | current HTML is a **redirect** to `Meet_Your_Makers` |
| `raw/fandom/revisions/0/Nothing%20And%20Everything.json` | 524 | 4269 | first revision is a **redirect** to `Nothing and Everything` |
| `raw/fandom/html/0/Nothing%20And%20Everything.html` | 1078 | 56124 | current HTML is a full "Who Run the World" article |
| `raw/fandom/file_descriptions/File%3A3-Star%20Bot%20Crystal%20Shard.png.json` | 307 | 336 | description metadata changed size only |

Conclusion:

- The five corrections are **valid for the bytes currently on disk**.  The
  hashes were stale because the raw archive replacement wrote newer responses
  than the manifest recorded.
- The `Meet Your Makers` HTML is a redirect response; the revisions JSON is the
  canonical article.  The `Nothing And Everything` HTML is a different page
  (the "Who Run the World" story page), while its revisions JSON is a redirect.
  This is a title/response mismatch from the wiki move/redirect, not a server
  or APK issue.
- Raw files were **not modified** during this analysis.  If the archive is
  extended, re-fetch these two pages by canonical title and keep both the
  redirect HTML and the article revisions, so the mismatch is explicit.
- The manifest remains self-consistent: 5154/5154 entries verify against the
  current files after the corrections.

Evidence: `archive/wiki/manifest_corrections_2026-10-23.json`,
`archive/INTEGRITY.md`, the two HTML/JSON files above.
