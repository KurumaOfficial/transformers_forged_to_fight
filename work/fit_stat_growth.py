import json
import re
import math
from pathlib import Path

ROOT = Path(r".")
DOC = ROOT / "data" / "wiki" / "bots.json"


def num(v):
    s = str(v).replace(",", "").strip()
    try:
        return float(s)
    except Exception:
        return None


def solve3(A, y):
    # normal equations A^T A x = A^T y
    n = len(A[0])
    M = [[sum(A[k][i] * A[k][j] for k in range(len(A))) for j in range(n)] for i in range(n)]
    b = [sum(A[k][i] * y[k] for k in range(len(A))) for i in range(n)]
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(M[r][i]))
        M[i], M[p] = M[p], M[i]; b[i], b[p] = b[p], b[i]
        if abs(M[i][i]) < 1e-12:
            return None
        for r in range(i + 1, n):
            f = M[r][i] / M[i][i]
            for c in range(i, n):
                M[r][c] -= f * M[i][c]
            b[r] -= f * b[i]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (b[i] - sum(M[i][j] * x[j] for j in range(i + 1, n))) / M[i][i]
    return x


def fit(rows, key):
    A = [[r, l, 1.0] for r, l, _h, _a in rows]
    y = [h if key == "hp" else a for _r, _l, h, a in rows]
    x = solve3(A, y)
    if not x:
        return None
    pred = [x[0] * r + x[1] * l + x[2] for r, l, _h, _a in rows]
    err = [p - v for p, v in zip(pred, y)]
    rmse = math.sqrt(sum(e * e for e in err) / len(err))
    mae = sum(abs(e) for e in err) / len(err)
    return x, rmse, mae, max(abs(e) for e in err)


bots = json.loads(DOC.read_text(encoding="utf-8"))["bots"]
results = []
for name, b in bots.items():
    rows = []
    for table in (b.get("stat_tables") or []):
        for row in table:
            if len(row) < 3:
                continue
            m = re.match(r"(\d+)\s*/\s*(\d+)", str(row[0]))
            if not m:
                continue
            rank, level = int(m.group(1)), int(m.group(2))
            hp, atk = num(row[1]), num(row[2])
            if hp is None or atk is None:
                continue
            rows.append((rank, level, hp, atk))
    if len(rows) >= 3:
        fh = fit(rows, "hp"); fa = fit(rows, "atk")
        if fh and fa:
            results.append({"bot": name, "rows": len(rows),
                            "hp": {"a_rank": fh[0][0], "b_level": fh[0][1], "c": fh[0][2], "rmse": fh[1], "mae": fh[2], "max": fh[3]},
                            "atk": {"a_rank": fa[0][0], "b_level": fa[0][1], "c": fa[0][2], "rmse": fa[1], "mae": fa[2], "max": fa[3]}})

print("bots with >=3 table rows:", len(results))
for r in sorted(results, key=lambda x: x["hp"]["rmse"] + x["atk"]["rmse"]):
    print(f"{r['bot']:28s} rows={r['rows']:2d} HP rmse={r['hp']['rmse']:8.1f} max={r['hp']['max']:8.1f} | ATK rmse={r['atk']['rmse']:7.1f} max={r['atk']['max']:7.1f}")
(ROOT / "data" / "wiki" / "stat_growth_fit.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
