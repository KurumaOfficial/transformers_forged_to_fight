"""Snapshot the current run artifacts into runs/<stamp>/ and update runs/index.json."""
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADB = str(ROOT / "work" / "platform-tools" / "adb.exe")
RUNS = ROOT / "runs"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
out = RUNS / stamp
out.mkdir(parents=True, exist_ok=True)

for src, name in [
    (ROOT / "server" / "requests.jsonl", "requests.jsonl"),
    (ROOT / "tests" / "smoke" / "latest.json", "smoke_latest.json"),
    (ROOT / "tests" / "smoke" / "battle_step.json", "battle_step.json"),
    (ROOT / "tests" / "smoke" / "battle_series.json", "battle_series.json"),
    (ROOT / "tests" / "smoke" / "battle_series_20.json", "battle_series_20.json"),
    (ROOT / "tests" / "smoke" / "full_smoke.json", "full_smoke.json"),
    (ROOT / "tests" / "sweep" / "sweep_59.json", "sweep_59.json"),
]:
    if src.exists():
        shutil.copy2(src, out / name)

nightly_logs = sorted((ROOT / "work" / "nightly").glob("nightly_*.log"))
if nightly_logs:
    shutil.copy2(nightly_logs[-1], out / "nightly.log")

logcat = subprocess.run([ADB, "logcat", "-d", "-v", "time"], capture_output=True,
                        text=True, encoding="utf-8", errors="replace", timeout=120).stdout
(out / "logcat.txt").write_text(logcat or "", encoding="utf-8")

shots = ROOT / "tests" / "smoke"
if shots.exists():
    (out / "screens").mkdir(exist_ok=True)
    for p in sorted(shots.glob("*.png"))[:20]:
        shutil.copy2(p, out / "screens" / p.name)

index_path = RUNS / "index.json"
index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else []
index.append({
    "stamp": stamp,
    "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "path": f"runs/{stamp}",
    "files": sorted(p.name for p in out.iterdir()),
    "notes": "requests, smoke/sweep JSON, nightly log, logcat, first 20 smoke screenshots",
})
index_path.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
print("run", out, "index entries", len(index))
