"""Dump live BattleArbiter.FightData.Fighters and blueprint tags (read-only)."""
import struct
import subprocess
import sys

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADB = str(ROOT / "work" / "platform-tools" / "adb.exe")
ELF = str(ROOT / "work" / "unpacked" / "lib" / "arm64-v8a" / "libil2cpp.so")
SLOT_BA = 0x2C377E0

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def adb(args):
    return subprocess.run([ADB] + args, capture_output=True, timeout=120)


PID = adb(["shell", "pidof com.kabam.bigrobot"]).stdout.decode().strip()
if not PID:
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
maps = adb(["shell", f"su 0 cat /proc/{PID}/maps"]).stdout.decode("latin1", "replace")
BASE = None
for line in maps.splitlines():
    if "libil2cpp.so" in line and "rw-p" in line and "02a97000" in line:
        BASE = int(line.split("-")[0], 16) - wv
        break
if BASE is None:
    raise SystemExit("no base")
print("pid", PID, "base", hex(BASE))


def mem(a, n=8):
    return adb(["exec-out", "su", "0", "dd", f"if=/proc/{PID}/mem", "bs=1", f"count={n}",
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


def dump_list(label, ptr):
    print(f"    {label} ptr={hex(ptr) if ptr else None} class={cname(ptr) if ptr else None}")
    if not ptr:
        return
    size = i32(ptr + 0x18)
    items = u64(ptr + 0x10)
    print(f"      size={size} items={hex(items) if items else None}")
    for j in range(min(size or 0, 10)):
        it = u64(items + 0x20 + j * 8) if items else None
        print(f"      [{j}] {ilstr(it)!r}")


A = u64(BASE + SLOT_BA)
CLS = u64(A) if A else None
SF = u64(CLS + 0xB8) if CLS else None
INST = u64(SF + 0x28) if SF else None
print("BattleArbiter class", hex(CLS) if CLS else None, cname(INST) if INST else None,
      "instance", hex(INST) if INST else None)
if not INST:
    raise SystemExit("no BattleArbiter instance")
fd = u64(INST + 0x88)
print("FightData", hex(fd) if fd else None, cname(fd) if fd else None)
if not fd:
    raise SystemExit("no FightData")
fighters = u64(fd + 0x30)
print("Fighters", hex(fighters) if fighters else None, cname(fighters) if fighters else None)
if not fighters:
    raise SystemExit("no Fighters array")
n = u32(fighters + 0x18)
print("Fighters length", n)
for i in range(min(n or 0, 4)):
    f = u64(fighters + 0x20 + i * 8)
    print(f"\nFighter[{i}] {hex(f) if f else None} {cname(f) if f else None}")
    if not f:
        continue
    print("  Id", ilstr(u64(f + 0x10)))
    bp = u64(f + 0x40)
    print("  Blueprint", hex(bp) if bp else None, cname(bp) if bp else None)
    if bp:
        dump_list("Tags", u64(bp + 0xB8))
        dump_list("BaseDamageType", u64(bp + 0x90))
        dump_list("BaseRangedDamageType", u64(bp + 0x98))
        dump_list("SynergyBonuses", u64(bp + 0xE0))
