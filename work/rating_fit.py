"""R2 attempt: fit wiki star-1 Max Rating against HP/ATK.

This is NOT the client formula; see spec/rating_formula.md. It documents the
operand-bound failure and the residual error.
"""
import json
from pathlib import Path

import numpy as np

ROOT = Path(r"C:\Users\gameg\Desktop\TFTF")
bots = json.loads((ROOT / "data" / "wiki" / "bots.json").read_text(encoding="utf-8"))["bots"]


def num(x):
    try:
        return float(str(x).replace(",", ""))
    except Exception:
        return None


rows = []
for name, b in bots.items():
    st = (b.get("stars") or {}).get("1") or {}
    hp, atk, rating = num(st.get("health")), num(st.get("attack")), num(st.get("max_rating"))
    if hp and atk and rating and hp > 10:  # exclude the 1.009 typo row
        rows.append({"bot": name, "hp": hp, "attack": atk, "rating": rating})

A = np.array([[r["hp"], r["attack"], 1.0] for r in rows])
y = np.array([r["rating"] for r in rows])
coef, *_ = np.linalg.lstsq(A, y, rcond=None)
pred = A @ coef
out = {
    "model": "rating = a*hp + b*attack + c",
    "coef": [float(c) for c in coef],
    "rows": rows,
    "pred": [float(p) for p in pred],
    "rmse": float(np.sqrt(np.mean((pred - y) ** 2))),
    "note": "not the client formula; R2 partial",
}
(ROOT / "data" / "wiki" / "rating_fit.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({k: out[k] for k in ("coef", "rmse")}, indent=1))
