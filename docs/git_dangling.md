# Git dangling objects — read-only audit (2026-10-25)

Nothing was deleted. `git fsck --unreachable --no-reflogs` is very slow because
of these objects, so the audit inspected the largest loose object files
directly and matched them to originals with `git hash-object`.

## Largest unreachable objects

| bytes | oid | type | content | original on disk |
|---:|---|---|---|---|
| 839,039,239 | `a7141e514f866fe5fcc8c73c2d3bf7a068ef1463` | blob | ZIP/APK, 4,133 entries, `AndroidManifest.xml` | **exact match**: `com.kabam.bigrobot_9.2.0-…apk` (same size, `git hash-object` equal) |
| 155,655,386 | `a272a891fb3d2065bf824a523f512bcb7b94f01f` | blob | `cmdline-tools.zip`, 330 entries | **exact match**: `work/android-sdk/cmdline-tools.zip` |
| 59,022,733 | `3001988c55248001c4aad40d4519c9f3048068f9` | blob | PE (`MZ`) | no equal-size file found; likely an Android SDK/emulator binary |
| 48,010,201 | `341d393ac1e7ef96d68c28f00e059263151cfb49` | blob | Kotlin compiler ZIP (24,896 entries) | likely inside `cmdline-tools.zip`; no standalone copy |
| 31,221,739 | `8c96ba7b807ba6393c531cf2fee1d46db12db23a` | blob | IntelliJ/Kotlin ZIP (19,168 entries) | likely inside `cmdline-tools.zip`; no standalone copy |
| 30,919,172 | `b907411e7d26ec375297cdc465ba2cb94513304a` | blob | ZIP of `archive/wiki/*` scripts (6,044 entries) | source files exist individually; no exact zip copy |
| 30,197,759 | `e4e34161d4ebf5a0931fe99b068f8f8e0f6897c2` | blob | PE (`MZ`) | likely SDK tool binary |
| 30,091,774 | `1f461e3663312f2c60077a8910cd153e1559ec1e` | blob | PE (`MZ`) | likely SDK tool binary |
| 29,704,063 | `6bd58f8faa8a9576b00728506b60ced842023b9f` | blob | PE (`MZ`) | likely SDK tool binary |
| 29,679,758 | `3e4ed5aa3949d5ac47a050c0645113529e2cf2b0` | blob | PE (`MZ`) | likely SDK tool binary |
| 24,401,760 | `19d9a20ace4607c46894f021a9622169c10cadc0` | blob | PE (`MZ`) | likely SDK tool binary |
| 24,297,100 | `926810aa819dd7a39aa2c12bb081359604738483` | blob | PE (`MZ`) | likely SDK tool binary |
| 23,903,641 | `4f3a2945586bc0e9fb1f7ab1b8f843a0d7c1353b` | blob | PE (`MZ`) | likely SDK tool binary |
| 20,806,785 | `945d02a2673798ac6665e1c4b50cb1112649eee2` | blob | PE (`MZ`) | likely SDK tool binary |
| 16,474,821 | `072b6bad97f7775bc6bf67b4a0bf6b21e368b8f9` | blob | R8/D8 JAR (8,166 entries) | likely inside `cmdline-tools.zip` |
| 11,192,747 | `96b0ee847ea56b50207dee33c583a474c7ce2dc5` | blob | `Il2CppDumper-win.zip`, 11 entries | **exact match**: `work/Il2CppDumper-win.zip` |
| 337,649,664 | (no valid oid) | — | `.git/objects/64/tmp_obj_IkD0Sp`, zlib header, incomplete temp | **not an object**; likely an interrupted `git add` temp |

All of the above are **unreachable** from every commit and are **not** in
`origin/master`. The APK and the SDK/Il2CppDumper zips are exact duplicates of
local originals, so pruning them loses no source.

## Why they exist

`git count-objects -vH` reports 1.51 GiB of loose objects and 322 MiB of
garbage. The timestamps cluster around the same sessions where the APK,
`cmdline-tools.zip`, `platform-tools.zip` and `Il2CppDumper` were downloaded
and an `git add` was attempted; the objects were never referenced by a commit.
The `.gitignore` later excluded `*.apk`, `work/*.zip` and the SDK dirs, but the
loose objects remained.

## Safe cleanup (requires consent)

1. Mirror backup: `git clone --mirror . <backup>.git`.
2. `git reflog expire --expire=now --all`.
3. `git gc --prune=now --aggressive`.
4. Verify `git count-objects -vH` and `git fsck --unreachable`.

This is local-only and does not touch `origin`. Do not run without the user's
approval; see `docs/git_cleanup_plan.md`.
