import argparse
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(r"C:\Users\gameg\Desktop\TFTF")
REQ = ROOT / "server" / "requests.jsonl"
GOLD = ROOT / "tests" / "golden"
GOLD.mkdir(parents=True, exist_ok=True)
FLOW = [
    "/bcg/getLoginData",
    "/account/data",
    "/tuning",
    "/quests/quest-list",
    "/quests/quest-active",
    "/quests/quest-progression",
    "/quests/quest-detail/",
    "/quests/quest-begin/",
    "/quests/quest-movedir/",
]
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def shape(value, depth=0):
    if depth > 5:
        return "..."
    if isinstance(value, dict):
        return {k: shape(v, depth + 1) for k, v in sorted(value.items())[:80]}
    if isinstance(value, list):
        return ["list", shape(value[0], depth + 1)] if value else ["list"]
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, (int, float)):
        return "number"
    if value is None:
        return "null"
    return "string"


def load_rows():
    rows = []
    for line in REQ.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows


def select(rows):
    out = []
    seen = set()
    for r in reversed(rows):
        path = r.get("path", "")
        hit = next((prefix for prefix in FLOW if path == prefix or path.startswith(prefix)), None)
        if not hit or hit in seen:
            continue
        seen.add(hit)
        out.append(r)
    return list(reversed(out))


def request(row):
    path = row.get("path", "/")
    query = row.get("query") or {}
    if query:
        path += "?" + urllib.parse.urlencode({k: v[0] if isinstance(v, list) and v else v for k, v in query.items()})
    body = row.get("body")
    if isinstance(body, (dict, list)):
        body = json.dumps(body, ensure_ascii=False).encode()
    elif isinstance(body, str):
        body = body.encode()
    else:
        body = None
    req = urllib.request.Request("http://127.0.0.1:8080" + path, data=body, method=row.get("method", "GET"))
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
        return resp.status, json.loads(raw.decode("utf-8", "replace"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="store_true")
    args = ap.parse_args()
    rows = select(load_rows())
    if not rows:
        raise SystemExit("no golden flow requests found")
    if args.record:
        (GOLD / "quest_flow.jsonl").write_text(
            "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8"
        )
        expected = []
        for row in rows:
            try:
                status, data = request(row)
            except Exception as exc:
                expected.append({"request": row, "status": None, "error": str(exc)})
                continue
            expected.append({"request": row, "status": status, "shape": shape(data)})
        (GOLD / "expected_shapes.json").write_text(json.dumps(expected, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"recorded {len(expected)} shapes")
        return
    expected = json.loads((GOLD / "expected_shapes.json").read_text(encoding="utf-8"))
    failures = []
    for exp in expected:
        row = exp.get("request") or {}
        label = row.get("path", "?")
        if exp.get("error"):
            failures.append(f"{label}: recorded error {exp['error']}")
            continue
        try:
            status, data = request(row)
            if status != 200:
                failures.append(f"{label}: HTTP {status}")
                continue
            if shape(data) != exp["shape"]:
                failures.append(f"{label}: response shape changed")
        except Exception as exc:
            failures.append(f"{label}: {exc}")
    print(json.dumps({"status": "PASS" if not failures else "FAIL", "checks": len(expected), "failures": failures[:20]}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if not failures else 1)


if __name__ == "__main__":
    main()
