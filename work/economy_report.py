"""6.3 economy coverage report from saved wiki revisions."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ECON = json.loads((ROOT / "data" / "wiki" / "economy.json").read_text(encoding="utf-8"))
OUT = ROOT / "docs" / "economy_report.md"
lines = ["# Economy coverage (6.3)", "",
         "Source: `data/wiki/economy.json` (saved wiki sections, as-of-2023 and latest).",
         "Numeric lines only; tables that are images/text without numbers are marked missing.", ""]
missing = []
for section, items in ECON.get("sections", {}).items():
    lines.append(f"## {section}")
    lines.append("")
    lines.append("| page | as_of_2023 | latest | numeric lines (2023/latest) |")
    lines.append("|---|---|---|---:|")
    for name, row in items.items():
        a = row.get("as_of_2023") or {}
        b = row.get("latest") or {}
        an = len(a.get("numeric_lines") or [])
        bn = len(b.get("numeric_lines") or [])
        lines.append(f"| {name} | {a.get('present')} | {b.get('present')} | {an}/{bn} |")
        if an == 0 and bn == 0:
            missing.append(f"{section}/{name}")
    lines.append("")
lines += ["## Missing numeric tables", ""]
if missing:
    lines += [f"- `{m}`" for m in missing]
else:
    lines.append("None: every saved page has at least one numeric line.")
lines += ["", "## Notes", "",
          "- Energon has the richest numbers (offer prices, mission rewards, ad rewards, 2022 shutdown changes).",
          "- Upgrade costs, XP curves and rank/mastery tables are not fully present as numeric lines; the",
          "  `progression/*` and `forge/*` pages are mostly text/layout pages.",
          "- `data/wiki/economy.json` is a text extract, not a normalized economy table; Q4/Q5 rewards",
          "  remain `[ASSUMED]` until the missing tables are parsed.",
          ]
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("missing", len(missing))
for m in missing:
    print(m)
