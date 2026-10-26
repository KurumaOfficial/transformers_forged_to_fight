"""R2.2/R2.3: interval LP for client-formula constants on wiki rating rows."""
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

ROOT = Path(__file__).resolve().parents[1]
ROWS = json.loads((ROOT / "data" / "wiki" / "rating_rows.json").read_text(encoding="utf-8"))
OUT = ROOT / "data" / "wiki" / "rating_lp.json"
stat = [r for r in ROWS.get("stat_table_rows", []) if r.get("rating")]
star = [r for r in ROWS.get("star_rows", []) if r.get("rating")]


def build(rows, features=("hp", "attack")):
    A, b, y = [], [], []
    for r in rows:
        row = [r[f] for f in features] + [1.0]
        A.append(row)
        y.append(r["rating"])
        # value <= rating
        b.append(r["rating"])
    A = np.array(A, dtype=float)
    y = np.array(y, dtype=float)
    # add lower bounds: -value <= -(rating-1+eps)
    A2 = np.vstack([A, -A])
    b2 = np.concatenate([y, -y + 1.0 - 1e-6])
    return A2, b2, A, y


def solve(rows, features=("hp", "attack")):
    A2, b2, A, y = build(rows, features)
    n = A.shape[1]
    res = linprog(c=np.zeros(n), A_ub=A2, b_ub=b2,
                  bounds=[(None, None)] * n, method="highs")
    out = {"feasible": bool(res.success), "features": list(features)}
    if res.success:
        out["x"] = [float(v) for v in res.x]
        out["region"] = {}
        for i in range(n):
            for sense, key in ((1, "min"), (-1, "max")):
                c = np.zeros(n)
                c[i] = sense
                r2 = linprog(c=c, A_ub=A2, b_ub=b2,
                             bounds=[(None, None)] * n, method="highs")
                out["region"][f"x{i}_{key}"] = float(r2.x[i]) if r2.success else None
        pred = A @ res.x
        out["rmse"] = float(math.sqrt(float(np.mean((pred - y) ** 2))))
        out["max_abs"] = float(np.max(np.abs(pred - y)))
        out["integer_exact"] = int(np.sum(np.ceil(pred - 1e-9) == y))
    return out


def slack_fit(rows, features=("hp", "attack")):
    """Minimize sum of constraint violations to find contradictory rows."""
    A2, b2, A, y = build(rows, features)
    n = A.shape[1]
    m2 = A2.shape[0]
    m = len(rows)
    c = np.concatenate([np.zeros(n), np.ones(m2)])
    A_ub = np.hstack([A2, -np.eye(m2)])
    b_ub = b2
    bounds = [(None, None)] * n + [(0, None)] * m2
    res = linprog(c=c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")
    if not res.success:
        return {"feasible": False, "error": res.message}
    x = res.x[:n]
    s = res.x[n:]
    pred = A @ x
    bad = []
    for i, r in enumerate(rows):
        v = max(s[i], s[m + i])
        if v > 1e-6:
            bad.append({**r, "pred": float(pred[i]), "violation": float(v)})
    return {"feasible": True, "x": [float(v) for v in x],
            "violations": len(bad), "bad": sorted(bad, key=lambda z: -z["violation"])[:20]}


out = {
    "stat_rows": len(stat),
    "star_rows": len(star),
    "stat_hp_atk": solve(stat),
    "star_hp_atk": solve(star),
    "stat_hp_atk_rank_level": solve(stat, ("hp", "attack", "rank", "level")),
    "stat_slack": slack_fit(stat),
    "star_slack": slack_fit(star),
}

# Leave-one-bot-out on the 3-variable model.
by_bot = defaultdict(list)
for r in stat:
    by_bot[r["bot"]].append(r)
lobo = []
for bot, rows in by_bot.items():
    train = [r for r in stat if r["bot"] != bot]
    A2, b2, A, y = build(train)
    res = linprog(c=np.zeros(3), A_ub=A2, b_ub=b2,
                  bounds=[(None, None)] * 3, method="highs")
    if not res.success:
        lobo.append({"bot": bot, "n": len(rows), "feasible": False})
        continue
    X = np.array([[r["hp"], r["atk"], 1.0] for r in rows])
    pred = X @ res.x
    lobo.append({
        "bot": bot, "n": len(rows), "feasible": True,
        "rmse": float(math.sqrt(float(np.mean((pred - np.array([r["rating"] for r in rows])) ** 2)))),
        "exact": int(np.sum(np.ceil(pred - 1e-9) == np.array([r["rating"] for r in rows]))),
    })
out["lobo"] = sorted(lobo, key=lambda x: -x.get("rmse", 0))[:15]

# Diagnostics: per-rank/per-level feasibility and column-shift flags.
by_rank = defaultdict(list)
by_level = defaultdict(list)
for r in stat:
    by_rank[r.get("rank")].append(r)
    by_level[r.get("level")].append(r)
out["by_rank"] = {str(k): solve(v) for k, v in sorted(by_rank.items(), key=lambda kv: (kv[0] is None, kv[0]))}
out["by_level"] = {str(k): solve(v) for k, v in sorted(by_level.items(), key=lambda kv: (kv[0] is None, kv[0]))}
out["column_flags"] = {
    "rating_equals_hp": [{"bot": r["bot"], "rank": r["rank"], "level": r["level"],
                         "hp": r["hp"], "rating": r["rating"]}
                        for r in stat if r["rating"] == r["hp"]],
    "rating_equals_attack": [{"bot": r["bot"], "rank": r["rank"], "level": r["level"],
                              "attack": r["attack"], "rating": r["rating"]}
                             for r in stat if r["rating"] == r["attack"]],
    "ratio_ranges": {
        "rating_hp": [min(r["rating"] / max(r["hp"], 1) for r in stat),
                      max(r["rating"] / max(r["hp"], 1) for r in stat)],
        "rating_attack": [min(r["rating"] / max(r["attack"], 1) for r in stat),
                          max(r["rating"] / max(r["attack"], 1) for r in stat)],
    },
}
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1, allow_nan=False), encoding="utf-8")
print(json.dumps({k: v for k, v in out.items() if k not in ("lobo",)}, ensure_ascii=False, indent=1)[:4000])
