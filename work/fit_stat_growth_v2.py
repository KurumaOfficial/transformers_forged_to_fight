"""R1 v2: robust stat-table parse + log-additive rank/level/bot fit."""
import json
import math
import re
from pathlib import Path

import numpy as np

ROOT = Path(r".")
DOC = ROOT / "data" / "wiki" / "bots.json"
OUT = ROOT / "data" / "wiki" / "stat_growth_fit_v2.json"


def num(v):
    s = str(v).replace(",", "").replace("+", "").strip()
    if not s:
        return None
    # 20.520 / 1.234.567 -> thousands separators, not decimals
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", s):
        s = s.replace(".", "")
    try:
        return float(s)
    except Exception:
        return None


def parse_table(table):
    if not table:
        return []
    header = [str(x) for x in table[0]]
    lower = [h.lower() for h in header]
    hp_col = atk_col = None
    for i, h in enumerate(lower):
        if "health" in h:
            hp_col = i
        elif "attack" in h:
            atk_col = i
    # Blank/scoped headers: fall back to numeric magnitude (HP > ATK).
    if hp_col is None or atk_col is None:
        for i, h in enumerate(lower):
            if "scope" in h and i in (1, 2) and hp_col is None:
                hp_col = i
        # detect by first data row
        data = [r for r in table[1:] if len(r) >= 3]
        if data:
            a, b = num(data[0][1]), num(data[0][2])
            if a is not None and b is not None:
                if a >= b:
                    hp_col, atk_col = 1, 2
                else:
                    hp_col, atk_col = 2, 1
    if hp_col is None or atk_col is None:
        return []
    rows = []
    for row in table[1:]:
        if len(row) <= max(hp_col, atk_col):
            continue
        rl = str(row[0])
        m = re.search(r"(\d+)\s*[/'|]\s*(\d+)", rl)
        if not m:
            continue
        rank, level = int(m.group(1)), int(m.group(2))
        hp, atk = num(row[hp_col]), num(row[atk_col])
        if hp is None or atk is None or hp <= 0 or atk <= 0:
            continue
        rows.append((rank, level, hp, atk))
    return rows


bots = json.loads(DOC.read_text(encoding="utf-8"))["bots"]
parsed = {}
for name, b in bots.items():
    rows = []
    for t in (b.get("stat_tables") or []):
        rows.extend(parse_table(t))
    if rows:
        parsed[name] = rows

print("bots with parsed rows:", len(parsed))
print("total rows:", sum(len(v) for v in parsed.values()))

# Simple per-bot linear fit, corrected numbers
def solve(A, y):
    x, *_ = np.linalg.lstsq(np.asarray(A), np.asarray(y), rcond=None)
    return x


lin = []
for name, rows in parsed.items():
    A = [[r, l, 1.0] for r, l, _h, _a in rows]
    for idx, key in ((2, "hp"), (3, "atk")):
        y = [row[idx] for row in rows]
        if len(rows) >= 3:
            x = solve(A, y)
            pred = np.asarray(A) @ x
            rmse = float(np.sqrt(np.mean((pred - np.asarray(y)) ** 2)))
            maxe = float(np.max(np.abs(pred - np.asarray(y))))
            lin.append({"bot": name, "stat": key, "rmse": rmse, "max": maxe})

print("\nlinear rank+level corrected (worst HP):")
for r in sorted([x for x in lin if x["stat"] == "hp"], key=lambda x: -x["rmse"])[:8]:
    print(f"  {r['bot']:26s} rmse={r['rmse']:9.1f} max={r['max']:9.1f}")
print("linear rank+level corrected (worst ATK):")
for r in sorted([x for x in lin if x["stat"] == "atk"], key=lambda x: -x["rmse"])[:8]:
    print(f"  {r['bot']:26s} rmse={r['rmse']:9.1f} max={r['max']:9.1f}")

# Global log-additive: log(stat) = intercept + rank + level + bot
def global_fit(stat_index):
    ranks = sorted({r for rows in parsed.values() for r, _l, _h, _a in rows})
    levels = sorted({l for rows in parsed.values() for _r, l, _h, _a in rows})
    botnames = sorted(parsed)
    r_index = {r: i for i, r in enumerate(ranks[1:])}
    l_index = {l: i for i, l in enumerate(levels[1:])}
    b_index = {b: i for i, b in enumerate(botnames[1:])}
    ncol = 1 + len(r_index) + len(l_index) + len(b_index)
    A, y, meta = [], [], []
    for bot in botnames:
        for rank, level, hp, atk in parsed[bot]:
            v = hp if stat_index == 2 else atk
            if v <= 0:
                continue
            row = np.zeros(ncol)
            row[0] = 1.0
            if rank in r_index:
                row[1 + r_index[rank]] = 1.0
            if level in l_index:
                row[1 + len(r_index) + l_index[level]] = 1.0
            if bot in b_index:
                row[1 + len(r_index) + len(l_index) + b_index[bot]] = 1.0
            A.append(row)
            y.append(math.log(v))
            meta.append((bot, rank, level, v))
    X = np.asarray(A)
    Y = np.asarray(y)
    coef, *_ = np.linalg.lstsq(X, Y, rcond=None)
    pred = X @ coef
    resid = pred - Y
    rmse = float(np.sqrt(np.mean(resid ** 2)))
    print(f"\nlog-additive stat={stat_index} rows={len(y)} rmse_log={rmse:.5f} "
          f"(~{100*(math.exp(rmse)-1):.2f}%)")
    print("  rank multipliers vs rank1:",
          {r: round(math.exp(coef[1 + i]), 4) for r, i in r_index.items()})
    print("  level multipliers vs level1:",
          {l: round(math.exp(coef[1 + len(r_index) + i]), 4) for l, i in l_index.items()})
    per_bot = {}
    for (bot, rank, level, v), p in zip(meta, pred):
        per_bot.setdefault(bot, []).append(p - math.log(v))
    worst = sorted(((b, float(np.sqrt(np.mean(np.square(e))))) for b, e in per_bot.items()),
                   key=lambda x: -x[1])[:6]
    print("  worst bots (log rmse):", [(b, round(e, 4)) for b, e in worst])
    return {"rmse_log": rmse, "rank_mult": {str(k): float(math.exp(v)) for k, v in
            ((r, coef[1 + i]) for r, i in r_index.items())},
            "level_mult": {str(k): float(math.exp(v)) for k, v in
            ((l, coef[1 + len(r_index) + i]) for l, i in l_index.items())},
            "worst": [(b, e) for b, e in worst]}

res = {"parsed_bots": len(parsed), "rows": sum(len(v) for v in parsed.values()),
       "linear": lin, "hp": global_fit(2), "atk": global_fit(3)}
OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
print("\nwrote", OUT)
