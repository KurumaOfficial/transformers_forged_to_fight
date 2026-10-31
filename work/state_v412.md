
## 2026-10-31 v4.12 final sync

- Steps 0-3: claims 57-61; 61-character census (`data/client_character_census.json`);
  id_map 61; bot_catalog_real 61; boss_map 90/90; boss_gaps empty;
  token/key-builder doc; 7 bots without client strings.
- Step 2: BOTS grid is a client-side 59 ODR-card list; Starscream/Optimus GS
  merged-only and absent. Cards 300/0 despite live userHero 1381. `docs/bots_grid.md`.
- Step 4: async `match-resolved` schema keys found; three reward payload shapes
  tried; VICTORY/PERFECT, 22%, REWARDS empty. `docs/post_battle_flow.md`.
- Step 5: `docs/difficulty_model.md`; test vs calibrated defined; 20+20 not done.
- Step 6: level fetch payload tried; live Level 0; blocked. `docs/level_lock.md`.
- Step 7: `spec/buff_schema.md`; trigger/effect JSON blocked.
- Step 8: `spec/configs_v412.md`; only bcg-combat confirmed.
- Step 9: `docs/systems_endpoints.md` unchanged (static endpoints only).
- Step 10: check_all PASS 9/9, unit 32/32, full smoke 6/6; normal battle
  COMPLETED/LOST. Full nightly with sweep not rerun (count-only metric).
- Step 11: MASTER v4.12, FINAL_2026-10-31, FIDELITY/OPEN/COVERAGE/LEDGER.
- Next independent: BOTS list/binding, Action rewards/active-quest persistence,
  LevelRewards root key, BuffTriggerFactory, then 20+20 and nightly.
