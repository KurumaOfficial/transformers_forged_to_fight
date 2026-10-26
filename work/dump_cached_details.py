"""Dump BCGManager._heroBaseAttributeData[bid][rank] (the cached team details)."""
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
print("pid", pid, "base", hex(BASE))


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


def cstr(a, n=80):
    if not a:
        return None
    b = mem(a, n)
    return b.split(b"\x00")[0].decode("latin1", "replace") if b else None


def ilstr(a):
    if not a:
        return None
    n = u32(a + 0x10)
    if n is None or n > 200:
        return None
    b = mem(a + 0x14, n * 2)
    return b.decode("utf-16le", "replace") if b else None


def cname(o):
    if not o:
        return None
    c = u64(o)
    return cstr(u64(c + 0x10)) if c else None


def entries(d):
    if not d:
        return []
    e = u64(d + 0x18)
    n = i32(d + 0x20)
    out = []
    for i in range(min(n or 0, 500)):
        base = e + 0x20 + i * 24
        if i32(base) is not None and i32(base) >= 0:
            k = u64(base + 8)
            v = u64(base + 16)
            if k:
                out.append((k, v))
    return out


def manager():
    slot = u64(BASE + 0x2BC1000 + 0xC68)
    c0 = u64(slot) if slot else None
    w = u64(c0 + 0x18) if c0 else None
    x = u64(w + 0xC0) if w else None
    c = u64(x) if x else None
    sf = u64(c + 0xB8) if c else None
    return u64(sf) if sf else None


I = manager()
print("manager", hex(I) if I else None, cname(I) if I else None)
cache = u64(I + 0xB0)
print("cache", hex(cache) if cache else None, cname(cache) if cache else None)
for k, v in entries(cache):
    name = ilstr(k)
    if name not in ("bumblebee_cin_dotm_2", "sideswipe_gs"):
        continue
    print("\nbid", name, "ranks", hex(v) if v else None, cname(v) if v else None)
    for rk, det in entries(v):
        rank = i32(rk) if rk and rk > 0x1000 else rk
        print(" rank", rank, "details", hex(det) if det else None, cname(det) if det else None)
        if not det:
            continue
        print("   owns?", mem(det + 0x38, 1).hex(), "level", i32(det + 0x1C), "sig", i32(det + 0x20),
              "HPMax", i32(det + 0x28), "Attack", i32(det + 0x30))
        attr = u64(det + 0x40)
        print("   attr", hex(attr) if attr else None, cname(attr) if attr else None)
        if attr:
            for off, lab in [(0x2C, "HPMax"), (0x34, "HP"), (0x38, "Attack"), (0x40, "Armor"),
                             (0x44, "CritChance"), (0x48, "CritDamage"), (0x50, "BlockProf"),
                             (0x54, "ManaGain"), (0x58, "ManaStart")]:
                val = i32(attr + off) if lab in ("HPMax", "Attack") else f32(attr + off)
                print(f"     +{off:#x} {lab} {val}")
