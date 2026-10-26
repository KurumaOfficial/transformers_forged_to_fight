"""R2.2/R2.3: nonlinear/robust rating fits and data-alignment flags."""
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ROWS = json.loads((ROOT / "data" / "wiki" / "rating_rows.json").read_text(encoding="utf-8"))
OUT = ROOT / "data" / "wiki" / "rating_fit_v2.json"


def fit(X, y):
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    pred = X @ coef
    err = pred - y
    return {
        "coef": [float(v) for v in coef],
        "rmse": float(math.sqrt(float(np.mean(err ** 2)))),
        "max_abs": float(np.max(np.abs(err))),
        "integer_exact": int(np.sum(np.rint(pred) == y)),
        "n": int(len(y)),
    }


def design(rows, nonlinear=False):
    A = []
    for r in rows:
        hp, atk = r["hp"], r["attack"]
        if nonlinear:
            A.append([math.log(max(hp, 1) / 1000.0), math.log(max(atk, 1) / 100.0), 1.0])
        else:
            A.append([hp, atk, 1.0])
    return np.array(A), np.array([r["rating"] for r in rows])


stat = [r for r in ROWS.get("stat_table_rows", []) if r.get("rating")]
star = [r for r in ROWS.get("star_rows", []) if r.get("rating")]

out = {"stat_n": len(stat), "star_n": len(star)}
for name, rows, nl in (("stat_linear", stat, False), ("stat_loglog", stat, True),
                       ("star_linear", star, False), ("star_loglog", star, True)):
    X, y = design(rows, nonlinear=nl)
    res = fit(X, y)
    if nl:
        pred = np.exp(X @ np.array(res["coef"]))
        rmse_orig = float(math.sqrt(float(np.mean((pred - y) ** 2))))
        res["rmse_original_scale"] = rmse_orig if math.isfinite(rmse_orig) else None
    out[name] = res

# Rank/level terms on stat rows.
for name, rows in (("stat_rank_level", stat),):
    X = np.array([[r["hp"], r["attack"], r.get("rank") or 1, r.get("level") or 1, 1.0]
                  for r in rows])
    y = np.array([r["rating"] for r in rows])
    out[name] = fit(X, y)

# Leave-one-bot-out on the linear stat model.
by_bot = defaultdict(list)
for r in stat:
    by_bot[r["bot"]].append(r)
lobo = []
for bot, rows in by_bot.items():
    train = [r for r in stat if r["bot"] != bot]
    Xtr, ytr = design(train)
    coef, *_ = np.linalg.lstsq(Xtr, ytr, rcond=None)
    Xte, yte = design(rows)
    pred = Xte @ coef
    lobo.append({
        "bot": bot,
        "n": len(rows),
        "rmse": float(math.sqrt(float(np.mean((pred - yte) ** 2)))),
        "max_abs": float(np.max(np.abs(pred - yte))) if len(rows) else 0.0,
    })
out["lobo_mean_rmse"] = float(np.mean([x["rmse"] for x in lobo])) if lobo else None
out["lobo"] = sorted(lobo, key=lambda x: -x["rmse"])[:10]

# sqrt(HP*ATK) single-feature proxy
X = np.array([[math.sqrt(max(r["hp"], 1) * max(r["attack"], 1)), 1.0] for r in stat])
y = np.array([r["rating"] for r in stat])
out["sqrt_hp_atk"] = fit(X, y)
out["loglog_note"] = "Log-log design is ill-conditioned (HP/ATK collinear); treat as diagnostic only."

# Outlier flag on the stat linear fit.
X, y = design(stat)
coef, *_ = np.linalg.lstsq(X, y, rcond=None)
pred = X @ coef
err = pred - y
sd = float(np.std(err)) or 1.0
out["outliers"] = [
    {**r, "pred": float(p), "resid": float(e), "z": float(e / sd)}
    for r, p, e in zip(stat, pred, err) if abs(e / sd) >= 3.0
]
out["note"] = (
    "Raw HP/ATK fits are proxies: the client formula consumes server-provided "
    "HeroRatingHP/HeroRatingAttack/HeroRatingAttackBase, not raw stats. "
    "Non-integer residuals are expected until those inputs are derived."
)
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1, allow_nan=False), encoding="utf-8")
print(json.dumps({k: v for k, v in out.items() if k not in ("lobo", "outliers")},
                 ensure_ascii=False, indent=1))
print("outliers", len(out["outliers"]))
