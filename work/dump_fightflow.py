"""Inspect FlowManager stack and FightInitInfo/FighterData after activate-match."""
import struct
import subprocess
import sys

ADB = r".\work\platform-tools\adb.exe"
ELF = r".\work\unpacked\lib\arm64-v8a\libil2cpp.so"
SLOT_FLOW = 0x2BFFE18

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


A = u64(BASE + SLOT_FLOW)
CLS = u64(A) if A else None
print("flow class", hex(CLS) if CLS else None, cstr(u64(CLS + 0x10)) if CLS else None)
SF = u64(CLS + 0xB8) if CLS else None
FM = u64(SF) if SF else None
print("FlowManager", hex(FM) if FM else None, cname(FM) if FM else None)
if not FM:
    raise SystemExit("no FlowManager")
print("inProgress", hex(u64(FM + 0x20)) if u64(FM + 0x20) else None,
      cname(u64(FM + 0x20)) if u64(FM + 0x20) else None)
stack = u64(FM + 0x18)
print("flowStack", hex(stack) if stack else None, cname(stack) if stack else None)
if stack:
    arr = u64(stack + 0x10)
    size = u32(stack + 0x18)
    print(" stack size", size)
    for i in range(min(size or 0, 20)):
        fl = u64(arr + 0x20 + i * 8)
        print("  flow", i, hex(fl) if fl else None, cname(fl) if fl else None)
        if cname(fl) == "FightFlow":
            for off, lab in [(0x18, "_state"), (0x20, "_battleArbiter"), (0x28, "_fightInitInfo")]:
                v = u64(fl + off)
                print("    +%#x %s = %s class=%s" % (off, lab, hex(v) if v else None, cname(v) if v else None))
            info = u64(fl + 0x28)
            if info:
                for off, lab in [(0x10, "activeQuest"), (0x18, "questEnemy"), (0x20, "mapTile"),
                                 (0x28, "playerFighter"), (0x30, "enemyFighter"), (0x38, "tower"),
                                 (0x40, "sceneName"), (0x48, "timeOfDay")]:
                    v = u64(info + off)
                    print("      +%#x %s = %s class=%s" % (off, lab, hex(v) if v else None, cname(v) if v else None))
                for side, off in (("player", 0x28), ("enemy", 0x30)):
                    f = u64(info + off)
                    if not f:
                        continue
                    print(f"      {side} fighter:")
                    for fo, lab in [(0x10, "Id"), (0x18, "PlayerName"), (0x20, "PlayerTag"),
                                    (0x28, "IsBoss"), (0x30, "BaseAttributes"), (0x38, "Attributes"),
                                    (0x40, "Blueprint"), (0x48, "SigLevel"), (0x4C, "AttackBonus"),
                                    (0x50, "AIProfile"), (0x58, "AIPersonality"), (0x60, "TeamData")]:
                        if fo == 0x28:
                            print(f"        +{fo:#x} {lab} = {mem(f+fo,1).hex()}")
                        elif fo in (0x48, 0x4C):
                            print(f"        +{fo:#x} {lab} = {i32(f+fo)}")
                        else:
                            v = u64(f + fo)
                            extra = ""
                            if fo in (0x10, 0x18, 0x20):
                                extra = repr(ilstr(v))
                            if fo == 0x40 and v:
                                extra = cname(v)
                            print(f"        +{fo:#x} {lab} = {hex(v) if v else None} {extra}")
