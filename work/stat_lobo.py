"""R1 leave-one-bot-out check and derived level-1 base estimates."""
import json
import math
import re
from pathlib import Path

import numpy as np

ROOT = Path(r".")
BOTS = ROOT / "data" / "wiki" / "bots.json"
OUT = ROOT / "data" / "wiki" / "stat_lobo.json"


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
        data = [r for r in table[1:] if len(r) >= 3]
        if not data:
            return []
        a, b = num(data[0][1]), num(data[0][2])
        if a is not None and b is not None:
            hp, at = (1, 2) if a >= b else (2, 1)
    rows = []
    for row in table[1:]:
        if len(row) <= max(hp, at):
            continue
        m = re.search(r"(\d+)\s*[/'|]\s*(\d+)", str(row[0]))
        if not m:
            continue
        rank, level = int(m.group(1)), int(m.group(2))
        h, a = num(row[hp]), num(row[at])
        if h and a and h > 0 and a > 0:
            rows.append((rank, level, h, a))
    return rows


bots = json.loads(BOTS.read_text(encoding="utf-8"))["bots"]
parsed = {}
for name, b in bots.items():
    rows = []
    for t in (b.get("stat_tables") or []):
        rows.extend(parse(t))
    if rows:
        parsed[name] = rows


def design(rows_by_bot, stat_idx, include_bot=True):
    ranks = sorted({r for rows in rows_by_bot.values() for r, _l, _h, _a in rows})
    levels = sorted({l for rows in rows_by_bot.values() for _r, l, _h, _a in rows})
    names = sorted(rows_by_bot)
    rmap = {r: i for i, r in enumerate(ranks[1:])}
    lmap = {l: i for i, l in enumerate(levels[1:])}
    bmap = {b: i for i, b in enumerate(names[1:])} if include_bot else {}
    ncol = 1 + len(rmap) + len(lmap) + len(bmap)
    A, y = [], []
    for bot in names:
        for rank, level, hp, atk in rows_by_bot[bot]:
            v = hp if stat_idx == 2 else atk
            row = np.zeros(ncol)
            row[0] = 1.0
            if rank in rmap:
                row[1 + rmap[rank]] = 1.0
            if level in lmap:
                row[1 + len(rmap) + lmap[level]] = 1.0
            if bot in bmap:
                row[1 + len(rmap) + len(lmap) + bmap[bot]] = 1.0
            A.append(row)
            y.append(math.log(v))
    return np.asarray(A), np.asarray(y), len(rmap), len(lmap)


def fit(rows_by_bot, stat_idx, include_bot=True):
    X, y, nr, nl = design(rows_by_bot, stat_idx, include_bot)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    return coef, nr, nl


def predict(coef, nr, nl, bot, rank, level, stat_idx):
    """Predict using global rank/level only (bot intercept 0)."""
    idx = 1
    vals = [coef[0]]
    # The design's rank/level columns are the first nr+nl after intercept.
    # We need the actual rank/level order; this helper is intentionally only
    # used for LOBO with the same ordering, so pass indices via globals.
    raise NotImplementedError


# Explicit LOBO with the same rank/level ordering as each fit.
ranks_order = sorted({r for rows in parsed.values() for r, _l, _h, _a in rows})
levels_order = sorted({l for rows in parsed.values() for _r, l, _h, _a in rows})
rmap = {r: i for i, r in enumerate(ranks_order[1:])}
lmap = {l: i for i, l in enumerate(levels_order[1:])}


def predict_global(coef, rank, level):
    v = coef[0]
    if rank in rmap:
        v += coef[1 + rmap[rank]]
    if level in lmap:
        v += coef[1 + len(rmap) + lmap[level]]
    return v


results = {}
for stat_idx, label in ((2, "hp"), (3, "atk")):
    errs_no_anchor = []
    errs_one_anchor = []
    per_bot = {}
    for held, rows in parsed.items():
        train = {b: r for b, r in parsed.items() if b != held}
        coef, nr, nl = fit(train, stat_idx, include_bot=True)
        # no anchor: h(bot)=0
        e0 = [predict_global(coef, rank, level) - math.log([rank, level, hp, atk][stat_idx])
              for rank, level, hp, atk in rows]
        # one anchor: use the first row's residual as the bot intercept
        h = math.log([rows[0][0], rows[0][1], rows[0][2], rows[0][3]][stat_idx]) - predict_global(coef, rows[0][0], rows[0][1])
        e1 = [(predict_global(coef, rank, level) + h) - math.log([rank, level, hp, atk][stat_idx])
              for rank, level, hp, atk in rows[1:]]
        rm0 = float(np.sqrt(np.mean(np.square(e0))))
        rm1 = float(np.sqrt(np.mean(np.square(e1)))) if e1 else 0.0
        errs_no_anchor.append(rm0)
        errs_one_anchor.append(rm1)
        per_bot[held] = {"no_anchor": rm0, "one_anchor": rm1, "rows": len(rows)}
    results[label] = {
        "bots": len(per_bot),
        "mean_no_anchor_pct": 100 * (math.exp(float(np.mean(errs_no_anchor))) - 1),
        "mean_one_anchor_pct": 100 * (math.exp(float(np.mean(errs_one_anchor))) - 1),
        "median_no_anchor_pct": 100 * (math.exp(float(np.median(errs_no_anchor))) - 1),
        "median_one_anchor_pct": 100 * (math.exp(float(np.median(errs_one_anchor))) - 1),
        "worst_no_anchor_pct": 100 * (math.exp(float(np.max(errs_no_anchor))) - 1),
        "per_bot": per_bot,
    }

# Star-1 base check for bots that have both a table and a wiki star-1 row.
star = {}
for name, b in bots.items():
    st = (b.get("stars") or {}).get("1") or {}
    h, a = num(st.get("health")), num(st.get("attack"))
    if name in parsed and h and a:
        star[name] = {"hp": h, "attack": a}

(OUT).write_text(json.dumps({"lobo": results, "star1_with_table": star},
                            ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({k: {x: v[x] for x in ("bots", "mean_no_anchor_pct", "mean_one_anchor_pct",
                                        "median_no_anchor_pct", "median_one_anchor_pct",
                                        "worst_no_anchor_pct")}
                  for k, v in results.items()}, indent=1))
print("star1 with table", len(star))
