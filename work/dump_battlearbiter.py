"""Read BattleArbiter singleton/state and static spawn arrays (read-only)."""
import struct
import subprocess

ADB = r"C:\Users\gameg\Desktop\TFTF\work\platform-tools\adb.exe"
ELF = r"C:\Users\gameg\Desktop\TFTF\work\unpacked\lib\arm64-v8a\libil2cpp.so"
SLOT = 0x2C377E0

pid = subprocess.run([ADB, "shell", "pidof com.kabam.bigrobot"], capture_output=True, text=True).stdout.strip()
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
maps = subprocess.run([ADB, "shell", f"su 0 cat /proc/{pid}/maps"], capture_output=True, text=True).stdout
BASE = None
for line in maps.splitlines():
    if "libil2cpp.so" in line and "rw-p" in line and "02a97000" in line:
        BASE = int(line.split("-")[0], 16) - wv
        break
print("pid", pid, "base", hex(BASE))


def mem(a, n=8):
    return subprocess.run([ADB, "exec-out", "su", "0", "dd", f"if=/proc/{pid}/mem",
                           "bs=1", f"count={n}", f"skip={a}", "status=none"], capture_output=True).stdout


def u64(a):
    b = mem(a, 8)
    return struct.unpack("<Q", b)[0] if len(b) == 8 else None


def u32(a):
    b = mem(a, 4)
    return struct.unpack("<I", b)[0] if len(b) == 4 else None


def cstr(a, n=80):
    b = mem(a, n)
    return b.split(b"\x00")[0].decode("latin1", "replace") if b else None


def cname(o):
    if not o:
        return None
    c = u64(o)
    return cstr(u64(c + 0x10)) if c else None


A = u64(BASE + SLOT)
CLS = u64(A) if A else None
print("class", hex(CLS) if CLS else None, cstr(u64(CLS + 0x10)) if CLS else None)
SF = u64(CLS + 0xB8) if CLS else None
print("static", hex(SF) if SF else None)
if not SF:
    raise SystemExit("no static")
for off, lab in [(0x0, "FighterStartPositions"), (0x8, "FighterStartRotations"),
                 (0x10, "FighterReferenceScales")]:
    arr = u64(SF + off)
    print(lab, hex(arr) if arr else None)
    if arr:
        print("  count", u32(arr + 0x18), "data", hex(u64(arr + 0x10)))
        data = u64(arr + 0x10)
        if data:
            for i in range(min(u32(arr + 0x18) or 0, 4)):
                b = mem(data + 0x20 + i * 12, 12)
                if len(b) == 12:
                    print("   ", i, struct.unpack("<fff", b))
inst = u64(SF + 0x28)
print("Instance", hex(inst) if inst else None, cname(inst) if inst else None)
if inst:
    for off, lab in [(0x38, "_states"), (0x40, "_queuedStates"), (0x48, "_state"),
                     (0x50, "_activeCoroutine"), (0x58, "_running")]:
        if off == 0x58:
            print(f"  +{off:#x} {lab}", mem(inst + off, 1).hex())
        else:
            v = u64(inst + off)
            print(f"  +{off:#x} {lab}", hex(v) if v else None, cname(v) if v else None)
    state = u64(inst + 0x48)
    if state:
        print("state class", cname(state))
        for off, lab in [(0x10, "StateName"), (0x18, "StateMachine")]:
            v = u64(state + off)
            print(f"  state +{off:#x} {lab}", hex(v) if v else None, cname(v) if v else None)
