# Archive changelog

## 2026-10-24

- Analysed the five stale-hash corrections in
  `wiki/manifest_corrections_2026-10-23.json`. The corrected hashes match the
  current bytes. Two HTML files are redirects/other pages relative to their
  revision JSON; documented in `wiki/MISMATCHES.md`. Raw files untouched.
- `data/quests_real.json` generated from the archived `Story` page and eight
  individual act pages: 66 Story missions in 4 acts, plus 24 missions in
  `Awaken and Corrupt` and 3 missions each in three other act pages. Only
  names/boss strings present in wikitext are used.
- `data/wiki/id_map.json`: five wiki-only pages analysed. `Optimus Prime`
  maps to `optimusprime_cin_tf` under the variant title `Optimus Prime (MV1)`;
  `Soundblaster/Tactician` is a class variant absent from 9.2.0; Chromia,
  Dead End and Starscream have no 9.2.0 client pack.

## 2026-10-25

- W1 retry: 2 priority images recovered (`2-Star_Sharkticon_Crystal_Shard.png`,
  `2-Star_Sharkticon_Crystal_banner.jpg`) with Referer/UA and 1.5 s pause.
  34 priority images remain 403 or lack a manifest URL; `Special:FilePath` is
  403, so the retry stopped. No bypass.
- W5: new archive `TFTF_wiki_archive_2026-10-25_195954.zip`,
  32,506,584 bytes, SHA-256
  `4a0aa74133eb80ba067e7a541195bb38d28d4b7db96138ab1f1924a1bb22cc9b`.
