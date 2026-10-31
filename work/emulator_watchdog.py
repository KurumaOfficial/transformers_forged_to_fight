"""TFTF emulator watchdog: check, restart, boot, reverse, install, launch.

Read-only with respect to the APK; it only starts the AVD and installs the
already-built APK when the package is missing. No new software is installed.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(r".")
ADB = ROOT / "work" / "platform-tools" / "adb.exe"
EMULATOR = ROOT / "work" / "android-sdk" / "emulator" / "emulator.exe"
AVD = "TFTF_AVD"
PKG = "com.kabam.bigrobot"
ACT = "com.kabam.bigrobot/com.explodingbarrel.Activity"
LOG_DIR = ROOT / "work"
LOCK_DIR = Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".android" / "avd" / f"{AVD}.avd"

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def run(*args, timeout=120, binary=False):
    p = subprocess.run([str(a) for a in args], capture_output=True, timeout=timeout)
    return p.returncode, (p.stdout if binary else (p.stdout or b"").decode("utf-8", "replace"))


def adb(*args, timeout=120):
    return run(ADB, *args, timeout=timeout)


def device_present():
    rc, out = adb("devices")
    return bool(re.search(r"emulator-\d+\s+device", out))


def booted():
    if not device_present():
        return False
    rc, out = adb("shell", "getprop", "sys.boot_completed", timeout=30)
    return out.strip() == "1"


def wait_boot(timeout=180):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if booted():
            return True
        time.sleep(3)
    return False


def kill_emulator():
    try:
        adb("emu", "kill", timeout=15)
    except Exception:
        pass
    time.sleep(3)
    ps = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'TFTF_AVD' } | "
         "ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"],
        capture_output=True, text=True,
    )
    time.sleep(2)


def clear_locks():
    for name in ("hardware-qemu.ini.lock", "multiinstance.lock"):
        p = LOCK_DIR / name
        try:
            if p.is_dir():
                for child in p.glob("*"):
                    child.unlink(missing_ok=True)
                p.rmdir()
            elif p.exists():
                p.unlink()
        except Exception:
            pass


def start_emulator(windowed=False, gpu="angle_indirect", wipe=False):
    clear_locks()
    args = [EMULATOR, "-avd", AVD, "-no-snapshot", "-no-audio", "-gpu", gpu]
    if not windowed:
        args.append("-no-window")
    if wipe:
        args.append("-wipe-data")
    out = LOG_DIR / "watchdog_emulator.out.log"
    err = LOG_DIR / "watchdog_emulator.err.log"
    subprocess.Popen(args, cwd=str(ROOT), stdout=out.open("wb"), stderr=err.open("wb"))
    return wait_boot(240)


def ensure_reverse():
    adb("reverse", "tcp:8080", "tcp:8080", timeout=30)


def package_installed():
    rc, out = adb("shell", "pm", "list", "packages", PKG, timeout=30)
    return PKG in out


def install_apk():
    apks = sorted(ROOT.glob("com.kabam.bigrobot_9.2.0*.apk"))
    if not apks:
        return False
    rc, out = adb("install", "-r", str(apks[0]), timeout=300)
    return rc == 0


def launch():
    adb("shell", "am", "start", "-n", ACT, timeout=30)


def snapshot_save(name="tftf_home"):
    rc, out = adb("emu", "avd", "snapshot", "save", name, timeout=120)
    return rc == 0, out


def snapshot_load(name="tftf_home"):
    rc, out = adb("emu", "avd", "snapshot", "load", name, timeout=120)
    return rc == 0, out


def ensure(windowed=False, gpu="angle_indirect", wipe=False, launch_app=True):
    if booted():
        ensure_reverse()
        if launch_app and not package_installed():
            install_apk()
        return True
    if device_present():
        kill_emulator()
    if not start_emulator(windowed=windowed, gpu=gpu, wipe=wipe):
        return False
    ensure_reverse()
    if not package_installed() and not install_apk():
        return False
    if launch_app:
        launch()
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--ensure", action="store_true")
    ap.add_argument("--restart", action="store_true")
    ap.add_argument("--wipe", action="store_true")
    ap.add_argument("--windowed", action="store_true")
    ap.add_argument("--gpu", default="angle_indirect")
    ap.add_argument("--save-snapshot", nargs="?", const="tftf_home")
    ap.add_argument("--load-snapshot", nargs="?", const="tftf_home")
    args = ap.parse_args()

    if args.check:
        print({"device": device_present(), "booted": booted(), "package": package_installed()})
        return 0 if booted() else 1
    if args.restart:
        kill_emulator()
    if args.save_snapshot:
        print(snapshot_save(args.save_snapshot))
        return 0
    if args.load_snapshot:
        print(snapshot_load(args.load_snapshot))
        return 0
    ok = ensure(windowed=args.windowed, gpu=args.gpu, wipe=args.wipe)
    print({"ok": ok, "device": device_present(), "booted": booted()})
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
