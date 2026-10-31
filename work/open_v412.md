
## 2026-10-31 v4.12

- **BOTS grid:** client-side 59-card ODR list; Starscream/Optimus GS are
  merged-only and do not appear. Server roster add/replace has no effect.
  Cards show 300/0 despite live `BCGUserHero` 1381. Need the client list
  source and HeroData binding. `docs/bots_grid.md`.
- **Post-battle:** async `match-resolved` keys are known (`qid`, `battleId`,
  `results`, `progression`, `teamData`, `version`); three reward payload
  shapes still show empty REWARDS and 22%. Need `Action.firstCompletionRewards`
  construction and active-quest refresh/persistence.
  `docs/post_battle_flow.md`.
- **Level:** `/levelrewards/fetch` returns `status`/`levelrewards` with
  `last_awarded_level`/`nextLevelXp`/`types`; live `Level` stays 0. Need the
  exact root key/path of `LevelRewardsStatus..ctor`.
- **Special attacks:** blueprint id must be `<loc_token>_<suffix>`; current
  catalog uses asset ids, so Windblade asks `WINDBLADE` instead of `WINDB_GS`.
  7 bots have no strings. On-screen check blocked by card binding.
- **Buff:** no decoded trigger/effect JSON; no Bleed/Shield/Evade stat enum.
- **Difficulty:** two modes defined; 20+20 series not completed.
- **Tests:** check_all 9/9, unit 32/32, full smoke 6/6; full nightly not rerun.
