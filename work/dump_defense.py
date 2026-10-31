"""Dump defensive stats for both fighters with corrected SafeValue bytes."""
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADB = str(ROOT / "work" / "platform-tools" / "adb.exe")
ELF = str(ROOT / "work" / "unpacked" / "lib" / "arm64-v8a" / "libil2cpp.so")
SLOT = 0x2C377E0
MASK = (1 << 64) - 1
FNV_PRIME = 0x100000001B3
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


def cstr(a, n=80):
    if not a:
        return None
    b = mem(a, n)
    return b.split(b"\x00")[0].decode("latin1", "replace") if b else None


def cname(o):
    if not o:
        return None
    c = u64(o)
    return cstr(u64(c + 0x10)) if c else None


def ilstr(a):
    if not a:
        return None
    n = u32(a + 0x10)
    if n is None or n > 200:
        return None
    b = mem(a + 0x14, n * 2)
    return b.decode("utf-16le", "replace") if b else None


def fnv64(data, salt):
    h = salt & MASK
    for byte in data:
        h = ((h * FNV_PRIME) & MASK) ^ byte
    return h


def safe(fsf):
    if not fsf:
        return None
    sv = u64(fsf + 0x10)
    if not sv:
        return {"value": 0.0, "note": "no SafeValue"}
    ba = u64(sv + 0x10)
    if not ba:
        return {"value": 0.0, "note": "no byte[]"}
    n = u32(ba + 0x18)
    h = u64(sv + 0x18)
    r = u64(sv + 0x20)
    if n is None or n > 8:
        return {"value": None, "len": n, "note": "bad len"}
    raw = mem(ba + 0x20, n)  # IL2CPP arrays store elements inline at +0x20
    value = struct.unpack("<f", raw + b"\x00" * (4 - len(raw)))[0] if len(raw) >= 4 else None
    return {"value": value, "hash_ok": fnv64(raw, r or 0) == h, "raw": raw.hex(), "len": n}


def stat(ptr):
    if not ptr:
        return None
    return {
        "class": cname(ptr),
        "value": f32(ptr + 0x28),
        "base": safe(u64(ptr + 0x10)),
        "modified": safe(u64(ptr + 0x18)),
        "safe": safe(u64(ptr + 0x20)),
        "def_name": ilstr(u64(u64(ptr + 0x30) + 0x10)) if u64(ptr + 0x30) else None,
    }


A = u64(BASE + SLOT)
CLS = u64(A) if A else None
SF = u64(CLS + 0xB8) if CLS else None
INST = u64(SF + 0x28) if SF else None
fighters = u64(INST + 0xC0)
n = u32(fighters + 0x18) if fighters else 0
print("pid", pid, "base", hex(BASE), "fighters", n)
for i in range(min(n or 0, 2)):
    pc = u64(fighters + 0x20 + i * 8)
    pa = u64(pc + 0x80)
    print(f"\n===== PC[{i}] =====")
    for off, lab in [
        (0x78, "attack"), (0x80, "attackFlat"), (0x98, "armorRating"),
        (0xA8, "armorFlat"), (0xB0, "critRating"), (0xB8, "critChanceMod"),
        (0xC0, "critDamage"), (0x108, "blockProf"), (0x110, "perfectBlock"),
        (0x130, "protection"), (0x1B0, "indestructible"), (0x1B8, "invulnerable"),
        (0x1A8, "unblockableImmune"), (0x198, "unstoppable"),
    ]:
        p = u64(pa + off)
        if p:
            print(f"  {lab:18s}", stat(p))
    dr = u64(pa + 0x228)
    print("  damageResistances", hex(dr) if dr else None, cname(dr) if dr else None)
    if dr:
        d = u64(dr + 0x10)
        cnt = i32(d + 0x20) if d else 0
        entries = u64(d + 0x18) if d else None
        print("    map count", cnt)
        for j in range(min(cnt or 0, 20)):
            e = entries + 0x20 + j * 24
            k = u64(e + 8)
            v = f32(e + 16)
            print("    ", ilstr(k), v)
