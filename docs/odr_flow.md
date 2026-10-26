# ODR flow and FuseODRBlocker (Step 1)

## 1.1 Static structure

`[STATIC]` `FuseODRBlocker` (TypeDef 6275, `Window`):
fields `_presentation` 0x88, `_presentationSCI` 0x90, `_model` 0x98.
Window base: `_isBlocking` 0x42, `state` 0x44 (`Window.State`: 0
Uninitialized, 1 WaitingForDependencies, 2 ReadyToShow, 3 Animating, 4 Open,
5 Closed, 6 Destroying, 7 ReEntry).

`[STATIC]` `FuseODRBlockerModel` (TypeDef 6281):
`_batchedDownloadInfo` 0x30, `_activeODRDownloads` 0x38,
`_requestedODRDownloads` 0x40, `_isListeningToSparxManagers` 0x48,
`_lastPendingWads` 0x50, `_jobQueueProgress` 0x58, `_jobQueueSize` 0x5C,
`_lastOdrUpdateFrame` 0x60, `_prevDownloadingODRProgress` 0x64,
`_downloadTotalSize` 0x68, `_downloadProgressBytes` 0x70,
`_downloadStartTime` 0x78, `_prevDownloadingODR` 0x80,
`_disableBlockingReasons` 0x88, `_batchAllDownloads` 0x90.

Methods: `GetDownloadingODR(bool onlyRequired)` 0xF60FF0,
`HasRequestedODR()` 0xF610E4, `GetWadFilesProgressText()` 0xF611FC,
`DisableBlockingForReason(string,bool)` 0xF61360, `OnLoggedIn` 0xF60E70,
`Start` 0xF60F84.

`[STATIC]` `ODRManager` (TypeDef 7292, `AutoRefreshingManager`):
- `_waitingForInit` 0x60, `_waitingForAssetBundleToLoad` 0x61,
  `_waitingForWadToDownload` 0x62, `_autoDownloadWads` 0x63,
  `_autoLoadAssetBundles` 0x64, `_autoExtractAssetBundles` 0x65,
  `_loadInline` 0x66, `_autoLoadTocWad` 0x67, `_autoExtractRawFiles` 0x68,
  `_forceProcessTocWadFirst` 0x69, `_tocWadIterativeYield` 0x6A,
  `_config` 0x70, `_odrManifests` 0x78, `_odrManifest` 0x80,
  `_wadManifests` 0x90, `_wadFilenameHashMap` 0x98, `_downloadPath` 0xA0,
  `_requestedWads` 0xF0, `_downloadOdrTags` 0x100,
  `_initAndGetManifestComplete` 0x101, `_waitingForRequestedWads` 0x102,
  `_processingRequests` 0x103.
- Instance slot `0x2BF3D98 + 0xB8`, instance at `+0x60` (`get_Instance`
  0x135831C).
- `Initialize` 0x135A7A8 sets Instance, starts
  `TransitionToNewExtractPath`, sets `_config = config+0xC0`.
- Endpoint literals in `string_literals.txt`: `/odr/get-manifest` (line 1329),
  `/odr/get-published-manifests` (line 1330).

## 1.2 Tags / arena

`[RUN]` The active arena at the failing fight was `karnak`
(`assetpack/karnak/karnak_merged.assetbundle`), which is one of the nine valid
arenas. The ODR blocker model has **no tag list**; it works with
`ODRInfo`/`WadDownloadInfo` entries (`Name`, `FileSize`, `Url`,
`DownloadType`). There is no evidence that `theme`/`todIndex`/`mapOverride`
selects a non-existent ODR tag in this flow.

`[RUN]` `sideswipe_gs.assetbundle` is present in the APK:
`assets/assetpack/sideswipe_gs_odr/sideswipe_gs.assetbundle` (4,168,275 bytes).
So this is not a missing character pack. The battle requested it through
`assetPackName: default, path: assetpack/sideswipe_gs_odr/sideswipe_gs.assetbundle`.

## 1.3 Server endpoints

`[RUN]` `server/requests.jsonl` contains **no** `/odr/*` requests, no `/cdn`
requests, and no WAD/manifest request. The client never asked the stub for an
ODR manifest. The `ODRManager` state confirms this:
`_odrManifests` count 0, `_wadManifests` count 0, `_requestedWads` count 0,
`_receivedDataFromServer=0`, `_initAndGetManifestComplete=0`.
`_tocWadProcessed=1`; `_odrManifest=None`.

Therefore a server-side minimal `/odr/*` response cannot fix the current
state by itself: the client has not reached the request. The routes are still
documented/added as `[ASSUMED]` for later.

## 1.4 Live blocker state (2026-10-26)

`[RUN]` `work/dump_odr_blocker.py`:
- Window `FuseODRBlocker` state **4 (Open)**, `_isBlocking=1`, `wasActive=1`.
- `_model`: `_activeODRDownloads` count 0, `_requestedODRDownloads` count 0,
  `_lastPendingWads=None`, `_jobQueueSize=0`, `_downloadTotalSize=0`,
  `_prevDownloadingODR=None`, `_disableBlockingReasons=empty`,
  `_batchAllDownloads=1`, `_isListening=1`.
- `_presentation` `TformODRBlockerPresentation`, `_presentationSCI` non-null.
- Window stack at the same time: `HeroesScreen` state 4 (Open),
  `TransformersMenuBar` state 4, `FuseSystemMessageOverlay` state 4,
  `SocialOverlay` state 4, `TutorialAreaIndicatorOverlay` state 4,
  `FuseLoadingScreen` state 5 (Closed), `FuseODRBlocker` state 4 (Open).
- There is no `HudScreen` in that stack; the app is on the BOTS/Heroes screen,
  not in the battle, and the blocker is global.

`[RUN]` 10-minute wait (18:57–19:08) produced no change. Back key twice did not
close it. All 12 BOTS taps in the nightly sweep hit the blocker
(`popup_error=True`), which explains the "popup error" symptom; it is not a
card popup bug.

`[RUN]` PlayCore logcat: `AssetPackServiceImpl getPackStates([UnityDataAssetPack])`
and `BIND_ASSET_MODULE_SERVICE ... com.android.vending not found`. The
sideloaded APK has no Play Store service; the Play Asset Delivery status for
the Unity data/streaming packs cannot complete. This is consistent with a
global ODR/asset-pack init wait, not an arena tag.

## 1.5 Cheap experiments

- **Long wait:** done (>10 min, 18:57–19:08); blocker unchanged.
- **Nine arenas:** not run. The blocker is global on `HeroesScreen` with no
  tag list; changing `theme`/`todIndex` of a quest cannot clear a blocker that
  is already open outside the battle. This hypothesis is **not supported** by
  the live model; do not spend 9 runs until the global blocker is explained.
- **`/odr/*` responses:** no request is made; an empty manifest has no effect
  yet. A stub is added for completeness and future runs.

## 1.6 Conclusion / next

The blocker is **client/asset-pack initialization**, not a missing arena tag
and not a missing character bundle in the APK. The most likely causes are:

1. Play Asset Delivery (`UnityDataAssetPack`/`UnityStreamingAssetsPack`)
   cannot bind to a Play Store service on the sideloaded emulator, so the
   global pack status never completes.
2. `ODRManager.InitAndGetManifest` never receives a manifest
   (`_receivedDataFromServer=0`, `_initAndGetManifestComplete=0`), and the
   blocker waits for it.

Data-only options to try next (planned, not yet proven):
- provide a valid **prelogin/postlogin ODR manifest** at the path/URL the
  native layer expects (not the `/odr/*` Unity route, since no Unity request is
  sent);
- provide Play Asset Delivery **pack metadata/status** compatible with a
  sideloaded install (if the Java layer can be satisfied by a local pack);
- only then vary arenas/quest tags.

Do not patch the client. If the Play Core service is the hard requirement, this
is a hard asset blocker and belongs in OPEN_QUESTIONS with the ODR asset-pack
request to the user.
