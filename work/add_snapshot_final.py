from pathlib import Path

p = Path("report/FINAL_2026-10-31.md")
s = p.read_text(encoding="utf-8")
s = s.replace(
    "## Повторено",
    "- Snapshot: `runs/2026-10-31_135904/`; docs archive in `docs/INTEGRITY.md`.\n\n## Повторено",
)
p.write_text(s, encoding="utf-8")
print("ok")
