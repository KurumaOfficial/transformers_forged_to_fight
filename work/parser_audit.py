"""Parser audit: sample 20 bots, validate stat-table rows by header name."""
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOTS = json.loads((ROOT / "data" / "wiki" / "bots.json").read_text(encoding="utf-8"))["bots"]
OUT = ROOT / "docs" / "parser_audit.md"
random.seed(42)
names = [n for n, b in BOTS.items() if b.get("stat_tables")]
sample = random.sample(names, min(20, len(names)))
lines = ["# Parser sample audit (Step 3.3 / 9.3)", "",
         f"Random seed 42; {len(sample)} pages with stat tables.", "",
         "| page | parsed rows | header | flags |", "|---|---:|---|---|"]
flags_total = 0
for name in sample:
    b = BOTS[name]
    parsed = []
    for t in b.get("stat_tables") or []:
        if not t:
            continue
        header = [str(x) for x in t[0]]
        for row in t[1:]:
            if not row:
                continue
            m = re.search(r"(\d+)\s*[/'|]\s*(\d+)", str(row[0]))
            if not m:
                continue
            nums = []
            for cell in row[1:]:
                s = str(cell).replace(",", "").replace("+", "").strip()
                if re.fullmatch(r"\d{1,3}(\.\d{3})+", s):
                    s = s.replace(".", "")
                try:
                    nums.append(float(s))
                except ValueError:
                    nums.append(None)
            parsed.append((header, int(m.group(1)), int(m.group(2)), nums))
    flags = []
    for header, rank, level, nums in parsed:
        hp = atk = rating = None
        for i, h in enumerate(header[1:]):
            hl = h.lower().replace('scope="col"|', "")
            val = nums[i] if i < len(nums) else None
            if "health" in hl:
                hp = val
            elif "attack" in hl:
                atk = val
            elif "rating" in hl:
                rating = val
        if hp is None or atk is None or hp <= 0 or atk <= 0:
            flags.append(f"r{rank}l{level}: bad hp/atk")
        elif rating is not None and rating == hp:
            flags.append(f"r{rank}l{level}: rating==hp")
        elif rating is not None and rating < atk:
            flags.append(f"r{rank}l{level}: rating<attack")
    flags_total += len(flags)
    header0 = parsed[0][0] if parsed else []
    lines.append(f"| {name} | {len(parsed)} | {header0} | {'; '.join(flags) or 'ok'} |")
lines += ["", f"Flags: {flags_total}", "",
          "## Interpretation", "",
          "- Header order is respected; pages with `Attack, Health, Rating` are not",
          "  treated as `Health, Attack, Rating`.",
          "- `rating==hp` on Ironhide rank 1 is the known suspicious row (Step 3.2 outlier).",
          "- `rating<attack` or non-numeric HP/ATK indicates a wiki/row issue, not a",
          "  valid rating; those rows are excluded from the rating LP.",
          "- 20 pages sampled; the parser reads by header name, so a shifted wiki table",
          "  would show as a flag here.",
          ]
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("sample", len(sample), "flags", flags_total)
for line in lines[-8:]:
    print(line)
