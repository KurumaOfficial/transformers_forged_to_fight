# Git cleanup runbook (plan only — do not execute without consent)

Scope: local repository only. No command in this file is executed by the
agent. A mirror backup and an explicit user decision are required first.

## Preconditions

1. `git status --short` is clean or the intended changes are committed.
2. `git log --oneline --decorate -5` and `git rev-parse master origin/master`
   are recorded.
3. A mirror backup exists outside the repository:
   `git clone --mirror . <backup-dir>/tftf-<date>.git`.
4. The backup is verified with `git fsck --full` and `git count-objects -vH`.

## A. Remove unreachable objects (APK/SDK/temp blobs)

Current state (read-only): `.git` has ~1.5 GiB of unreachable loose objects;
the largest are exact copies of the local APK, `cmdline-tools.zip`,
`Il2CppDumper-win.zip`, plus a 337 MB invalid temp. See
`docs/git_dangling.md`.

Commands:

```
git count-objects -vH
git reflog expire --expire=now --all
git gc --prune=now
git fsck --unreachable --no-reflogs
git count-objects -vH
```

Expected: loose size drops to a few MB; `fsck` lists no APK/SDK blobs. If a
needed blob disappears, restore the mirror backup (step C-rollback).

Rollback: `git clone <backup-dir>/tftf-<date>.git restored` and use
`restored` as the repository.

## B. Rewrite history (PNG, wiki metadata, personal path, emails)

Only after A and a second backup. Use `git filter-repo` (not `filter-branch`).
The remote currently contains binary screenshots, wiki dumps and a personal
path; the user has not approved a rewrite.

Dry-run inventory:

```
git log --all --name-only --pretty=format: | sort -u > /tmp/history-paths.txt
git log --all --format='%ae <%ce>' | sort -u
```

Rewrite (example; adjust the path list from the audit):

```
git filter-repo --invert-paths \
  --path-glob '*.png' --path-glob '*.jpg' \
  --path 'archive/wiki/raw' --path 'work/unpacked' --path 'work/il2cpp_dump' \
  --path 'com.kabam.bigrobot_9.2.0-123129100_minAPI23(arm64-v8a,armeabi-v7a)(nodpi)_apkmirror.com.apk'
```

For the personal path and emails, use `--replace-text` / `--mailmap` with a
reviewed mapping file. **Do not** rewrite `origin/master` unless the user
explicitly approves a force-push.

## C. Force-push (requires explicit consent)

```
git push --force-with-lease origin master
git ls-remote origin refs/heads/master
```

`--force-with-lease` is mandatory; never use a bare `--force`. Verify the
remote commit, then ask all other clones to re-clone.

Rollback: restore from the mirror backup and force-push the old commit only
with the user's approval.

## D. Never run without consent

`git push`, `git gc --prune`, `git filter-repo`, `git remote set-url`,
`git config user.email`, `git reset --hard` on shared history.
