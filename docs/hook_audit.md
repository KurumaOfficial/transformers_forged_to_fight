# Pre-commit hook audit (9.4)

Hook: `.git/hooks/pre-commit` (source `work/git-hooks/pre-commit`). Tested with
`C:\Program Files\Git\bin\bash.exe .git/hooks/pre-commit` on staged files.
No commit was made; every test file was unstaged and deleted.

| Case | Expected | Actual |
|---|---|---|
| small markdown `docs/hook_audit_ok.md` | allowed | allowed |
| PNG in `docs/screens_ok/` | allowed | allowed |
| PNG outside `docs/screens_ok/` | blocked | `binary image outside docs/screens_ok/` |
| `.so` file (forced past `.gitignore`) | blocked | `blocked extension` |
| 1.1 MB markdown | blocked | `file is larger than 1 MiB (1100000 bytes)` |
| text containing the personal profile path | blocked | `added text contains C:/Users/ personal path` (earlier test) |
| normal repository commits | allowed | 30+ local commits since installation |

## False positives

None in legitimate project files. The only blocked cases were the deliberate
test files. `docs/screens_ok/` is the approved image location; images
elsewhere are blocked by design. The hook checks **staged** content only.

## Known limitations

- It cannot detect a secret split across multiple added lines.
- It does not scan binary content for strings; binaries are blocked by
  extension/directory first.
- `.gitignore` may silently skip a file before the hook sees it (e.g. a `.so`
  ignored by default); this is expected, but `git add -f` is still blocked.

## No push

The hook only guards commits. It does not push, change remotes, or rewrite
history. See `docs/git_cleanup_runbook.md`.
