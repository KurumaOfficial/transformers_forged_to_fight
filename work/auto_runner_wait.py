import subprocess
import time
import os
import sys

ADB = r".\work\platform-tools\adb.exe"
APK = r".\work\patched_build\tftf_patched_v9.2.0.apk"
LOGCAT_FILE = r".\work\logcat.txt"

def get_devices():
    res = subprocess.run([ADB, "devices"], capture_output=True, text=True)
    lines = res.stdout.strip().split("\n")[1:]
    devices = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 2:
            devices.append((parts[0], parts[1]))
    return devices

def run_pipeline():
    print("=======================================================", flush=True)
    print("  TFTF Automated Launch & Logcat Pipeline (Active)", flush=True)
    print("=======================================================", flush=True)
    print("[*] Listening for phone USB Debugging (timeout 600s)...", flush=True)
    
    start_time = time.time()
    device_found = None
    last_status = None
    
    while time.time() - start_time < 600:
        devs = get_devices()
        if devs:
            dev_id, status = devs[0]
            if status != last_status:
                print(f"[*] Detected device {dev_id} with status: '{status}'", flush=True)
                last_status = status
                
            if status == "device":
                device_found = dev_id
                print(f"[+] Device fully authorized: {dev_id}!", flush=True)
                break
            elif status == "unauthorized":
                print(f"[!] Device {dev_id} is UNAUTHORIZED. Please accept the prompt on phone screen!", flush=True)
        time.sleep(3)
        
    if not device_found:
        print("[!] Timeout (600s): Phone still not recognized by ADB.", flush=True)
        return False
        
    print(f"\n[*] Step 1: Setting up port reverse (tcp:8080 -> tcp:8080)...", flush=True)
    subprocess.run([ADB, "reverse", "tcp:8080", "tcp:8080"], check=True)
    print("[+] Port reverse active.", flush=True)
    
    print(f"\n[*] Step 2: Installing patched APK ({os.path.basename(APK)})...", flush=True)
    install_res = subprocess.run([ADB, "install", "-r", APK], capture_output=True, text=True)
    print(install_res.stdout, flush=True)
    if "Success" not in install_res.stdout:
        print("[!] Install error:", install_res.stderr, flush=True)
        return False
    print("[+] APK installed successfully.", flush=True)
    
    print(f"\n[*] Step 3: Clearing logcat buffer...", flush=True)
    subprocess.run([ADB, "logcat", "-c"])
    
    print(f"\n[*] Step 4: Starting logcat capture to {LOGCAT_FILE}...", flush=True)
    log_file = open(LOGCAT_FILE, "w", encoding="utf-8", errors="replace")
    logcat_proc = subprocess.Popen(
        [ADB, "logcat", "-v", "time", "-s", "Unity:V", "ActivityManager:I", "Sparx:V", "CRASH:E", "*:E"],
        stdout=log_file,
        stderr=subprocess.DEVNULL
    )
    print(f"[+] Logcat PID: {logcat_proc.pid}", flush=True)
    
    print(f"\n[*] Step 5: Launching Transformers: Forged to Fight (com.kabam.bigrobot)...", flush=True)
    launch_res = subprocess.run(
        [ADB, "shell", "monkey", "-p", "com.kabam.bigrobot", "-c", "android.intent.category.LAUNCHER", "1"],
        capture_output=True, text=True
    )
    print(launch_res.stdout, flush=True)
    
    print("\n[*] Step 6: Waiting 20 seconds for initial client boot & network handshake...", flush=True)
    time.sleep(20)
    
    req_file = r".\server\requests.jsonl"
    if os.path.exists(req_file):
        with open(req_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = [l.strip() for l in f if l.strip()]
        print(f"[+] Total requests logged so far: {len(lines)}", flush=True)
        print("Last requests:", flush=True)
        for l in lines[-10:]:
            print("  ", l[:160], flush=True)
            
    print("\n[+] Pipeline run complete! Inspecting results.", flush=True)
    return True

if __name__ == "__main__":
    run_pipeline()
