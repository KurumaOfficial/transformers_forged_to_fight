
## 2026-10-31 v4.12

- **Census:** 61 base characters, 122 tokens, 59 ODR + 2 merged, 923 moves;
  `data/client_character_census.json`.
- **Tokens:** 61/61 mapped; 7 bots without client strings; key builder uses
  `<loc_token>_<suffix>` (`docs/special_attack_tokens.md`).
- **Boss map:** 90/90 quests have a client id; 9 Starscream bosses fixed;
  `boss_gaps []`.
- **BOTS:** 59 ODR cards, no Starscream; card 300/0 is a binding gap.
- **Post-battle:** async schema keys found; rewards/tile/progress still empty.
- **Level:** fetch payload tried; live Level 0.
- **Tests:** check_all 9/9, unit 32/32, full smoke 6/6; normal battle
  COMPLETED/LOST with wiki stats.
