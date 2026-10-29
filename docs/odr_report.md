# ODR report (Step 1.9)

## Known

- `[RUN]` `FuseODRBlocker` is **Open** (state 4) with 0 active/requested ODR
  downloads, no pending WADs, `_batchAllDownloads=1`; this is global (seen on
  `HeroesScreen`, not only the battle).
- `[RUN]` `ODRManager`: toc processed, `_odrManifests=0`, `_requestedWads=0`,
  `_odrManifest=None`, `_receivedDataFromServer=0`,
  `_initAndGetManifestComplete=0`.
- `[RUN]` No `/odr/*`, `/cdn`, WAD or manifest request reaches the stub.
- `[STATIC]` Normal `ODRManager.Initialize` does not call
  `InitAndGetManifest`; `EnsureManifest` -> `WaitForTOC` ->
  `ODRAPI.GetManifest` -> `/odr/get-manifest` is lazy. The download-all debug
  coroutine is the only found caller of `InitializedAndLoadedCoroutine`.
- `[RUN]` PlayCore logs `getPackStates([UnityDataAssetPack])` and
  `BIND_ASSET_MODULE_SERVICE ... com.android.vending not found`.
- `[RUN]` The battle character bundle `sideswipe_gs.assetbundle` is present in
  `assets/assetpack/sideswipe_gs_odr`; the arena is `karnak`, valid. The
  blocker is not an arena-tag or missing-character-bundle issue.

## Unknown

- Exact `AssetPackState`/`PackDriver`/`PlayAssetRegistry` state for
  `UnityDataAssetPack`/`UnityStreamingAssetsPack` (the Java layer may not
  expose it to `/proc`).
- Whether a Google Play image without an account changes the PlayCore state at
  all.
- Whether a data-only flag disables the blocker. No such flag was found; if
  one is found, it is **plan-only** until the user approves.

## Options and cost

| option | cost | expected result | risk |
|---|---|---|---|
| google_apis_playstore AVD (API 30 x86_64) | 1.2–1.6 GB, 10–40 min | PlayCore may bind; may still need account | high; no root/memory probes |
| ARM64 AVD + gdbserver/lldb (plan only) | 1.2 GB, slow TCG | native breakpoints on ODR/PlayCore | high CPU; needs approval |
| data-only ODR manifest | low | no request today, so no effect | low but unproven |
| user provides ODR/asset packs | depends | directly removes the missing pack | needs source/licence |
| disable PlayCore/ODR via data | low | blocker closes if a safe flag exists | must not change behavior; not found |

## Recommendation

Do not spend more runs on 9 arenas: the blocker is global and the arena is
valid. Next useful step is a **Play Store image** (permission was empty, so
not executed) or a **rooted ARM64 debugger** plan. Until then, the battle
track is blocked; the rest of the queue is unaffected.

## 1.10 Data-only ODR tuning flags (plan only, not applied)

`[STATIC]` `Tuning` (TypeDef 9463) exposes ODR switches at +0x360..0x368:

| field | live value [RUN] | note |
|---|---:|---|
| `ODRForceDownloadAll` | 0 | force all ODR downloads |
| `ODRForceDownloadAllPreTutorial` | 0 | |
| `ODRShowProgressMB` | 1 | UI |
| `ODRShowTimeEstimate` | 1 | UI |
| `ODRForceDownloadAssetListPreTutorial` | 0 | |
| `ODRAllowNative` | 1 | native ODR path allowed |
| `ODRAssetListForForcedDownload` | empty/unknown | string |

`Tuning.LoadTuningData` (`0x14233EC`) applies these by field name through
`TuningManager.Apply`; `/tuning` can therefore set them in principle. This is a
**client-data flag** and is not applied. In particular, setting
`ODRAllowNative=0` is only a hypothesis for changing the ODR path; it must not
be tried without explicit consent. The live value is already 1, so the blocker
is not simply "native ODR disabled".

Full field table: `spec/tuning_keys.md`.

## 2026-10-29 update: the overlay is not a permanent input blocker

`[RUN]` After the latest runs the battle scene is visible and controllable:
swipes increment the HITS counter, the HUD is drawn, and the camera follows
the player. `dump_odr_blocker.py` still finds the `FuseODRBlocker` window/model
(0 active/requested downloads, no pending WADs), but no loading overlay covers
the HUD in `BattleArbiterMainState`. The earlier "input blocked by the blocker"
conclusion was therefore too strong; the overlay is transient/state-dependent.

The battle still does not resolve, but the cause is **zero damage**, not ODR:

- `[RUN]` `HitResultData` after an enemy hit: `Flags=129` (Hit+LastHit),
  `AttackLevel=1`, `Damage=0.0`, `DamageRating=0.7`.
- `[RUN]` `PlayerAttributes._attack` is a `StatAttribute`; its visible/plain
  `_value` is 115.0, but `Get()` (which reads the `FastSafeFloat` safe value)
  returns 0.0. `GetDamageInflicted` multiplies by that value, so every hit is 0.
- `[RUN]` The attack-value lookup itself now works after adding the
  `Light/Medium/Heavy/Ranged/Special*` keys and the literal `attack_percent`
  key: `DamageRating` became 0.7 for a Light hit (was 0 before).
- Adding `class_power: 1.0` to the team/details did not change the result;
  `ClassPower` is 1.0 live but `_attack.Get()` is still 0.

This is a **client stat initialization/commit issue**, not a missing server
field and not a reason to patch client code. It is recorded in
`OPEN_QUESTIONS.md` and `STATE.md`; the ODR track stays blocked by the lack of
Play Asset Delivery for the loading path, but it no longer explains the
no-death/no-resolve outcome.

## 2026-10-29 correction: the zero-damage cause

The earlier "`_attack.Get()` safe value is 0" statement was a decoding error:
IL2CPP arrays store elements inline at `+0x20`; the correct value is 115 and
the hash is valid. The real zero-damage cause was
`TuningGameplay.ArmorRatingConstant=0` (missing `bcg-combat` config), which
made armor 50 give 100% damage reduction. The combat loop now reaches K.O.,
`resolve-match` and return-to-map. Full details: `docs/damage_pipeline.md`;
evidence `docs/evidence/post_battle_2026-10-29/`.
