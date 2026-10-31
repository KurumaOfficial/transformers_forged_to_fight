import subprocess
import time
import os
import sys

ADB = r".\work\platform-tools\adb.exe"
APK = r".\work\patched_build\tftf_patched_v9.2.0.apk"
LOGCAT_FILE = r".\work\logcat.txt"

def check_adb_devices():
    res = subprocess.run([ADB, "devices"], capture_output=True, text=True)
    lines = res.stdout.strip().split("\n")[1:]
    devices = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 2:
            devices.append((parts[0], parts[1]))
    return devices

def main():
    print("[*] TFTF Auto-Runner started.")
    print(f"[*] Monitoring for connected Android phone via {ADB}...")
    
    devices = check_adb_devices()
    if not devices:
        print("[!] No ADB devices found yet.")
        print("[!] ACTION REQUIRED ON PHONE:")
        print("    1. Откройте Настройки -> О телефоне -> нажмите 7 раз на 'Номер сборки' (Build number).")
        print("    2. Настройки -> Система -> Для разработчиков -> Включите 'Отладка по USB' (USB Debugging).")
        print("    3. На экране телефона появится запрос: 'Разрешить отладку по USB?'. Поставьте галочку 'Всегда' и нажмите 'Разрешить'.")
        return False
        
    dev_id, status = devices[0]
    print(f"[+] Found device: {dev_id} (Status: {status})")
    
    if status == "unauthorized":
        print("[!] Device is UNAUTHORIZED. Please accept the 'Allow USB debugging' prompt on the phone screen!")
        return False
        
    if status != "device":
        print(f"[!] Device status is '{status}'. Please reconnect USB.")
        return False
        
    print(f"[*] Setting up reverse port forwarding (tcp:8080 -> tcp:8080)...")
    subprocess.run([ADB, "reverse", "tcp:8080", "tcp:8080"], check=True)
    
    print(f"[*] Installing patched APK: {APK}...")
    install_res = subprocess.run([ADB, "install", "-r", APK], capture_output=True, text=True)
    print(install_res.stdout)
    if "Success" not in install_res.stdout:
        print("[!] Installation output:", install_res.stderr)
        
    print(f"[*] Clearing logcat buffer...")
    subprocess.run([ADB, "logcat", "-c"])
    
    print(f"[*] Starting background logcat capture to {LOGCAT_FILE}...")
    logcat_cmd = f'"{ADB}" logcat -v time -s Unity:V ActivityManager:I Sparx:V CRASH:E *:E'
    # Start logcat process
    logcat_proc = subprocess.Popen([ADB, "logcat", "-v", "time", "-s", "Unity:V", "ActivityManager:I", "Sparx:V", "CRASH:E", "*:E"],
                                   stdout=open(LOGCAT_FILE, "w", encoding="utf-8", errors="replace"),
                                   stderr=subprocess.DEVNULL)
                                   
    print(f"[*] Launching game com.kabam.bigrobot...")
    launch_res = subprocess.run([ADB, "shell", "monkey", "-p", "com.kabam.bigrobot", "-c", "android.intent.category.LAUNCHER", "1"],
                                capture_output=True, text=True)
    print(launch_res.stdout)
    
    print("[SUCCESS] Game launched on phone! Monitoring traffic...")
    return True

if __name__ == "__main__":
    main()
