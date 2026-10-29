"""Run N normal fights through battle_step.py and record the series.

Usage: python work/battle_series.py --count 20
Writes tests/smoke/battle_series.json. No weak-enemy flag.
"""
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tests" / "smoke" / "battle_series.json"
STEP = ROOT / "tests" / "smoke" / "battle_step.json"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=20)
    ap.add_argument("--wait", type=int, default=75)
    args = ap.parse_args()

    results = []
    started = datetime.now(timezone.utc).isoformat()
    for i in range(args.count):
        print(f"[series] fight {i + 1}/{args.count}", flush=True)
        row = {"index": i, "started": datetime.now(timezone.utc).isoformat()}
        try:
            p = subprocess.run(
                [sys.executable, str(ROOT / "work" / "battle_step.py"),
                 "--wait", str(args.wait)],
                cwd=str(ROOT), capture_output=True, text=True, timeout=600)
            row["exit"] = p.returncode
            row["tail"] = (p.stdout or "")[-600:]
            if p.returncode != 0:
                row["stderr"] = (p.stderr or "")[-600:]
        except Exception as exc:
            row["exit"] = -1
            row["error"] = str(exc)
        try:
            if STEP.exists():
                row["step"] = json.loads(STEP.read_text(encoding="utf-8"))
        except Exception:
            pass
        row["finished"] = datetime.now(timezone.utc).isoformat()
        results.append(row)
        OUT.write_text(json.dumps({
            "started": started,
            "updated": datetime.now(timezone.utc).isoformat(),
            "count": args.count,
            "completed": len(results),
            "results": results,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        time.sleep(3)

    ok = sum(1 for r in results if r.get("step", {}).get("status") == "PASS")
    print(json.dumps({"completed": len(results), "pass": ok, "out": str(OUT)},
                     ensure_ascii=False))
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
