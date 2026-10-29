"""Read last hit results and attack stats for the active fight."""
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


A = u64(BASE + SLOT)
CLS = u64(A) if A else None
SF = u64(CLS + 0xB8) if CLS else None
INST = u64(SF + 0x28) if SF else None
print("pid", pid, "BattleArbiter", hex(INST) if INST else None)
if not INST:
    raise SystemExit("no BattleArbiter")
state = u64(INST + 0x48)
print("state", hex(state) if state else None)
fighters = u64(INST + 0xC0)
n = u32(fighters + 0x18) if fighters else 0
for i in range(n or 0):
    pc = u64(fighters + 0x20 + i * 8)
    if not pc:
        continue
    print(f"\nPC[{i}] {hex(pc)} id={i32(pc+0xf4)} transformed={mem(pc+0x138,1).hex()} input={mem(pc+0x139,1).hex()}")
    pa = u64(pc + 0x80)
    atk = u64(pa + 0x78) if pa else None
    cp = u64(pa + 0xf8) if pa else None
    print("  attack", f32(atk + 0x28) if atk else None, "classPower", f32(cp + 0x28) if cp else None,
          "attackBonus", i32(pc + 0x4c) if pc else None)
    hr = u64(pc + 0x120)
    print("  LastHitResult", hex(hr) if hr else None)
    if hr:
        print("    Flags", i32(hr + 0x20), "AttackLevel", i32(hr + 0x24),
              "DamageType", hex(u64(hr + 0x28) or 0) if hr else None,
              "Damage", f32(hr + 0x3c), "DamageRating", f32(hr + 0x40),
              "IsDeathBlow", mem(hr + 0x44, 1).hex(),
              "Instigator", i32(hr + 0x18), "Target", i32(hr + 0x1c))
