"""Dump WindowManager windowStacks and PreFightScreen fields via known class accessor.

The accessor slot 0x2BE5B18 is read from WindowManager.get_Instance (0x1586354):
  slot -> Il2CppClass** -> Il2CppClass*; static_fields = class+0xB8; Instance = static+8.
Read-only, no Frida.
"""
import struct
import subprocess
import sys

ADB = r"C:\Users\gameg\Desktop\TFTF\work\platform-tools\adb.exe"
ELF = r"C:\Users\gameg\Desktop\TFTF\work\unpacked\lib\arm64-v8a\libil2cpp.so"
SLOT_WM = 0x2BE5B18

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
    p = adb(["exec-out", "su", "0", "dd", f"if=/proc/{PID}/mem", "bs=1", f"count={n}",
             f"skip={a}", "status=none"])
    return p.stdout


def u64(a):
    b = mem(a, 8)
    return struct.unpack("<Q", b)[0] if len(b) == 8 else None


def u32(a):
    b = mem(a, 4)
    return struct.unpack("<I", b)[0] if len(b) == 4 else None


def cstr(a, n=80):
    if not a:
        return None
    b = mem(a, n)
    return b.split(b"\x00")[0].decode("latin1", "replace") if b else None


def class_name(obj):
    if not obj:
        return None
    cls = u64(obj)
    return cstr(u64(cls + 0x10)) if cls else None


A = u64(BASE + SLOT_WM)
CLS = u64(A) if A else None
print("wm class", hex(CLS) if CLS else None, "name", cstr(u64(CLS + 0x10)) if CLS else None)
STATIC = u64(CLS + 0xB8) if CLS else None
WM = u64(STATIC + 8) if STATIC else None
print("static", hex(STATIC) if STATIC else None, "instance", hex(WM) if WM else None,
      "class", class_name(WM) if WM else None)
if not WM:
    raise SystemExit("no instance")

STACKS = u64(WM + 0x98)
print("windowStacks", hex(STACKS) if STACKS else None, class_name(STACKS) if STACKS else None)

cnt = u32(STACKS + 0x20)
entries = u64(STACKS + 0x18)
print("stacks count", cnt, "entries", hex(entries) if entries else None)
infos = []
for i in range(min(cnt or 0, 50)):
    e = entries + 0x20 + i * 24
    k = u64(e + 8)
    v = u64(e + 16)
    if not k:
        continue
    print("layer", hex(k), class_name(k), "-> stack", hex(v) if v else None, class_name(v) if v else None)
    if not v:
        continue
    arr = u64(v + 0x10)
    size = u32(v + 0x18)
    print("  stack size", size, "array", hex(arr) if arr else None)
    for j in range(min(size or 0, 50)):
        info = u64(arr + 0x20 + j * 8)
        if not info:
            continue
        name = cstr(u64(info + 0x10)) if u64(info + 0x10) else None
        win = u64(info + 0x48)
        print(f"   info[{j}] {hex(info)} name={name!r} window={hex(win) if win else None} "
              f"window_class={class_name(win) if win else None}")
        infos.append((info, name, win))

for info, name, win in infos:
    if class_name(win) != "PreFightScreen":
        continue
    print("\n=== PreFightScreen", hex(win), "info", hex(info), "===")
    fields = {}
    for off, lab in [(0x88, "_config"), (0x90, "_presentationSCI"), (0x98, "_model"),
                     (0xA0, "_presentation"), (0xA8, "_resourcesReleased"), (0xA9, "_onFightClicked"),
                     (0x20, "windowManager"), (0x30, "windowInfo")]:
        if off in (0xA8, 0xA9):
            print(f"  +{off:#x} {lab} = {mem(win + off, 1).hex()}")
            continue
        val = u64(win + off)
        fields[lab] = val
        print(f"  +{off:#x} {lab} = {hex(val) if val else None} class={class_name(val) if val else None}")
    model = fields.get("_model")
    if model:
        print("\n  model fields:")
        for off, lab in [(0x10, "onPlayerHeroUpdated"), (0x18, "idealContenderMap"),
                         (0x28, "_config"), (0x30, "_currentTeam"), (0x38, "_enemy"),
                         (0x40, "_tower"), (0x48, "_controller"), (0x50, "_activeQuest"),
                         (0x58, "_onError"), (0x60, "_onHeal"), (0x68, "_teamDeadWindow"),
                         (0x70, "_baseEnemyPI"), (0x74, "_buffContribution"),
                         (0x78, "_towerContribution"), (0x7C, "_timeRemaining"),
                         (0x80, "_hiddenInfo")]:
            if off in (0x70, 0x74, 0x78, 0x7C):
                print(f"    +{off:#x} {lab} = {u32(model + off)}")
            else:
                val = u64(model + off)
                print(f"    +{off:#x} {lab} = {hex(val) if val else None} class={class_name(val) if val else None}")
        team = u64(model + 0x30)
        if team:
            print("\n  current team:")
            print("    class", class_name(team))
            for off, lab in [(0x10, "heroes"), (0x18, "name"), (0x20, "size"), (0x28, "hp")]:
                val = u64(team + off)
                print(f"    +{off:#x} {lab} = {hex(val) if val else None} class={class_name(val) if val else None}")
    cfg = fields.get("_config")
    if cfg:
        print("\n  config fields:")
        for off, lab in [(0x10, "enemy"), (0x18, "tower"), (0x20, "qid"), (0x28, "mapTile"),
                         (0x30, "ModeSpecificData"), (0x38, "questboardCharacter")]:
            val = u64(cfg + off)
            print(f"    +{off:#x} {lab} = {hex(val) if val else None} class={class_name(val) if val else None}")
