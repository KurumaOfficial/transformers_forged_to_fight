"""Decode FastSafeFloat/StatAttribute values for the active fight."""
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADB = str(ROOT / "work" / "platform-tools" / "adb.exe")
ELF = str(ROOT / "work" / "unpacked" / "lib" / "arm64-v8a" / "libil2cpp.so")
SLOT = 0x2C377E0
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


def i32(a):
    b = mem(a, 4)
    return struct.unpack("<i", b)[0] if len(b) == 4 else None


def f32(a):
    b = mem(a, 4)
    return struct.unpack("<f", b)[0] if len(b) == 4 else None


def safe(fsf):
    if not fsf:
        return None
    sv = u64(fsf + 0x10)
    if not sv:
        return None
    ba = u64(sv + 0x10)
    if not ba:
        return None
    n = u32(ba + 0x18)
    data = u64(ba + 0x20)
    if not data or not n or n > 8:
        return ("bad", n, hex(data) if data else None)
    b = mem(data, n)
    val = struct.unpack("<f", b + b"\x00" * (4 - len(b)))[0] if len(b) >= 4 else None
    return (n, b.hex(), val)


A = u64(BASE + SLOT)
CLS = u64(A) if A else None
SF = u64(CLS + 0xB8) if CLS else None
INST = u64(SF + 0x28) if SF else None
fighters = u64(INST + 0xC0) if INST else None
print("pid", pid, "base", hex(BASE), "arbiter", hex(INST) if INST else None)
for i in range(2):
    pc = u64(fighters + 0x20 + i * 8)
    pa = u64(pc + 0x80)
    print(f"\nPC[{i}] pc={hex(pc)} pa={hex(pa)}")
    for off, lab in [(0x68, "health"), (0x70, "mana"), (0x78, "attack"),
                     (0x80, "attackFlat"), (0xF8, "classPower"),
                     (0x100, "classAttackBonus")]:
        p = u64(pa + off)
        print(f"  {lab:18s} obj={hex(p) if p else None} safe={safe(p)} raw28={f32(p+0x28) if p else None}")
