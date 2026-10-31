import subprocess
import time
import sys

ADB = r".\work\platform-tools\adb.exe"

print("[TUNNEL DAEMON] Starting ADB reverse tunnel supervisor...")
sys.stdout.flush()

while True:
    try:
        # Check current reverse list
        chk = subprocess.run([ADB, "reverse", "--list"], capture_output=True, text=True, timeout=5)
        if "8080" not in chk.stdout:
            print("[TUNNEL DAEMON] 8080 not found in adb reverse list. Adding reverse tcp:8080 tcp:8080...")
            res = subprocess.run([ADB, "reverse", "tcp:8080", "tcp:8080"], capture_output=True, text=True, timeout=5)
            print("[TUNNEL DAEMON] Reverse result:", res.stdout.strip())
            sys.stdout.flush()
    except Exception as e:
        print(f"[TUNNEL DAEMON] Warning: {e}")
        sys.stdout.flush()
    time.sleep(2)
