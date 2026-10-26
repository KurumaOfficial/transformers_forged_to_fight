"""8.2 numeric diff between as_of_2023 and latest saved revisions."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ECON = json.loads((ROOT / "data" / "wiki" / "economy.json").read_text(encoding="utf-8"))
VERS = ROOT / "data" / "wiki" / "versions"
OUT = ROOT / "docs" / "wiki_revision_diff.md"
lines = ["# Wiki revision numeric diff (8.2)", "",
         "Comparison of `as_of_2023` and `latest` saved sections in",
         "`data/wiki/economy.json`, plus `changed_values` from `versions/*.json`.", "",
         "| section/page | 2023 numeric | latest numeric | added | removed |",
         "|---|---:|---:|---:|---:|"]
changed = 0
for section, items in ECON.get("sections", {}).items():
    for name, row in items.items():
        a = set(row.get("as_of_2023", {}).get("numeric_lines") or [])
        b = set(row.get("latest", {}).get("numeric_lines") or [])
        add, rem = len(b - a), len(a - b)
        if add or rem:
            changed += 1
        lines.append(f"| {section}/{name} | {len(a)} | {len(b)} | {add} | {rem} |")
lines += ["", f"Pages with numeric changes: {changed}", ""]
lines += ["## Version pages with changed values", ""]
vrows = []
for f in sorted(VERS.glob("*.json")):
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        continue
    cv = d.get("changed_values") or []
    ni = d.get("new_interesting_lines") or []
    if cv or ni:
        vrows.append((f.name, len(cv), len(ni)))
for name, cv, ni in vrows:
    lines.append(f"- `{name}`: changed_values={cv}, new_interesting_lines={ni}")
if not vrows:
    lines.append("- none")
lines += ["", "## Notes", "",
          "- Most `latest` numeric sets are empty because the saved page is a",
          "  redirect/layout page or the numeric values live in images/tables.",
          "- Energon and Bot Chip/Spark have the richest 2023 numeric lines.",
          "- This is a text diff, not a parsed economy table; Q4/Q5 rewards remain",
          "  `[ASSUMED]`.",
          ]
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("changed pages", changed, "version rows", len(vrows))
