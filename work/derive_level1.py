"""Derive rank-1/level-1 stats for bots with at least one table row.

Uses the global log-additive fit and one anchor row per bot. Error is the
leave-one-bot-out one-anchor error from stat_lobo.py (HP ~4.1%, ATK ~2.8%).
"""
import json
import math
import re
from pathlib import Path

import numpy as np

ROOT = Path(r"C:\Users\gameg\Desktop\TFTF")
BOTS = ROOT / "data" / "wiki" / "bots.json"
OUT = ROOT / "data" / "wiki" / "derived_level1.json"
LOBO = ROOT / "data" / "wiki" / "stat_lobo.json"


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
    hp = next((i for i, h in enumerate(header) if "health" in h), None)
    at = next((i for i, h in enumerate(header) if "attack" in h), None)
    if hp is None or at is None:
        return []
    rows = []
    for row in table[1:]:
        if len(row) <= max(hp, at):
            continue
        m = re.search(r"(\d+)\s*[/'|]\s*(\d+)", str(row[0]))
        if not m:
            continue
        r, l = int(m.group(1)), int(m.group(2))
        h, a = num(row[hp]), num(row[at])
        if h and a and h > 0 and a > 0:
            rows.append((r, l, h, a))
    return rows


bots = json.loads(BOTS.read_text(encoding="utf-8"))["bots"]
parsed = {}
for name, b in bots.items():
    rows = []
    for t in (b.get("stat_tables") or []):
        rows.extend(parse(t))
    if rows:
        parsed[name] = rows

ranks = sorted({r for rows in parsed.values() for r, _l, _h, _a in rows})
levels = sorted({l for rows in parsed.values() for _r, l, _h, _a in rows})
rmap = {r: i for i, r in enumerate(ranks[1:])}
lmap = {l: i for i, l in enumerate(levels[1:])}
names = sorted(parsed)
# full fit with bot dummies
ncol = 1 + len(rmap) + len(lmap) + len(names[1:])
X, Yh, Ya = [], [], []
bmap = {b: i for i, b in enumerate(names[1:])}
meta = []
for bot in names:
    for r, l, hp, atk in parsed[bot]:
        row = np.zeros(ncol)
        row[0] = 1
        if r in rmap:
            row[1 + rmap[r]] = 1
        if l in lmap:
            row[1 + len(rmap) + lmap[l]] = 1
        if bot in bmap:
            row[1 + len(rmap) + len(lmap) + bmap[bot]] = 1
        X.append(row); Yh.append(math.log(hp)); Ya.append(math.log(atk)); meta.append((bot, r, l, hp, atk))
X = np.asarray(X)
ch, *_ = np.linalg.lstsq(X, np.asarray(Yh), rcond=None)
ca, *_ = np.linalg.lstsq(X, np.asarray(Ya), rcond=None)


def base(coef, bot):
    rows = parsed[bot]
    r, l, hp, atk = rows[0]
    # value at rank1/level1 = log(anchor) - f(r,l) + f(1,1)
    def f(rr, ll):
        v = coef[0]
        if rr in rmap:
            v += coef[1 + rmap[rr]]
        if ll in lmap:
            v += coef[1 + len(rmap) + lmap[ll]]
        return v
    return f(1, 1) + (math.log(hp if coef is ch else atk) - f(r, l)), (r, l)


lobo = json.loads(LOBO.read_text(encoding="utf-8"))["lobo"]
out = {
    "method": "global log-additive fit + one anchor row per bot",
    "error": {
        "hp_mean_pct": lobo["hp"]["mean_one_anchor_pct"],
        "hp_median_pct": lobo["hp"]["median_one_anchor_pct"],
        "atk_mean_pct": lobo["atk"]["mean_one_anchor_pct"],
        "atk_median_pct": lobo["atk"]["median_one_anchor_pct"],
        "note": "leave-one-bot-out, one anchor row; no-anchor error is ~14-16%, so bots without any row stay ASSUMED",
    },
    "bots": {},
}
for bot in names:
    h, anchor = base(ch, bot)
    a, _ = base(ca, bot)
    out["bots"][bot] = {
        "hp": round(math.exp(h), 1),
        "attack": round(math.exp(a), 1),
        "anchor_row": {"rank": anchor[0], "level": anchor[1]},
        "source": "[DERIVED] from wiki table + global ladder",
    }
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("derived", len(out["bots"]), "bots; errors", out["error"])
print("Rhinox", out["bots"].get("Rhinox"), "Windblade", out["bots"].get("Windblade"))
