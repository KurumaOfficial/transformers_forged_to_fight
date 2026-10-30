"""Merge the two 10-fight series into a 20-fight report."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / "tests" / "smoke" / "battle_series_part1.json"
B = ROOT / "tests" / "smoke" / "battle_series.json"
OUT = ROOT / "tests" / "smoke" / "battle_series_20.json"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

a = json.loads(A.read_text(encoding="utf-8"))
b = json.loads(B.read_text(encoding="utf-8"))
rows = list(a.get("results") or [])[:10] + list(b.get("results") or [])[:10]
for i, row in enumerate(rows):
    row["global_index"] = i
passed = sum(1 for r in rows if (r.get("step") or {}).get("status") == "PASS")
payload = {
    "started": a.get("started"),
    "finished": datetime.now(timezone.utc).isoformat(),
    "count": 20,
    "completed": len(rows),
    "pass": passed,
    "fail": len(rows) - passed,
    "status": "PASS" if len(rows) == 20 and passed == 20 else "PARTIAL",
    "sources": [A.name, B.name],
    "results": rows,
}
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: payload[k] for k in ("count", "completed", "pass", "fail", "status")},
                 ensure_ascii=False))
