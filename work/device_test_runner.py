import subprocess
import time
import os
import sys

ADB = r".\work\platform-tools\adb.exe"
APK = r".\work\patched_build\tftf_patched_v9.2.0.apk"
FULL_LOGCAT = r".\work\logcat_full.txt"
FILTERED_LOGCAT = r".\work\logcat_filtered.txt"
REQUESTS_LOG = r".\server\requests.jsonl"

def run_test():
    print("================================================================")
    print("  Transformers: Forged to Fight - Stage 1 Device Execution Run")
    print("================================================================")
    
    # 1. Check device
    res = subprocess.run([ADB, "devices"], capture_output=True, text=True)
    print("[*] ADB devices output:\n" + res.stdout)
    if "device" not in res.stdout:
        print("[!] Error: No authorized ADB device found!")
        return False
        
    # 2. Reverse port 8080
    print("[*] Setting up adb reverse tcp:8080 tcp:8080...")
    rev_res = subprocess.run([ADB, "reverse", "tcp:8080", "tcp:8080"], capture_output=True, text=True)
    print("    Reverse result:", rev_res.stdout.strip() or "OK")
    
    # 3. Check if installed, if so clear data, else install
    pkg_chk = subprocess.run([ADB, "shell", "pm", "list", "packages", "com.kabam.bigrobot"], capture_output=True, text=True)
    if "package:com.kabam.bigrobot" in pkg_chk.stdout:
        print("[*] com.kabam.bigrobot is already installed. Resetting app data with pm clear...")
        subprocess.run([ADB, "shell", "pm", "clear", "com.kabam.bigrobot"], capture_output=True, text=True)
        print("    App data cleared (clean slate).")
    else:
        print(f"[*] Installing patched APK: {APK} (this may take 15-30s for an 800MB APK)...")
        inst_cmd = [ADB, "install", "-r", "--no-incremental", APK]
        inst_res = subprocess.run(inst_cmd, capture_output=True, text=True)
        print("    Install output:\n" + inst_res.stdout)
        if "Success" not in inst_res.stdout:
            print("[!] Install stderr:\n" + inst_res.stderr)
            if "INSTALL_FAILED_USER_RESTRICTED" in inst_res.stderr or "INSTALL_FAILED_USER_RESTRICTED" in inst_res.stdout:
                print("[ACTION REQUIRED ON PHONE] Разрешите 'Установка через USB' на экране телефона!")
            return False
        
    # 5. Clear requests log to ensure 100% clean capture
    with open(REQUESTS_LOG, "w", encoding="utf-8") as f:
        pass
    print("[*] requests.jsonl cleared for fresh client session.")
    
    # 6. Clear logcat
    print("[*] Clearing logcat buffer...")
    subprocess.run([ADB, "logcat", "-c"])
    
    # 7. Start full logcat without filters (threadtime)
    print(f"[*] Starting FULL logcat capture to {FULL_LOGCAT}...")
    f_full = open(FULL_LOGCAT, "w", encoding="utf-8", errors="replace")
    p_full = subprocess.Popen([ADB, "logcat", "-v", "threadtime"], stdout=f_full, stderr=subprocess.DEVNULL)
    
    # 8. Start filtered logcat
    print(f"[*] Starting filtered logcat capture to {FILTERED_LOGCAT}...")
    f_filt = open(FILTERED_LOGCAT, "w", encoding="utf-8", errors="replace")
    p_filt = subprocess.Popen([ADB, "logcat", "-v", "time", "-s", "Unity:V", "ActivityManager:I", "Sparx:V", "CRASH:E", "*:E"],
                              stdout=f_filt, stderr=subprocess.DEVNULL)
                              
    # 9. Launch the game
    print("[*] Launching game com.kabam.bigrobot on device...")
    launch_res = subprocess.run([ADB, "shell", "monkey", "-p", "com.kabam.bigrobot", "-c", "android.intent.category.LAUNCHER", "1"],
                                capture_output=True, text=True)
    print("    Monkey output:\n" + launch_res.stdout)
    
    # 10. Monitor execution
    print("[*] Client launched! Monitoring incoming requests for 30 seconds...")
    for sec in range(1, 31):
        time.sleep(1)
        if os.path.exists(REQUESTS_LOG):
            with open(REQUESTS_LOG, "r", encoding="utf-8", errors="ignore") as f:
                lines = [l.strip() for l in f if l.strip()]
            if lines:
                print(f"[+] [{sec}s] Received {len(lines)} request(s) so far!")
                for line in lines[-1:]:
                    print("    Last:", line[:160])
                    
    # Capture device screenshot
    print("[*] Capturing device screenshot...")
    subprocess.run([ADB, "shell", "screencap", "-p", "/sdcard/screen.png"])
    subprocess.run([ADB, "pull", "/sdcard/screen.png", r".\work\screenshot_stage1.png"])
    if os.path.exists(r".\work\screenshot_stage1.png"):
        print(f"    Screenshot saved to work/screenshot_stage1.png ({os.path.getsize(r'.\work\screenshot_stage1.png')} bytes)")

    # Stop logcats
    time.sleep(1)
    p_full.terminate()
    p_filt.terminate()
    f_full.close()
    f_filt.close()
    
    print("\n================================================================")
    print("[*] Execution run finished. Summary:")
    if os.path.exists(REQUESTS_LOG):
        with open(REQUESTS_LOG, "r", encoding="utf-8", errors="ignore") as f:
            lines = [l.strip() for l in f if l.strip()]
        print(f"[+] Total HTTP Requests captured: {len(lines)}")
        for i, l in enumerate(lines):
            try:
                import json
                entry = json.loads(l)
                p = entry.get('path', '')
                m = entry.get('method', '')
                q = list(entry.get('query', {}).keys())
                print(f"    #{i+1}: {m} {p} (query keys: {q})")
            except Exception:
                print(f"    #{i+1}: {l[:100]}")
    else:
        print("[!] No requests captured!")
        
    if os.path.exists(FULL_LOGCAT):
        fsize = os.path.getsize(FULL_LOGCAT)
        print(f"[+] Full logcat size: {fsize} bytes ({FULL_LOGCAT})")
    print("================================================================")
    return True

if __name__ == "__main__":
    run_test()
