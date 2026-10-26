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
