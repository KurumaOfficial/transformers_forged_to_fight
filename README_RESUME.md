
# Resume in 10 minutes

1. Open the project root and read `STATE.md` (latest section), `OPEN_QUESTIONS.md`,
   and `report/FINAL_2026-10-24.md`.
2. Start the emulator `TFTF_AVD` and wait for `adb devices` to show
   `emulator-5554 device`.
3. Run `powershell -ExecutionPolicy Bypass -File .\resume.ps1 -Full`.
   It sets `adb reverse tcp:8080 tcp:8080`, starts `server/stub_server.py 8080`
   if needed, checks the installed APK and SHA-256, launches the app, and runs
   the full smoke + golden regression.
4. Evidence lands in `tests/smoke/latest.json` and `tests/smoke/*.png`.
   `status=PASS` means the UI flow reached the battle tile; it does **not**
   mean combat works.
5. Current hard blocker: `PreFightScreen._model` is null, so FIGHT NREs in
   `PreFightScreen.OnFight`. Team data is not the blocker (`TeamHeroes=1`,
   `localPlayer.team=1`). Read `STATE.md` §15 and `docs/memory_probe.md`.
6. Queue: A5/A6 (other battle entrances / match protocol), R2-R6, C1-C3,
   W4-W5, P2 I1-I2. Work from the first item not marked done in
   `report/FINAL_2026-10-24.md`.
7. Do not modify the APK, raw wiki archive, or `server/data` by hand unless
   the change is recorded in `LEDGER.md` and `FIDELITY.md`.
