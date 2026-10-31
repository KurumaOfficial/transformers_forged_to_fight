"""Read TuningGameplay SafeFloat fields (read-only)."""
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADB = str(ROOT / "work" / "platform-tools" / "adb.exe")
ELF = str(ROOT / "work" / "unpacked" / "lib" / "arm64-v8a" / "libil2cpp.so")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def adb(args, timeout=120):
    return subprocess.run([ADB] + args, capture_output=True, timeout=timeout)


pid = adb(["shell", "pidof com.kabam.bigrobot"]).stdout.decode().strip()
elf = open(ELF, "rb").read()
e_phoff = struct.unpack_from("<Q", elf, 32)[0]
e_phentsize = struct.unpack_from("<H", elf, 54)[0]
e_phnum = struct.unpack_from("<H", elf, 56)[0]
wv = None
for i in range(e_phnum):
    o = e_phoff + i * e_phentsize
    t, fl, fo, va, pa, fs, ms, al = struct.unpack_from("<IIQQQQQQ", elf, o)
    if t == 1 and (fl & 2):
        wv = va
maps = adb(["shell", f"su 0 cat /proc/{pid}/maps"]).stdout.decode("latin1", "replace")
BASE = None
for line in maps.splitlines():
    if "libil2cpp.so" in line and "rw-p" in line and "02a97000" in line:
        BASE = int(line.split("-")[0], 16) - wv
        break


def mem(a, n=8):
    return adb(["exec-out", "su", "0", "dd", f"if=/proc/{pid}/mem", "bs=1", f"count={n}",
                f"skip={a}", "status=none"]).stdout


def u64(a):
    b = mem(a, 8)
    return struct.unpack("<Q", b)[0] if len(b) == 8 else None


def u32(a):
    b = mem(a, 4)
    return struct.unpack("<I", b)[0] if len(b) == 4 else None


def safe_float(sv):
    if not sv:
        return None
    ba = u64(sv + 0x10)
    if not ba:
        return None
    n = u32(ba + 0x18)
    raw = mem(ba + 0x20, n) if n and n <= 8 else b""
    return (n, raw.hex(), struct.unpack("<f", raw)[0] if len(raw) >= 4 else None)


# TuningGameplay.get_Instance: slot -> type info -> class -> static +0xb8 -> instance
p = u64(BASE + 0x2BE0000 + 0x348)
cls = u64(p) if p else None
sf = u64(cls + 0xB8) if cls else None
inst = u64(sf) if sf else None
print("pid", pid, "base", hex(BASE), "instance", hex(inst) if inst else None)
if not inst:
    raise SystemExit("no TuningGameplay")
for off, lab in [(0x18, "ManaPerSpecial"), (0x20, "ArmorRatingConstant"),
                 (0x28, "CritRatingConstant_A"), (0x30, "DefenderManaModifier"),
                 (0x38, "DefenderManaBlockedModifier"), (0x40, "AttackChainResetTime"),
                 (0x48, "EvadeMeleeSpeed"), (0x50, "MeleeRangeMod")]:
    print(f"{lab:26s}", safe_float(u64(inst + off)))
