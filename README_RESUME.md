# Resume in 10 minutes

1. Read `STATE.md` (latest section), `OPEN_QUESTIONS.md`, `MASTER_PROMPT.md`
   (v4.5) and `report/FINAL_2026-10-25.md`.
2. Start the emulator:
   `work/android-sdk/emulator/emulator.exe -avd TFTF_AVD -no-snapshot -no-audio -gpu angle_indirect`
   (windowed is the stable mode; headless was unstable).
3. `work/emulator_watchdog.py --ensure --windowed` — checks adb, boots,
   restores `adb reverse`, installs the APK if missing, launches the app.
   `--save-snapshot tftf_home` / `--load-snapshot tftf_home` are available.
4. Start the server if needed:
   `python server/stub_server.py` (port 8080). Optional persistence:
   set `TFTF_DB=<path>` before starting.
5. Quick health: `python work/check_all.ps1` (golden + fast smoke + unit
   tests) or `powershell -ExecutionPolicy Bypass -File work\nightly.ps1`.
6. Current battle blocker: prefight works and FIGHT sends
   `/matches/activate-match/quests_fight`; the fight scene then throws
   `ArgumentNullException` from `PlayerAttributes.Init`'s `HashSet<string>`.
   `Blueprint.ModelID` was fixed by the `"m"` key; `tags`/`t` made live
   `Blueprint.Tags` non-null. No `/matches/match-loaded` yet.
   See `docs/battle_init_progress.md`.
7. Quest data: 90 missions in `server/data/quest_list.json`; detail/begin/
   movedir are built by `server/routes/quests.py`; maps use the validated
   9-tile template with per-qid `mapHash`. 70/90 bosses have a client id;
   `data/boss_gaps.json` lists the 20 gaps.
8. Tests: full smoke PASS, golden 9/9, unit 19/19. Golden is re-recorded only
   with a diff/reason in `LEDGER.md`.
9. Git: **do not push/gc/filter-repo/change remotes or user.email without the
   user's consent.** The remote is ahead/behind; local commits only. Read
   `docs/git_audit.md`, `docs/git_dangling.md`,
   `docs/git_cleanup_plan.md`.
10. Public-repo guard: `.git/hooks/pre-commit` (source
    `work/git-hooks/pre-commit`) blocks binaries, >1 MiB files, unpacked
    assets, keys and `C:/Users/` in added text. `docs/screens_ok/` is the only
    image exception.
11. Do not modify the APK, raw wiki archive, or `server/data` by hand unless
    the change is recorded in `LEDGER.md` and `FIDELITY.md`.
