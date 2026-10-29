# Changelog (2026-10-26)

## Battle

- Found the real `PlayerAttributes.Init` null: `Blueprint.BaseRangedDamageType`
  (character field `BCGCharacterData +0x48`), not `Tags`.
  `DamageType..ctor` tail-calls `HashSet<string>..ctor`.
- Fixed every character/blueprint damage list; added `bumblebee_cin_dotm`
  blueprint alias.
- Battle now reaches `BattleArbiterMainState` with two `PlayerController`s and
  MoveSets. `FuseODRBlocker`/asset-pack init remains the playable-fight blocker.

## Quests

- 3 Bumblebee DOTM boss ids changed from character id to
  `bumblebee_cin_dotm_2`.
- Act 4 I/II bosses filled from the wiki revision: 81/90 boss ids, 9 Starscream
  gaps (all outside 9.2.0).
- Added `[ASSUMED]` `nemesisprime_gs_voyager2015` fallback for Starscream
  experiments; never labelled as the original.

## Data / R2 / R1

- R2 client formula decoded (`spec/rating_formula.md`), 6 tests.
- Interval LP on raw HP/ATK is infeasible globally and per rank/level
  (`data/wiki/rating_lp.json`); parser audit 20 pages has 0 numeric misparses.
- R1: 37 WIKI/table, 22 ASSUMED; 2 anchored with star-3 + global ratio (10%),
  20 class-median priors (25%). `docs/stat_coverage.md`.
- `docs/bot_matrix.md`, `data/wiki/bot_matrix_full.json`.

## Infrastructure

- SQLite live persistence across kill/restart (`docs/persistence_live.md`).
- Smoke `battle_checks` and open xfails; golden re-recorded 9/9.
- Nightly fixed to report FAIL/PARTIAL instead of exit-code PASS; actual
  check_all PASS, full smoke FAIL, BOTS 12/59 (`docs/nightly_2026-10-26.md`).
- Git cleanup runbook and hook audit (`docs/git_cleanup_runbook.md`,
  `docs/hook_audit.md`); no push/gc/filter-repo.
- Docs zip/integrity generated separately in `work/archive/` (outside git).

## Blockers

- `FuseODRBlocker` / Play Asset Delivery init on sideloaded emulator.
- Starscream 9.2.0 pack absent.
- R2 server-side rating split absent.
- 34 wiki images (Wayback 404/503 in the tried variants).

## S1 correction

- `[RUN]` `work/sweep_bots59.py` reached **59/59** (5 pages, 0 info errors,
  0 NRE). The old 12/59 note is superseded; `popup_error` is a transition-frame
  metric, not an NRE.
- `nightly.ps1` default is now fast quest smoke (`--plus --fight`) + 59-card
  sweep; `-Full` keeps the full-mode experiment.

## Nightly

- 21:19 default nightly: **PASS** — check_all PASS, smoke PASS
  (`activate_match=true`), BOTS 59/59. Log
  `work/nightly/nightly_2026-10-26_211947.log`.
- 19:48 run remains historical: old 12-card sweep, full smoke FAIL.

## 2026-10-29

- Hidden player stats sourced from quest team payload; live Armor 50/Crit 0.1/
  CritDamage 1.5/Block 0.5/ManaGain 1.0.
- AttackValueData keys and `attack_percent` fixed; Light DamageRating 0.7.
- ODR overlay no longer blocks input; battle visible/controllable.
- New blocker: `_attack.Get()=0` while display `_value=115`; all damage 0.
- Routing split (auth/matches/odr), tuning field table, match schemas, economy
  and post-battle plan, ability blocker, nightly 2026-10-29 PASS.
- Final report `report/FINAL_2026-10-29.md`, MASTER_PROMPT v4.9, docs archive
  `TFTF_docs_2026-10-29_201026.zip`.
