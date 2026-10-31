"""Raw layout audit for _attack and _health (read-only)."""
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


def raw(a, n):
    b = mem(a, n)
    return b, b.hex()


def qwords(b):
    return [hex(struct.unpack_from("<Q", b, i)[0]) for i in range(0, len(b) - 7, 8)]


def floats(b):
    return [struct.unpack_from("<f", b, i)[0] for i in range(0, len(b) - 3, 4)]


A = u64(BASE + SLOT)
CLS = u64(A) if A else None
SF = u64(CLS + 0xB8) if CLS else None
INST = u64(SF + 0x28) if SF else None
fighters = u64(INST + 0xC0)
pc = u64(fighters + 0x20)
pa = u64(pc + 0x80)
print("pid", pid, "base", hex(BASE), "PA", hex(pa))

attack = u64(pa + 0x78)
health = u64(pa + 0x68)
for label, p, n in [("attack", attack, 0x40), ("health", health, 0x50)]:
    b, hx = raw(p, n)
    print(f"\n{label} {hex(p)}")
    print(" bytes", hx)
    print(" qwords", qwords(b))
    print(" floats", [round(x, 5) for x in floats(b)])

# Follow attack base/modified/safe
for off, lab in [(0x10, "attack.base"), (0x18, "attack.modified"), (0x20, "attack.safe")]:
    fsf = u64(attack + off)
    print(f"\n{lab} fsf={hex(fsf) if fsf else None}")
    if not fsf:
        continue
    b, hx = raw(fsf, 0x30)
    print(" fsf bytes", hx)
    print(" fsf qwords", qwords(b))
    sv = u64(fsf + 0x10)
    print(" sv", hex(sv) if sv else None)
    if sv:
        b2, hx2 = raw(sv, 0x30)
        print(" sv bytes", hx2)
        print(" sv qwords", qwords(b2))
        ba = u64(sv + 0x10)
        print(" ba", hex(ba) if ba else None)
        if ba:
            b3, hx3 = raw(ba, 0x30)
            print(" ba bytes", hx3)
            print(" ba qwords", qwords(b3))
            n3 = struct.unpack_from("<I", b3, 0x18)[0] if len(b3) >= 0x1C else None
            data = struct.unpack_from("<Q", b3, 0x20)[0] if len(b3) >= 0x28 else None
            print(" ba len", n3, "data", hex(data) if data else None)
            if data and n3 and n3 <= 16:
                b4, hx4 = raw(data, n3)
                print(" data bytes", hx4)

# Follow health amount/max
for off, lab in [(0x18, "health.amount"), (0x28, "health.max")]:
    fsf = u64(health + off)
    print(f"\n{lab} fsf={hex(fsf) if fsf else None}")
    if not fsf:
        continue
    b, hx = raw(fsf, 0x30)
    print(" fsf bytes", hx)
    print(" fsf qwords", qwords(b))
    sv = u64(fsf + 0x10)
    print(" sv", hex(sv) if sv else None)
    if sv:
        b2, hx2 = raw(sv, 0x30)
        print(" sv bytes", hx2)
        print(" sv qwords", qwords(b2))
        ba = u64(sv + 0x10)
        print(" ba", hex(ba) if ba else None)
        if ba:
            b3, hx3 = raw(ba, 0x30)
            print(" ba bytes", hx3)
            print(" ba qwords", qwords(b3))
            n3 = struct.unpack_from("<I", b3, 0x18)[0] if len(b3) >= 0x1C else None
            data = struct.unpack_from("<Q", b3, 0x20)[0] if len(b3) >= 0x28 else None
            print(" ba len", n3, "data", hex(data) if data else None)
            if data and n3 and n3 <= 16:
                b4, hx4 = raw(data, n3)
                print(" data bytes", hx4)
