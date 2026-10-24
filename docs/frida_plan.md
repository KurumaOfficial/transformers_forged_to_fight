# Frida plan (not executed)

Status: **plan only**. No Frida, gadget, agent, or client patch was run.
This document is for the user's decision.

## Why

The current hard blocker is not the team data. The live prefight screen has
`PreFightScreen._model == null`; `PreFightScreen.OnFight` (`0xE397BC`) NREs
before any team code. `_model` is fetched only via
`InterfaceInjector.Get<IPrefightDataProvider>` (`0x11E7640`) in
`CacheReferences` (`0xE38F08`).

A dynamic hook would answer three questions that static analysis and the
read-only `/proc/<pid>/mem` probe cannot answer cheaply:

1. Which of the 78 `_gameInterfaces` entries is `IPrefightDataProvider`, and
   which tag/implementation does the injector select?
2. Is `PrefightScreenData..ctor` ever called, and with what `PreFightParams`?
3. Does `ActiveQuest.ActivateMatch` (`0x10A0038`) get a non-empty battle id
   and hero, and why is `/matches/activate-match` never sent?

## Options and feasibility

| Option | Feasibility | Notes |
|---|---|---|
| Frida server on `TFTF_AVD` (x86_64, API 30, google_apis) | medium | `adb root` is available on google_apis; Frida server for x86_64 can attach. But the game runs the **ARM64** `libil2cpp.so` through ndk-translation, so a native x86_64 hook cannot directly instrument the translated ARM64 code. Java/IL2CPP-level hooks may still see managed methods if Frida's ART instrumentation is used, but IL2CPP is native, not ART. |
| Frida server on a rooted ARM64 device | high | The cleanest path: arm64 Frida server and arm64 `libil2cpp.so`, no translation. Requires a rooted physical device or an ARM64 emulator image with root. Not available in the current environment. |
| Frida gadget in a **copy** of the APK | medium | Unpack `lib/arm64-v8a`, add `libfrida-gadget.so`, add a `System.loadLibrary`/config entry, re-sign with uber-apk-signer. This modifies a copy of the client and would need the user's explicit consent. It also risks the Kabam checksum/anti-tamper path (`libapkprotect.so`) and signer checks. |
| Read-only `/proc/<pid>/mem` probe | **already used** | `work/read_bcg_memory.py`, `work/read_tag.py`, `work/read_injector_final.py`. No injection, no patch. Limited to reading structures with known offsets. |
| Static IL2CPP + Ghidra | **already used** | `dump.cs`, `rva_map.json`, Capstone; exact NRE branch and provider call site found. The remaining gap is runtime object identity/tag selection. |

## Proposed hooks (if the user approves)

On an ARM64 root device or a consenting gadget copy:

```js
// Resolve the IL2CPP exports, then hook by RVA + module base.
// 0xE38E4C CacheReferences, 0xE38F08 call to Get<IPrefightDataProvider>
// 0x11E7640 InterfaceInjector.Get<T>, 0xE3F734 PrefightScreenData..ctor
// 0x10A0038 ActiveQuest.ActivateMatch, 0x11F1FD0 MatchManager.ActivateMatch
Interceptor.attach(base.add(0xE38F08), {
  onEnter(args) { console.log("Get<IPrefightDataProvider> methodInfo", args[0]); },
  onLeave(retval) { console.log("provider", retval); }
});
```

Also dump:
- `InterfaceInjector._currentTag`, `_gameInterfaces` keys/values (use the
  offsets in `docs/memory_probe.md`);
- `PrefightScreenData` fields `_activeQuest`, `_currentTeam`, `_enemy`;
- `ActiveQuest.player.battleId`, `QuestUserInfo.team` count.

## Risks / constraints

- The client is to remain unmodified except the endpoint and re-sign; a gadget
  build is a **test copy**, not the playable client.
- `libapkprotect.so` sends a checksum to `/auth/login`; re-signing a gadget
  copy may be detected or destabilize the app.
- Frida on the x86_64 emulator may attach but cannot reliably hook the
  translated ARM64 IL2CPP code; results could be misleading.
- Time cost and stability; the read-only probe already answered the team
  question (count 1).
- No anti-tamper bypass, no site blocking bypass, no publication.

## Recommendation

Do **not** run Frida yet. First exhaust the read-only route:
1. resolve the 78 interface names from the runtime type handles (Mono-style
   handles, not Il2CppClass pointers);
2. test whether another injector interface with only a `default` entry also
   fails under the live `tform` tag (settings/profile screens);
3. inspect the `PrefightScreenData` ctor call sites via method-pointer tables.

If those fail, the least invasive dynamic option is a rooted **ARM64** device
with Frida server, not a gadget in the APK. Await the user's decision.
