# Git audit — 2026-10-25

Scope: local repository `C:\Users\gameg\Desktop\TFTF`, branch `master`,
remote `origin`. No GitHub settings were opened, no tokens were used, no
history was rewritten, and nothing was deleted on the server.

## 0.1 Freeze

Per the user's instruction, **no further `git push` and no remote changes**
until the user answers. This document is a local commit only.

## Remote and branch

```
origin  https://github.com/KurumaOfficial/transformers_forged_to_fight.git (fetch)
origin  https://github.com/KurumaOfficial/transformers_forged_to_fight.git (push)
* master                ca5b867 [origin/master]
  remotes/origin/master ca5b867
```

- `master` was created with the first commit on **2026-10-21 16:21:55 +0200**
  (`2feaabf`, author `Kuruma <kurumibestwaify@gmail.com>`).
- `origin` was added by this session on **2026-10-25** via
  `git remote add origin ...`; Git does not record a timestamp for remote
  addition. The first push was `master -> origin/master` on 2026-10-25.
- The local config contains only `remote.origin.url`, `remote.origin.fetch`,
  `branch.master.remote`, `branch.master.merge`; no credentials or tokens.
- Reflog shows only the normal commit sequence; the remote-tracking ref points
  at `ca5b867`.

## Tracked / remote tree

`git ls-tree -r --long origin/master`: **557 files, 42.51 MiB**.

| top dir | MiB | contents |
|---|---:|---|
| `archive/` | 27.35 | wiki metadata/state JSON (`archive/wiki/meta/*`, `manifest.json`) |
| `data/` | 8.49 | wiki pages/versions/topics, bot stats, localization extracts |
| `docs/` | 3.73 | docs + 6 evidence PNGs |
| `server/` | 1.72 | stub, JSON payloads, persistence, backups |
| `tests/` | 0.61 | tests, golden JSON, smoke/sweep PNGs |
| `work/` | 0.19 | a few tracked helper scripts |
| `spec/`, `report/`, `notes/`, root | 0.41 | text |

Largest tracked files:

```
21.30 MiB archive/wiki/meta/allimages_tfwiki.json
 1.95 MiB archive/wiki/state.json
 1.76 MiB data/wiki/pages.json
 1.54 MiB archive/wiki/manifest.json
 1.30 MiB archive/wiki/meta/allimages_fandom.json
 0.86 MiB docs/evidence/a8/prefight_before_key_fix.png
 0.86 MiB docs/evidence/a5/prefight_before_fight.png
 0.85 MiB docs/evidence/a8/prefight_after_key_fix.png
 0.77 MiB server/data/quest_list.json
 0.74 MiB server/data/bcg_login_data.json
```

## What the history ever contained

`git rev-list --objects --all` gives 1000 objects / 566 unique paths.
Searching every path ever:

- **No APK** (`*.apk`: 0).
- **No unpacked assets** (`assets/`: 0).
- **No `libil2cpp` / `global-metadata` / `dump.cs` / `il2cpp_dump`**: 0.
- **No archive zip** (`*.zip`: 0).
- **No keystore/private key** (`*.keystore`, `*.jks`, `*.p12`, `*.pfx`,
  `*.pem`, `*.key`: 0).
- **No `.so`/`.dll`/`.exe`/`.bin`/`.dat`** tracked: 0.
- 14 tracked PNGs: `tests/smoke/*.png` (7), `docs/evidence/a5/*.png` (4),
  `docs/evidence/a8/*.png` (2), `docs/evidence/a9/fight_click_error.png` (1).
- Wiki archives are metadata/state JSON, not raw image binaries; raw files and
  zips are ignored/untracked.

### Personal paths / names

`C:\Users\gameg` appears in **58 historical objects** (tracked scripts/docs):
`MASTER_PROMPT.md`, `STATE.md`, `archive/wiki/*.py`, many `work/*.py`, etc.
This is a real personal-path leak in the public history. The author identity in
every commit is also `Kuruma <kurumibestwaify@gmail.com>`.

### Secrets / tokens

- The literal `sess_tf_stub_token_12345` is a **test fixture**, not a real
  credential. It appears in `LEDGER.md`, `STATE.md`, docs and the captured
  request.
- `Authorization`/`Bearer`/`Secret` hits are wiki filenames, story words or
  image descriptions, not credentials.
- No real API key, password, private key or session token was found in the
  scanned blobs.
- `server/data/login_response.json` contains `commander@local.test` (fixture).
- One public page metadata hit `wiki@ratin.de` (wiki author contact, public).

## Local-only garbage (not in history, not on remote)

`git count-objects -vH`:

```
count: 6736
size: 1.51 GiB
in-pack: 857
packs: 4
size-pack: 13.17 MiB
prune-packable: 0
garbage: 1
size-garbage: 322.01 MiB
```

`.git/objects` has ~1.98 GiB of files, dominated by **unreachable loose
objects** from abandoned `git add` attempts:

- `a7141e5…` — unreachable blob, 839,039,239 bytes, starts with `PK` (ZIP)
- `64/tmp_obj_IkD0Sp` — garbage temp object, 337,649,664 bytes
- `a272a89…` — unreachable blob, 155,655,386 bytes, `PK` (ZIP)
- `3001988…` — unreachable blob, 121,830,552 bytes, starts with `MZ` (PE)
- several 15–59 MiB unreachable blobs (likely APK/unpacked/asset material)

These are **not** reachable from any commit and are **not** on `origin/master`;
they are local disk residue. `git fsck` is slow because of them. They should be
pruned locally (with consent) after a backup decision.

## Violations of the 0.4 publication rule

The current remote contains, besides code/spec/tests/docs:

1. **Binary screenshots** (`tests/smoke/*.png`, `docs/evidence/**/*.png`).
2. **Wiki metadata dumps** (`archive/wiki/meta/*`, `archive/wiki/state.json`,
   `manifest.json`, ~27 MiB).
3. **Wiki/game data extracts** (`data/wiki/*`, `server/data/*.json`), which are
   dumps of third-party/game data, not stub code.
4. **Personal Windows path** `C:\Users\gameg` in tracked files.
5. **Author email** in commit metadata (normal for Git, but public).

The source code, specs, tests and prose docs themselves are fine; the data and
binary evidence need to move out of the public tree.

## Verdict

- No APK, libil2cpp, dump.cs, keystore or private key ever entered Git history
  or the remote branch. **This is the good news.**
- The remote does contain binary screenshots, wiki metadata/data dumps and a
  personal path. It should be cleaned before the repository is treated as
  publishable.
- The 1.5 GiB of local garbage is not on GitHub but should be pruned locally.

## 0.3 Cleanup plan (not executed)

See `docs/git_cleanup_plan.md` for the exact filter-repo/path list and the
decision points. No history rewrite or force-push will happen without the
user's explicit approval.
