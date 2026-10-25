from pathlib import Path

p = Path(__file__).resolve().parents[1] / "MASTER_PROMPT.md"
s = p.read_text(encoding="utf-8")
start = s.index("## Next queue (v4.5)")
end = s.index("## Rules", start)
new = """## Queue status v4.5

- Step 0: git audit + dangling audit + pre-commit hook done; no push.
- Step 1: watchdog/snapshot done; windowed angle stable; full smoke PASS.
- Step 2: ModelID/tags fixed; `PlayerAttributes.Init` HashSet NRE open.
- Step 3: blocked (no match-loaded).
- Step 4: R1 coverage 37 WIKI / 22 ASSUMED; LOBO errors recorded; R2 rows + partial fit.
- Step 5: S1 12/59; nightly/backup done; screens table exists.
- Step 6: Q1/Q2/Q3 done (70/90 boss ids); Q4/Q5 blocked.
- Step 7: C1/C2/C3 partial; sync/async catalog started.
- Step 8: W1 2/36; W2-W4 partial; W5 done.
- Step 9: T1 quest routing split done; T2/T3 done; backup done.
- Step 10: this file; STATE/FIDELITY/COVERAGE/OPEN_QUESTIONS updated.

## Next queue (v4.6)

1. Battle: breakpoint on `0xDAC198`/`HashSet..ctor`; then match-loaded/resolve.
2. S1 59/59; R3/R4; Q4/Q5 after battle.
3. C1/C2/C3 deeper; W2 exact economy; W1 remaining priority URLs.
4. Git cleanup only after user decision; never push/gc/filter-repo without consent.

"""
s = s[:start] + new + s[end:]
p.write_text(s, encoding="utf-8")
print("cleaned queue")
