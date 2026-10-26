"""Dump live FighterData.BaseAttributes/Attributes (BCGAttributeData) read-only."""
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADB = str(ROOT / "work" / "platform-tools" / "adb.exe")
ELF = str(ROOT / "work" / "unpacked" / "lib" / "arm64-v8a" / "libil2cpp.so")
SLOT_BA = 0x2C377E0
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


A = u64(BASE + SLOT_BA)
CLS = u64(A) if A else None
SF = u64(CLS + 0xB8) if CLS else None
INST = u64(SF + 0x28) if SF else None
print("BattleArbiter", hex(INST) if INST else None, cname(INST) if INST else None)
if not INST:
    raise SystemExit("no BattleArbiter instance")
fd = u64(INST + 0x88)
print("FightData", hex(fd) if fd else None)
if not fd:
    raise SystemExit("no FightData")
fighters = u64(fd + 0x30)
n = u32(fighters + 0x18) if fighters else 0
print("Fighters length", n)


def dump_attr(label, p):
    print(f"  {label} ptr={hex(p) if p else None} class={cname(p) if p else None}")
    if not p:
        return
    for off, lab, kind in [
        (0x10, "StatMods", "ptr"), (0x18, "SigMods", "ptr"), (0x20, "BuffMods", "ptr"),
        (0x28, "SpecialAttackCount", "i"),
        (0x2C, "HPMax", "i"), (0x30, "HPMaxBase", "i"), (0x34, "HP", "f"),
        (0x38, "Attack", "i"), (0x3C, "AttackBase", "i"), (0x40, "Armor", "f"),
        (0x44, "CritChance", "f"), (0x48, "CritDamage", "f"), (0x4C, "PerfectBlockChance", "f"),
        (0x50, "BlockProficiency", "f"), (0x54, "ManaGain", "f"), (0x58, "ManaStart", "f"),
        (0x5C, "ResistMagic", "f"), (0x60, "ResistPhysical", "f"),
        (0x64, "StunTime", "f"), (0x68, "StunChance", "f"),
        (0x6C, "HeroRating", "i"), (0x70, "HeroRatingHP", "i"), (0x74, "HeroRatingAttack", "i"),
        (0x78, "HeroRatingHPBase", "i"), (0x7C, "HeroRatingAttackBase", "i"),
        (0x80, "isModified", "b"),
        (0x84, "CritRate", "f"), (0x88, "ResistCritRate", "f"), (0x8C, "ResistCritDamage", "f"),
        (0x90, "SpecialBonus", "f"), (0x94, "ProjectileBonus", "f"), (0x98, "ClassPower", "f"),
        (0x9C, "ArmorPenetration", "f"), (0xA0, "BlockPenetration", "f"),
    ]:
        if kind == "f":
            v = f32(p + off)
        elif kind == "i":
            v = i32(p + off)
        elif kind == "b":
            v = mem(p + off, 1).hex()
        else:
            v = u64(p + off)
        print(f"    +{off:#04x} {lab:20s} {v}")


for i in range(min(n or 0, 4)):
    f = u64(fighters + 0x20 + i * 8)
    print(f"\nFighter[{i}] {hex(f) if f else None} {cname(f) if f else None} Id={ilstr(u64(f + 0x10)) if f else None}")
    if not f:
        continue
    dump_attr("BaseAttributes", u64(f + 0x30))
    dump_attr("Attributes", u64(f + 0x38))
