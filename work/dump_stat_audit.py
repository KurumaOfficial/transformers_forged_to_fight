"""Audit StatAttribute/ResourceAttribute safe values in the live fight.

Read-only /proc/pid/mem. Compares _attack (broken) with _health/_hpMax-like
attributes (working). Decodes FastSafeFloat -> SafeValue byte[] + FNV64 hash.
"""
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
if not pid:
    raise SystemExit("app not running")
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
if BASE is None:
    raise SystemExit("no base")


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


def safe_value(fsf_ptr):
    """FastSafeFloat -> (plain value, hash_ok, bytes, _h, _r, len)."""
    if not fsf_ptr:
        return None
    sv = u64(fsf_ptr + 0x10)  # SafeValue object
    if not sv:
        return {"value": 0.0, "hash_ok": None, "note": "no SafeValue"}
    ba = u64(sv + 0x10)  # byte[]
    if not ba:
        return {"value": 0.0, "hash_ok": None, "note": "no byte[]"}
    n = u32(ba + 0x18)
    data_ptr = u64(ba + 0x20)
    h = u64(sv + 0x18)
    r = u64(sv + 0x20)
    if not data_ptr or n is None or n > 8:
        return {"value": None, "hash_ok": False, "len": n, "data": hex(data_ptr or 0),
                "h": h, "r": r, "note": "bad byte[]"}
    raw = mem(data_ptr, n)
    value = struct.unpack("<f", raw + b"\x00" * (4 - len(raw)))[0] if len(raw) >= 4 else None
    hash_ok = fnv64(raw, r or 0) == h
    return {"value": value, "hash_ok": hash_ok, "raw": raw.hex(), "h": h, "r": r,
            "len": n}


def stat(ptr):
    if not ptr:
        return None
    d = {"class": cname(ptr), "value": f32(ptr + 0x28)}
    base = u64(ptr + 0x10)
    mod = u64(ptr + 0x18)
    safe = u64(ptr + 0x20)
    deff = u64(ptr + 0x30)
    d["base"] = safe_value(base)
    d["modified"] = safe_value(mod)
    d["safe"] = safe_value(safe)
    if deff:
        d["def_name"] = ilstr(u64(deff + 0x10))
        d["def_min"] = f32(deff + 0x28)
        d["def_max"] = f32(deff + 0x2c)
        d["def_default"] = f32(deff + 0x24)
    return d


def resource(ptr):
    if not ptr:
        return None
    d = {"class": cname(ptr)}
    for off, lab in [(0x18, "amount"), (0x20, "prev"), (0x28, "max"),
                     (0x30, "start"), (0x38, "base")]:
        d[lab] = safe_value(u64(ptr + off))
    deff = u64(ptr + 0x40)
    if deff:
        d["def_name"] = ilstr(u64(deff + 0x10))
        d["def_min"] = f32(deff + 0x28)
        d["def_max"] = f32(deff + 0x2c)
    return d


def bcgattr(ptr):
    if not ptr:
        return None
    return {
        "class": cname(ptr),
        "HPMax": i32(ptr + 0x2c), "HP": f32(ptr + 0x34),
        "Attack": i32(ptr + 0x38), "Armor": f32(ptr + 0x40),
        "CritChance": f32(ptr + 0x44), "CritDamage": f32(ptr + 0x48),
        "PBC": f32(ptr + 0x4c), "Block": f32(ptr + 0x50),
        "ManaGain": f32(ptr + 0x54), "ManaStart": f32(ptr + 0x58),
        "ClassPower": f32(ptr + 0xa0), "ArmorPen": f32(ptr + 0xa4),
        "BlockPen": f32(ptr + 0xa8),
    }


A = u64(BASE + SLOT)
CLS = u64(A) if A else None
SF = u64(CLS + 0xB8) if CLS else None
INST = u64(SF + 0x28) if SF else None
if not INST:
    raise SystemExit("no BattleArbiter")
fighters = u64(INST + 0xC0)
n = u32(fighters + 0x18) if fighters else 0
print("pid", pid, "base", hex(BASE), "arbiter", hex(INST), "fighters", n)
for i in range(min(n or 0, 2)):
    pc = u64(fighters + 0x20 + i * 8)
    pa = u64(pc + 0x80) if pc else None
    print(f"\n===== PC[{i}] {hex(pc) if pc else None} PA={hex(pa) if pa else None} =====")
    if not pa:
        continue
    print("baseAttrs", bcgattr(u64(pa + 0x50)))
    print("attrs", bcgattr(u64(pa + 0x58)))
    print("health", resource(u64(pa + 0x68)))
    print("mana", resource(u64(pa + 0x70)))
    for off, lab in [(0x78, "attack"), (0x80, "attackFlat"),
                     (0x98, "armorRating"), (0xA0, "armorPen"),
                     (0xA8, "armorFlat"), (0xB0, "critRating"),
                     (0xB8, "critChanceMod"), (0xC0, "critDamage"),
                     (0x108, "blockProf"), (0x110, "perfectBlock"),
                     (0xF8, "classPower"), (0x100, "classAttackBonus")]:
        p = u64(pa + off)
        if p:
            print(f"{lab:16s}", stat(p))
