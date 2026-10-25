"""Build rating rows and try a linear rating fit (R2)."""
import json
import math
import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BOTS = ROOT / "data" / "wiki" / "bots.json"
OUT = ROOT / "data" / "wiki" / "rating_rows.json"


def num(v):
    s = str(v).replace(",", "").replace("+", "").strip()
    if not s:
        return None
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", s):
        s = s.replace(".", "")
    try:
        return float(s)
    except Exception:
        return None


def parse(table):
    header = [str(x).lower() for x in table[0]]
    cols = {}
    for i, h in enumerate(header):
        if "health" in h:
            cols["hp"] = i
        elif "attack" in h:
            cols["atk"] = i
        elif "rating" in h:
            cols["rating"] = i
    if "hp" not in cols or "atk" not in cols:
        return []
    rows = []
    for row in table[1:]:
        if len(row) <= max(cols.values()):
            continue
        m = re.search(r"(\d+)\s*[/'|]\s*(\d+)", str(row[0]))
        if not m:
            continue
        rank, level = int(m.group(1)), int(m.group(2))
        hp, atk = num(row[cols["hp"]]), num(row[cols["atk"]])
        rating = num(row[cols["rating"]]) if "rating" in cols else None
        if hp and atk:
            rows.append({"rank": rank, "level": level, "hp": hp, "attack": atk,
                         "rating": rating})
    return rows


bots = json.loads(BOTS.read_text(encoding="utf-8"))["bots"]
stat_rows = []
star_rows = []
for name, b in bots.items():
    for t in (b.get("stat_tables") or []):
        for r in parse(t):
            r.update({"bot": name, "star": None, "source": "stat_table"})
            stat_rows.append(r)
    for star, st in (b.get("stars") or {}).items():
        hp, atk, rating = num(st.get("health")), num(st.get("attack")), num(st.get("max_rating"))
        if hp and atk and rating:
            star_rows.append({"bot": name, "star": int(star), "rank": None, "level": None,
                              "hp": hp, "attack": atk, "rating": rating,
                              "source": "wiki_star"})
(OUT).write_text(json.dumps({"stat_table_rows": stat_rows, "star_rows": star_rows,
                             "note": "stat rows have rank/level but no star; star rows have "
                                     "star but no rank/level"}, ensure_ascii=False, indent=1),
                 encoding="utf-8")

print("stat rows", len(stat_rows), "with rating", sum(1 for r in stat_rows if r["rating"]))
print("star rows", len(star_rows))

# Fit on stat rows with rating (rating may be text/None).
rows = [r for r in stat_rows if r["rating"]]
A = np.array([[r["hp"], r["attack"], r["rank"], r["level"], 1.0] for r in rows])
y = np.array([r["rating"] for r in rows])
coef, *_ = np.linalg.lstsq(A, y, rcond=None)
pred = A @ coef
err = pred - y
print("stat fit coef", coef, "rmse", float(np.sqrt(np.mean(err ** 2))))
# integer rounded residual
print("rounded exact", int(np.sum(np.rint(pred) == y)), "of", len(y))
# fit stars
rows2 = star_rows
A2 = np.array([[r["hp"], r["attack"], r["star"], 1.0] for r in rows2])
y2 = np.array([r["rating"] for r in rows2])
coef2, *_ = np.linalg.lstsq(A2, y2, rcond=None)
pred2 = A2 @ coef2
print("star fit coef", coef2, "rmse", float(np.sqrt(np.mean((pred2 - y2) ** 2))))
print("rounded exact", int(np.sum(np.rint(pred2) == y2)), "of", len(y2))
