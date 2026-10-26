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
