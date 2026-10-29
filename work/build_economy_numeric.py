"""Render all numeric economy lines from data/wiki/economy.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "data" / "wiki" / "economy.json").read_text(encoding="utf-8"))
OUT = ROOT / "docs" / "economy_numeric.md"

lines = [
    "# Economy: all numeric wiki lines (Step 8.3)",
    "",
    f"Source: `data/wiki/economy.json`, cutoff `{DATA.get('cutoff')}`.",
    "These are saved wikitext lines, not verified retail tables. Duplicates",
    "across `as_of_2023` and `latest` are kept only once per revision.",
    "",
]
total = 0
for section, pages in (DATA.get("sections") or {}).items():
    lines.append(f"## {section}")
    lines.append("")
    for page, entry in pages.items():
        revs = []
        for label in ("as_of_2023", "latest"):
            r = (entry or {}).get(label) or {}
            nums = r.get("numeric_lines") or []
            if nums:
                revs.append((label, r.get("revid"), r.get("timestamp"), nums))
        if not revs:
            continue
        lines.append(f"### {page}")
        lines.append("")
        lines.append(f"[{entry.get('url', '')}]({entry.get('url', '')})")
        lines.append("")
        for label, revid, ts, nums in revs:
            lines.append(f"- {label}: revid {revid}, saved {ts}")
            for n in nums:
                total += 1
                lines.append(f"  - {n.strip()}")
        lines.append("")

lines += [
    "## Gaps",
    "",
    "- Many pages have zero numeric lines (Gold costs, forge XP, mastery costs).",
    "- The same text can be a wiki editor's approximation; do not treat it as a",
    "  retail table without a second source.",
    "- Store prices, gacha weights and crystal drop rates are still missing.",
    "",
]
OUT.write_text("\n".join(lines), encoding="utf-8")
print("wrote", OUT, "lines", total)
