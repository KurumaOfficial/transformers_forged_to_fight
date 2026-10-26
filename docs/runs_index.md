# Run index (5.4)

Heavy artifacts stay outside git; this index points to them. All times are
2026-10-26 local/UTC from the captured logs.

| run | purpose | evidence | result |
|---|---|---|---|
| 17:10 | baseline quest fight (story_act1_ch4_m2) | `tests/smoke/latest.json`, `work/a9_full_stack.txt` | NRE `PlayerAttributes.Init` before fix |
| 17:38-17:44 | 4-run player/boss matrix | `work/battle_matrix.jsonl` | 3 NRE; 1 navigation failure (`kabam_rhinox`) |
| 17:48 | held activate-match; pre-battle scan | `work/hold_activate_scan.txt` | no fighters before response; pre-battle class slot uninitialized |
| 17:53-18:07 | stop probes at 1.5-3.2 s | `work/stop_probe.txt`, `work/stop_logcat.txt` | player OK; enemy component not yet present; crash ~2.6 s after request |
| 18:10 | first null-safe blueprint run | `tests/smoke/latest.json` | NRE still present (character keys added later) |
| 18:14-18:24 | post-fix battle | `work/after_fix2.png`, `work/probe_fightdata.py` output | no NRE; `BattleArbiterMainState`, fighters spawned |
| 18:25-18:35 | ODR/loading inspection | `docs/battle_started.md`, `work/battle_now.png` | `FuseLoadingScreen`/`FuseODRBlocker` above HUD |
| 18:4x | live persistence | `work/live_persistence_test.py`, `work/persist_live.db` | `quest_run=1` before/after kill/restart |
| nightly | `work/nightly.ps1` full | `work/nightly/nightly_*.log` | see latest log (full smoke + 59-bot sweep) |
| smoke | `work/smoke_test.py --plus --fight` | `tests/smoke/latest.json`, `tests/smoke/*.png` | PASS, `prefight_detected=true` after fix |
| golden | `work/golden_regression.py` | `tests/golden/*.json` | 9/9 PASS after re-record |

## Storage rules

- `work/`, `tests/smoke/*.png`, `work/nightly/` and the SQLite DB are outside
  the tracked source; the pre-commit hook blocks binary/large files.
- Do not add run videos/screenshots to git; keep them in `work/` or an external
  evidence directory.

## Latest run snapshot

`[RUN]` `runs/2026-10-26_232903/` contains `requests.jsonl`, `logcat.txt`,
`smoke_latest.json`, `sweep_59.json`, `nightly.log`, and the first 20 smoke
screenshots. Index: `runs/index.json`. `runs/` is outside git.
