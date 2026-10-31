import json, os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"."
W = os.path.join(ROOT, "archive", "wiki")
s = json.load(open(os.path.join(W, "state.json"), encoding="utf-8"))
m = json.load(open(os.path.join(W, "manifest.json"), encoding="utf-8"))
e = json.load(open(os.path.join(W, "errors.json"), encoding="utf-8"))
matrix = json.load(open(os.path.join(ROOT, "data", "wiki", "bot_matrix.json"), encoding="utf-8"))
idmap = json.load(open(os.path.join(ROOT, "data", "wiki", "id_map.json"), encoding="utf-8"))
vers = json.load(open(os.path.join(ROOT, "data", "wiki", "versions.json"), encoding="utf-8"))
text = f'''# COVERAGE_WIKI

## Fandom archive

- Enumerated: **3613** = **817 non-File + 2796 File**.
- Full history + HTML: **822** = **817 non-File + 5 File**.
  The [DERIVED] hypothesis is confirmed: every non-File page is saved.
- File descriptions (latest revision): **2796/2796** in
  `archive/wiki/raw/fandom/file_descriptions/`.
- Revisions stored: **8985**; HTML snapshots: **830**.
- allredirects=20, allcategories=80, allimages=2752.
- Image binaries: **{len(s['files'])}/2752**; **{len(e)}** errors
  (mostly static.wikia 403, no bypass). Remaining URLs are resumable.
- Manifest: **{len(m)}** entries; state: `archive/wiki/state.json`.

## TFWiki mirror

- 8 FTF pages with full history + HTML: `Forged to Fight`,
  `Transformers: Forged to Fight`, `Crossfire`,
  `Crossfire (Forged to Fight)`, `Generations`, `Prime Suspect`,
  `Magnus Opus`, `Crossfire (Prime)`.

## Extensions

- Fandom: Scribunto=yes, Cargo=no; `Module:` (ns 828) = 0 pages.
- TFWiki: Scribunto=no, Cargo=no.

## Parsed game data

- **44 bots** — `data/wiki/bots.json`: infobox, star HP/Attack/rating,
  rank/level tables, abilities, signature tables, special attacks,
  synergy; source page/revid/url/[WIKI].
- **252 pages** — `data/wiki/pages.json`: classes, status effects, mods,
  relics, crystals, currencies, missions, events, story, arena, raids,
  away missions; generic sections/tables with source.
- **Quality matrix** — `data/wiki/bot_matrix.json`: {matrix['total_bots']}
  bots; counts: {json.dumps(matrix['counts'], ensure_ascii=False)}.
  Missing lists are in `matrix["missing"]`.
- **ID map** — `data/wiki/id_map.json`: **{idmap['client_pack_count']}**
  client packs (**{idmap['non_sharkticon_client_count']}** bots +
  **{idmap['sharkticon_pack_count']}** Sharkticon variants), **44** wiki
  stat pages; {idmap['unmatched_client_count']} client packs without a
  wiki page. Wiki-only: {", ".join(idmap['wiki_without_client'])}.
- **Version sets** — `data/wiki/versions.json` + `versions/<page>.json`:
  cutoff **{vers['cutoff']}**; {vers['pages_analyzed']} pages analyzed;
  **{vers['changed_count']}** changed; **{len(vers['created_after_cutoff'])}**
  created after cutoff: {", ".join(vers['created_after_cutoff'])}.
- **Unparsed** — `data/wiki/unparsed/pages.json`: Sharkticon (no numeric
  table), layout template, and metadata namespaces. File descriptions are
  archived but not parsed as game data.

## Caveats

- Hidden base stats (crit/armor/block) are often absent from wiki tables;
  they are not invented.
- Regex parser may miss unusual tables; raw wikitext is authoritative.
- OneDrive collection is auth-gated (`isAuthenticated:false`); not downloaded.
- Backup ZIP path/hash are below; regenerate after future downloads.

## Backup

- ZIP: `archive/TFTF_wiki_archive_2026-10-23.zip`
- SHA256: `PENDING_REGENERATE`
'''
open(os.path.join(ROOT, "COVERAGE_WIKI.md"), "w", encoding="utf-8").write(text)
print("coverage updated", len(s["files"]), len(e), len(m))
