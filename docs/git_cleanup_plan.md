# Git cleanup plan — 2026-10-25 (not executed)

No history rewrite, no force-push and no server-side deletion has been done.
This is a decision document for the user.

## 1. Local-only immediate cleanup (safe, no remote change)

Backup first:

```powershell
git clone --mirror . C:\Backup\TFTF_git_$(Get-Date -Format yyyyMMdd_HHmmss).git
```

Then remove unreachable local objects (the ~1.5 GiB of abandoned `git add`
residue, including two ZIPs and one PE):

```powershell
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

This does **not** touch `origin/master`; it only reclaims local disk. It also
removes the dangling blobs that may contain APK/unpacked material, so keep the
mirror backup until the user confirms.

`git count-objects -vH` after the operation should show a small pack instead of
1.5 GiB.

## 2. What to remove from the public tree

Minimum set for the 0.4 rule (code/spec/tests/docs only, no binary data, no
dumps of third-party/game data):

```
tests/smoke/*.png
tests/sweep/*.png
docs/evidence/**/*.png
archive/wiki/meta/**
archive/wiki/state.json
archive/wiki/manifest.json
archive/wiki/manifest_corrections_*.json
archive/wiki/raw/**
archive/wiki/*.py            # archive tooling, optional
data/wiki/**
server/data/**              # game data fixtures; keep locally or private release
```

`server/data` is required to run the stub. Recommended split:

- public repo: `server/stub_server.py`, `server/persistence.py`, schemas,
  tests, docs, and a **small synthetic fixture** with no real game dump;
- private/local: `server/data/`, `data/wiki/`, `archive/wiki/` (or a release
  artifact / private branch).

If the user wants to keep the repo private instead, the data can stay; the
decision is the user's.

## 3. History rewrite (requires explicit approval)

Use `git filter-repo` (install separately; do not install without consent):

```bash
git filter-repo \
  --invert-paths \
  --path tests/smoke \
  --path tests/sweep \
  --path docs/evidence \
  --path archive/wiki/meta \
  --path archive/wiki/state.json \
  --path archive/wiki/manifest.json \
  --path archive/wiki/raw \
  --path data/wiki \
  --path server/data \
  --path-glob 'server/data/*.bak' \
  --path-glob 'server/data/*.pre_*'
```

Personal path replacement (do it in the same rewrite, or a second one):

```text
C:\Users\gameg==>%USERPROFILE%
C:\\Users\\gameg==>%USERPROFILE%
```

```bash
git filter-repo --replace-text replacements.txt
```

Then:

1. Run the full test suite against the rewritten tree.
2. Force-push with `--force-with-lease` **only after the user approves**:
   `git push --force-with-lease origin master`.
3. GitHub may keep unreachable objects for a while; server-side GC/support is
   outside this repo and outside this task.

## 4. Decisions needed from the user

1. Public repo or private repo?
2. Remove `server/data`/`data/wiki`/`archive/wiki` from history, or keep them
   and make the repo private?
3. Rewrite history to remove `C:\Users\gameg` and the author email, or accept
   them?
4. Run the local `git gc --prune=now` now (with mirror backup), or keep the
   dangling blobs for forensic review?
5. If rewriting: force-push `master` (only branch) or keep a `legacy` branch?

## 5. Future .gitignore

Already added: `server/data/*.bak`, `server/data/*.pre_*.json`, test DBs,
`tests/sweep/*.png`. Add (after the decision) for future commits:

```
docs/evidence/**/*.png
tests/smoke/*.png
archive/wiki/meta/
archive/wiki/raw/
*.zip
*.apk
*.so
*.dll
*.exe
*.keystore
*.jks
*.pem
*.key
```

Until the decision, do not `git add -A`; add only source/spec/test/doc text.
