# Netflix version plan (T4, plan only — no download)

Status: **plan only**. The Netflix build was not downloaded, unpacked or run.
The original 9.2.0 APK remains the only client used.

## Why consider it

The Netflix edition may contain a newer/cleaner `libil2cpp.so`, different
metadata, or a build with the retail service layer removed. It could help with:

- confirming the 9.2.0 IL2CPP class layout (`Il2CppClass`, `MethodInfo`) if the
  Netflix build is a similar Unity version;
- finding a real `attributeGrowthDefs`/`curves` table if the catalog is less
  stripped;
- checking whether the Netflix build has a different match/quest protocol.

## How to compare, if the user supplies it

1. Record the package name, versionName/versionCode, SHA-256 and signing cert.
2. Compare `global-metadata.dat` header/version and `libil2cpp.so` build ID.
3. Diff class/field lists for `PreFightScreen`, `PrefightScreenData`,
   `QuestBoss`, `FighterData`, `MatchManager`, `TeamData`.
4. Diff the OpenAPI/protocol strings and any `tuning` defaults.
5. Only then consider a separate worktree; never mix assets between builds.

## Risks

- Different Unity/IL2CPP version: all RVAs and offsets change.
- Netflix build may be a different game build with removed content.
- Legal/ToS and distribution risk; keep it local and do not redistribute.
- A new APK would need endpoint patching/re-signing, which changes the client.

## Decision

Do not download or use it without explicit user consent. It is not on the
critical path; the current blocker (battle-scene init) is inside 9.2.0.
