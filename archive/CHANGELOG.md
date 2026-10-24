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
