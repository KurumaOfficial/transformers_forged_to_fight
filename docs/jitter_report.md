# Jitter report (Step 2, v4.13) - first measurement

Status: **measurement started; root cause not proven.** The emulator capture is
15.24 fps and the showcase model moves; the UI itself is stable, so this is not
whole-screen capture jitter. A real ARM phone was not available
(`ТЕЛЕФОН_ARM_ПОДКЛЮЧЁН` empty).

## Measurement

- Device: `TFTF_AVD`, `swiftshader_indirect`.
- Scene: BOTS -> Windblade -> INFO showcase (idle model, no battle).
- Capture: `adb shell screenrecord --time-limit 8 --bit-rate 8000000`.
- File: `work/jitter_info.mp4 (local capture; not committed: >1 MiB pre-commit limit)`; frames: 124; container fps: **15.24**.
- Metric: red-mask centroid and bbox of the model in the left showcase area
  (`x 200..980`, `y 80..980`), one sample per decoded frame.

| metric | value |
|---|---:|
| frames with model | 124 |
| duration | 8.136 s |
| container fps | 15.24 |
| centroid dx mean abs | 5.20 px/frame |
| centroid dy mean abs | 8.48 px/frame |
| centroid dx max abs | 27.39 px |
| centroid dy max abs | 45.68 px |
| high-pass x std | 31.17 px |
| high-pass y std | 34.87 px |
| bbox width range | 654..780 px |
| bbox height range | 780..900 px |
| static UI crop frame diff | **0.065 mean** (0.451 max) |
| black-region noise | 0.426 mean |

The static UI crop is stable, while the model mask moves. The model has an
idle animation, so the centroid motion is **not automatically jitter**; it is
consistent with low-FPS idle animation plus possible root motion. The bbox
change of 126 px width / 120 px height is large for a pure idle pose and needs
a second scene (prefight/battle) and a higher-fps capture.

Data: `docs/jitter/jitter_info.json`, `docs/jitter/jitter_info.csv`,
`docs/screens_ok/jitter_info_plot.png`.

## Static audit

- `TuningGameplay.DefaultAnimatorScale` live **6.808** (`0x58`, raw float).
  This is suspicious: it is the only global animator scale and is not a normal
  1.0. It is a client prefab value, not in `bcg-combat`; do not overwrite
  blindly.
- `TuningGameplay.MeleeRangeMod` live **0** (valid no-modifier value).
- `PrefightScreenPresentation.GetNewScale` (`0xE47314`) calls
  `CachedActorBounds.GetActorSize(ModelID)` and only scales down if the actor
  size exceeds the screen threshold (`+0x128`/`+0x12C`). Missing/zero cached
  bounds for a merged/ODR model would change the scale branch.
- Root motion is enabled/disabled through `Animator.applyRootMotion`
  (`setter` at `0x?`); `PlayerController.ActionFlags.RootMotion = 6` is used
  for movement. No server-side tuning field for interpolation/damping was
  found in `Tuning`/`TuningGameplay`.
- The 95 zero/empty `Tuning` fields (v4.11 audit) do not include a camera
  smoothing/damping field; the only scale-related live value is
  `DefaultAnimatorScale=6.808`.

## Matrix still to capture

| scene | Windblade | Bumblebee | Rhinox | Starscream |
|---|---|---|---|---|
| hub | not captured | not captured | not captured | not captured |
| BOTS INFO | measured (above) | not captured | not captured | not captured |
| prefight | not captured | not captured | not captured | not captured |
| battle idle/move/hit | not captured | not captured | not captured | not captured |
| victory | not captured | not captured | not captured | not captured |

## Next

1. Capture the same 8 s in prefight and battle at the highest available fps;
   compare high-pass centroid/bbox.
2. Repeat on a second model (Rhinox) and with `_lw` if a scene exposes it.
3. If `DefaultAnimatorScale`/`CachedActorBounds` differ between jittering and
   stable bots, fix the data; otherwise report emulator frame-rate as the
   primary cause. No client patch.
