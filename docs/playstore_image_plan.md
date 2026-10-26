# Google Play / ARM64 emulator plan (Step 1.6/1.7)

`РАЗРЕШАЮ_ОБРАЗ_PLAYSTORE` is **empty** in the message, so nothing was
downloaded and no AVD was created. This is plan-only.

## A. google_apis_playstore AVD (API 30, x86_64)

### Cost

| item | estimate |
|---|---:|
| system image download | 1.2–1.6 GB |
| disk after AVD | 2–3 GB |
| download time (depends on link) | 10–40 min |
| AVD boot first time | 2–5 min |
| install APK + login | 2–5 min |

No administrator rights and no system-wide install are needed; everything is
under `work/android-sdk/` and the user AVD directory.

### Planned steps (not executed)

```
work/android-sdk/cmdline-tools/latest/bin/sdkmanager.bat \
  "system-images;android-30;google_apis_playstore;x86_64"

work/android-sdk/cmdline-tools/latest/bin/avdmanager.bat create avd \
  -n TFTF_PLAY -k "system-images;android-30;google_apis_playstore;x86_64" \
  -d pixel_4

work/android-sdk/emulator/emulator.exe -avd TFTF_PLAY \
  -no-snapshot -no-audio -gpu angle_indirect

adb reverse tcp:8080 tcp:8080
adb install -r <the same APK>
```

Then run the watchdog with `AVD=TFTF_PLAY`, save a `tftf_play_home` snapshot,
and compare `FuseODRBlocker`/`ODRManager` memory and PlayCore logcat.

### Risks

- The Play Store image is usually **not rootable** with `adb root`; the
  read-only `/proc/pid/mem` probes may stop working. Keep the current
  `google_apis` AVD for memory evidence.
- Without a Google account/sign-in, PlayCore may still not fetch packs; the
  image alone does not guarantee ODR.
- Play Protect/sideload warnings, signature mismatch, and first-boot setup
  dialogs can block automation.
- The APK is a split/base install; the Play Store may demand a license or the
  original package signature. Do not re-sign or patch.
- Emulator performance may be worse; ODR downloads still use the real network.

### Rollback

Delete only the new AVD/image under `work/android-sdk/` after user approval;
the current `TFTF_AVD` and snapshots stay untouched.

## B. ARM64 AVD (plan only)

- Image `system-images;android-30;google_apis;arm64-v8a` (or `default`), size
  ~1.2 GB; on an x86_64 host it runs under QEMU TCG (slow, high CPU).
- Benefits: native arm64 `libil2cpp.so`, `gdbserver`/`lldb-server` can attach
  without ARM translation; `adb root` may work on `google_apis` (not
  `playstore`), enabling `/proc/pid/mem` and watchpoints.
- Risks: very slow boot/battle, possible unsupported emulator image, high RAM;
  still not a Play Store/ODR fix.
- Steps: install image, create `TFTF_ARM64`, boot, adb root, push
  `gdbserver`/`lldb-server` **only after explicit approval**, attach to
  `libil2cpp.so` at the ODR/PlayCore functions, set breakpoints/watchpoints.
- This is a debugging fallback, not a data fix. Do not run without approval.
