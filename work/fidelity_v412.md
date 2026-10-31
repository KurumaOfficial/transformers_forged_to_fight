
## 2026-10-31 v4.12

| Area | Level | Basis |
|---|---|---|
| Character census | **61 base / 122 tokens** | `data/client_character_census.json` `[STATIC]` |
| Token mapping | **61/61 mapped** | `docs/character_census.md`; 7 without strings |
| Boss map | **90/90 client ids** | `data/boss_map.json`; `boss_gaps []` |
| BOTS grid | **59 ODR cards, Starscream absent** | `docs/bots_grid.md` `[RUN]` |
| Card rating / UPGRADE | **300 / 0-0, binding gap** | live userHero 1381 vs card 300 `[RUN]` |
| Special-attack key builder | **static algorithm found** | `0xC1B154`; token must be short `[STATIC]` |
| Post-battle async | **keys found; rewards not bound** | VICTORY/PERFECT, 22%, `[RUN]` |
| Level / STORE | **fetch works, Level 0** | `docs/level_lock.md` `[RUN]` |
| Difficulty | **two modes defined; 20+20 not done** | `docs/difficulty_model.md` |
| Buff schema | **blocked** | `spec/buff_schema.md` `[STATIC]` |
| Configs | **only bcg-combat confirmed** | `spec/configs_v412.md` |
| Tests | **check_all PASS 9/9, unit 32/32, full smoke 6/6** | `[RUN]` 2026-10-31 |
| Normal battle | **COMPLETED/LOST** | damage 271.6 / 1248, HP drops `[RUN]` |
| Full nightly v4.12 | **not rerun** | check_all+smoke+battle done; BOTS sweep count metric |
