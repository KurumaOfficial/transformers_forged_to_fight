
## 2026-10-31 v4.13 Step 0 corrections

| # | Claim | Status | Evidence |
|---:|---|---|---|
| 62 | The blueprint id must be the short loc token (`windb_gs_5`) | **disproved for the grid** | Renaming `windblade_gs` -> `windb_gs_5` removed the Windblade BOTS card entirely; restoring the asset id returned it. The loc token is a separate character field, not the blueprint key. `[RUN]` `docs/blueprint_ids.md`, `docs/evidence/blueprint_pilot/`. |
| 63 | Rewards are not applied because only the resolve result route was used | **partially corrected / still open** | Async `match-resolved` keys are confirmed (`qid`, `battleId`, `results`, `progression`, `teamData`, `version`), but three reward payload shapes still show empty REWARDS and 22%. The remaining cause is `Action.firstCompletionRewards`/active-quest refresh, not the route alone. `[RUN]` `docs/post_battle_flow.md`. |
| 64 | The 300 card rating and 0 HP/ATK are caused by the blueprint id | **not confirmed** | After restoring the asset key and setting the character token, the card still shows 300 and INFO still 0/0. The blueprint rename only removed the card. `[RUN]` `docs/blueprint_ids.md`. |
