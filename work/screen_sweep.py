"""Quick non-combat screen sweep: CRYSTALS, OBJECTIVES, profile, STORE."""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r".")
sys.path.insert(0, str(ROOT / "work"))
import smoke_test as s

OUT = ROOT / "tests" / "screens"
OUT.mkdir(parents=True, exist_ok=True)
start = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def step(name):
    p = s.shot(name)
    print(f"[screens] {name} {p.stat().st_size if p.exists() else 0}")


def main():
    s.adb("shell", "am", "force-stop", s.PKG)
    s.adb("logcat", "-c")
    time.sleep(2)
    s.adb("shell", "am", "start", "-n", s.ACT)
    ok = s.wait_title_then_home(150)
    print("home", ok)
    step("00_home")
    # CRYSTALS tab
    s.tap(1755, 160, 8)
    step("01_crystals")
    s.adb("shell", "input", "keyevent", "4")
    time.sleep(3)
    # OBJECTIVES card
    s.tap(2000, 300, 8)
    step("02_objectives")
    s.adb("shell", "input", "keyevent", "4")
    time.sleep(3)
    # profile name / commander
    s.tap(300, 70, 8)
    step("03_profile")
    s.adb("shell", "input", "keyevent", "4")
    time.sleep(3)
    # STORE tab
    s.tap(2070, 160, 8)
    step("04_store")
    rows = s.read_requests()
    paths = [r.get("path") for r in rows if r.get("timestamp", "") >= start]
    (OUT / "latest.json").write_text(json.dumps({"started": start, "home": ok, "paths": paths[-60:]}, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
