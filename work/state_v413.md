
## 2026-10-31 v4.13 progress

- Step 0: claims 62-64 (blueprint-id rename disproved for grid; rewards route
  partially corrected; 300/0 not caused by blueprint id).
- Step 1: pilot A renamed `windblade_gs` -> `windb_gs_5`; the BOTS card
  disappeared. Pilot B restored the asset key and set
  `characters.windblade_gs.character = "windb_gs_5"`; card returned, INFO still
  0/0. Conclusion: grid keys on asset/character id; loc token is a separate
  character field (likely `BCGCharacterData.Character`); exact JSON key open.
  `data/blueprint_id_map.json` (61 rows), `docs/blueprint_ids.md`.
- Step 2: 8 s INFO capture, 124 frames, 15.24 fps; model centroid moves
  5.2/8.5 px/frame mean, 27/46 px max; static UI crop diff 0.065, so not
  whole-screen jitter. `TuningGameplay.DefaultAnimatorScale` live 6.808;
  `PrefightScreenPresentation.GetNewScale` uses `CachedActorBounds`.
  `docs/jitter_report.md`, `docs/jitter/`. No phone.
- Tests: check_all PASS 9/9, unit 32/32, fast smoke PASS after the v4.13
  changes.
- Next independent: Step 3 rewards/active-quest persistence; Step 4
  LevelRewards root key; Step 5 BuffTriggerFactory; Step 6 20+20; Step 7
  systems; Step 8 sweep/nightly/openapi/routing.
- Push: **not performed** because the standing rules in the same queue forbid
  `git push`/remotes. All work is committed locally.
