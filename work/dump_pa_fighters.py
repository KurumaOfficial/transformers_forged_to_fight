"""Read BattleArbiter._fighters[*].Attributes and attack/health (read-only)."""
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


A = u64(BASE + SLOT)
CLS = u64(A) if A else None
SF = u64(CLS + 0xB8) if CLS else None
INST = u64(SF + 0x28) if SF else None
print("BattleArbiter", hex(INST) if INST else None)
if not INST:
    raise SystemExit("no BattleArbiter")
fighters = u64(INST + 0xC0)
n = u32(fighters + 0x18) if fighters else 0
print("PlayerControllers", hex(fighters) if fighters else None, "count", n)


def attr(label, p):
    print(f"  {label} {hex(p) if p else None} {cname(p) if p else None}")
    if not p:
        return
    print(f"    HPMax={i32(p+0x2c)} HP={f32(p+0x34)} Attack={i32(p+0x38)} "
          f"Armor={f32(p+0x40)} Crit={f32(p+0x44)} CD={f32(p+0x48)} "
          f"Block={f32(p+0x50)} ManaGain={f32(p+0x54)} ManaStart={f32(p+0x58)}")


for i in range(min(n or 0, 4)):
    pc = u64(fighters + 0x20 + i * 8)
    print(f"\nPC[{i}] {hex(pc) if pc else None} {cname(pc) if pc else None} id={i32(pc+0xf4) if pc else None}")
    if not pc:
        continue
    pa = u64(pc + 0x80)
    print("  PlayerAttributes", hex(pa) if pa else None)
    if not pa:
        continue
    print("  SignatureLevel", i32(pa + 0x38), "Class", i32(pa + 0x3c))
    attr("BaseAttributes", u64(pa + 0x50))
    attr("Attributes", u64(pa + 0x58))
    atk = u64(pa + 0x78)
    print("  _attack", hex(atk) if atk else None, "value", f32(atk + 0x28) if atk else None,
          "base", f32(atk + 0x10) if atk else None)
    hp = u64(pa + 0x68)
    print("  _health", hex(hp) if hp else None)
    if hp:
        raw = mem(hp, 0x48)
        for off in range(0, 0x48, 4):
            print(f"    health+{off:#04x} u32={struct.unpack_from('<I', raw, off)[0] if len(raw)>=off+4 else None} "
                  f"f={struct.unpack_from('<f', raw, off)[0] if len(raw)>=off+4 else None}")
    cp = u64(pa + 0xf8)
    print("  _classPower", hex(cp) if cp else None, "value", f32(cp + 0x28) if cp else None)
    cab = u64(pa + 0x100)
    print("  _classAttackBonus", hex(cab) if cab else None, "value", f32(cab + 0x28) if cab else None)
