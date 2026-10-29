# Post-battle evidence, 2026-10-29

Status: **win and loss both reached `/matches/resolve-match` and returned to
the quest map.** This is the first time the full kill -> resolve -> map loop
was observed.

## Loss path `[RUN]`

- fight: Bumblebee vs Sideswipe, `story_act1_ch4_m2`.
- `HitResultData`: `Flags=129`, `AttackLevel=1`, `DamageRating=0.7`,
  `Damage=64.4` after the `bcg-combat` config fix.
- K.O. screen, then `POST /matches/resolve-match/quests_fight` with
  `results={"result":"LOST"}`, `enemyHealth=1`, player HP 0, enemy HP 1050.
- The client returned to the quest map (22% explored).
- Evidence: `work/dmg1.png` (K.O.), `work/ko2.png` (map),
  `resolve_request.json` (loss body).

## Win path `[RUN]`

- test helper: `work/weak_enemy.flag` sets server-generated enemy HP/attack
  to 1; **not a normal-data run**, only to make the win/reward path reachable.
  Remove the flag for normal tests.
- `POST /matches/resolve-match/quests_fight` with
  `results={"result":"WON"}`, `enemyHealth=0`; player HP 1021.9, enemy HP 0;
  player damage 80.5.
- The client returned to the quest map. Current map response
  (`match_resolve_response.json`) did **not** mark the tile cleared or show
  rewards; the response needs `progression`/`results`/`teamData` (and probably
  `battlecomplete`/`questcomplete` async), as described in
  `docs/post_battle_quests.md`.
- Evidence: `work/winA.png` (fight), `work/winB.png` (map),
  `resolve_win.json` (full request body).

## What this proves

1. ODR/loading is not blocking the fight.
2. Armor DR constant `ArmorRatingConstant` from
   `missionsconfig.configs["bcg-combat"]["armor_break"]=200` turns damage from
   0 to 64.4; the tuning key/default mapping is real.
3. Death/K.O., `resolve-match`, and return-to-map all work.
4. Remaining post-battle work is server response/async data, not client code.

## Normal win (no weak-enemy test data) `[RUN]`

`work/battle_step.py` (normal server data, automatic attack taps) produced a
**WON** resolve: player HP 300.2, enemy HP 0, player damage 1069.5, enemy
damage 749.8. This supersedes the earlier test-only win. Evidence:
`resolve_win_normal.json`, `tests/smoke/battle_step.json`, nightly
`nightly_2026-10-29_233256.log`.
