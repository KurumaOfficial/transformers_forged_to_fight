"""Find WindowManager via its class-name pointer, dump windowStacks, then PreFightScreen fields.

Read-only. No Frida. Uses /proc/pid/mem through su.
"""
import json
import re
import struct
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(r".")
ADB = str(ROOT / "work" / "platform-tools" / "adb.exe")
META_FILE = ROOT / "work" / "unpacked" / "assets" / "bin" / "Data" / "Managed" / "Metadata" / "global-metadata.dat"

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def sh(args, timeout=180):
    return subprocess.run([ADB] + args, capture_output=True, timeout=timeout)


def shell(cmd, timeout=180):
    p = sh(["shell", cmd], timeout=timeout)
    return (p.stdout or b"").decode("latin1", "replace")


def pid():
    return shell("pidof com.kabam.bigrobot").strip()


PID = pid()
if not PID:
    raise SystemExit("app not running")

maps_text = shell(f"su 0 cat /proc/{PID}/maps")
regions = []
meta_map = None
for line in maps_text.splitlines():
    m = re.match(r"([0-9a-f]+)-([0-9a-f]+)\s+(\S+)\s+\S+\s+\S+\s+\S+\s*(.*)", line)
    if not m:
        continue
    s, e, perm, name = int(m.group(1), 16), int(m.group(2), 16), m.group(3), m.group(4).strip()
    regions.append((s, e, perm, name))
    if "global-metadata.dat" in name:
        meta_map = (s, e)

if not meta_map:
    raise SystemExit("global-metadata mapping not found")
print("pid", PID, "metadata", hex(meta_map[0]), hex(meta_map[1]))

META = META_FILE.read_bytes()
STR_OFF = struct.unpack_from("<I", META, 0x18)[0]
STR_SIZE = struct.unpack_from("<I", META, 0x1C)[0]


def meta_offsets(name):
    out = []
    needle = name.encode() + b"\x00"
    st = STR_OFF
    while True:
        i = META.find(needle, st, STR_OFF + STR_SIZE)
        if i < 0:
            break
        out.append(i - STR_OFF)
        st = i + 1
    return out


def mem(addr, size):
    p = sh(["exec-out", "su", "0", "dd", f"if=/proc/{PID}/mem", "bs=1", f"count={size}", f"skip={addr}", "status=none"], timeout=60)
    return p.stdout or b""


def u64(a):
    b = mem(a, 8)
    return struct.unpack("<Q", b)[0] if len(b) == 8 else None


def u32(a):
    b = mem(a, 4)
    return struct.unpack("<I", b)[0] if len(b) == 4 else None


def cstr(a, n=96):
    if not a:
        return None
    b = mem(a, n)
    return b.split(b"\x00")[0].decode("latin1", "replace") if b else None


def bulk(addr, size):
    """Read [addr, addr+size) using 1 MiB aligned dd reads."""
    out = bytearray()
    block = 1 << 24
    first = addr // block
    last = (addr + size - 1) // block
    for blk in range(first, last + 1):
        p = sh(["exec-out", "su", "0", "dd", f"if=/proc/{PID}/mem", f"bs={block}",
                f"skip={blk}", "count=1", "status=none"], timeout=180)
        out += p.stdout or b""
    start = first * block
    return bytes(out), start


targets = {}
for off in meta_offsets("WindowManager"):
    p = meta_map[0] + STR_OFF + off
    if cstr(p, 20) == "WindowManager":
        targets[p] = off
print("windowmanager name ptrs", [hex(x) for x in targets])

# Native heap range only; skip dalvik/stack/metadata.
cands = []
t0 = time.time()
for s, e, perm, name in regions:
    if "rw" not in perm or e - s < 8:
        continue
    if not (0x770000000000 <= s < 0x780000000000):
        continue
    if "stack_and_tls" in name or "dalvik" in name:
        continue
    size = e - s
    if size > 512 * 1024 * 1024:
        continue
    try:
        blob, base = bulk(s, size)
    except Exception as exc:
        print("skip", hex(s), exc)
        continue
    if not blob:
        continue
    for tp in targets:
        pat = struct.pack("<Q", tp)
        pos = 0
        while True:
            i = blob.find(pat, pos)
            if i < 0:
                break
            hit = base + i
            if s <= hit < e:
                cands.append((hit, tp))
            pos = i + 1
print("scan done", len(cands), "candidates in", round(time.time() - t0, 1), "s")

wm_class = None
for hit, tp in cands:
    cls = hit - 0x10
    namep = u64(cls + 0x10)
    if namep == tp and cstr(namep, 20) == "WindowManager":
        ns = u64(cls + 0x18)
        image = u64(cls)
        print("WindowManager class", hex(cls), "image", hex(image) if image else None,
              "namespace", repr(cstr(ns)) if ns else None)
        wm_class = cls
        break

if not wm_class:
    raise SystemExit("WindowManager class not found")

static = u64(wm_class + 0xB8)
print("static fields", hex(static) if static else None)
if not static:
    raise SystemExit("no static fields")
inst = u64(static + 0x8)
print("WindowManager.Instance", hex(inst) if inst else None, "class", cstr(u64(inst)) if inst else None)
if not inst:
    raise SystemExit("no WindowManager instance")

stacks = u64(inst + 0x98)
print("windowStacks", hex(stacks) if stacks else None, "class", cstr(u64(stacks)) if stacks else None)


def dump_dict(d, label):
    cnt = u32(d + 0x20)
    ent = u64(d + 0x18)
    print(f"{label}: count={cnt} entries={hex(ent) if ent else None}")
    if not ent:
        return []
    items = []
    for i in range(min(cnt or 0, 50)):
        e = ent + 0x20 + i * 24
        k = u64(e + 8)
        v = u64(e + 16)
        if k is None:
            continue
        items.append((k, v))
        print(f"  key={hex(k)} value={hex(v) if v else None} value_class={cstr(u64(v)) if v else None}")
    return items


def stack_items(st):
    arr = u64(st + 0x10)
    size = u32(st + 0x18)
    print("stack", hex(st), "size", size, "array", hex(arr) if arr else None)
    out = []
    if not arr or not size:
        return out
    for i in range(min(size, 50)):
        item = u64(arr + 0x20 + i * 8)
        if item:
            out.append(item)
            print("   info", i, hex(item), "name", repr(cstr(u64(item + 0x10))) if u64(item + 0x10) else None,
                  "window", hex(u64(item + 0x48)) if u64(item + 0x48) else None,
                  "window_class", cstr(u64(u64(item + 0x48))) if u64(item + 0x48) else None)
    return out


windows = []
if stacks:
    for k, v in dump_dict(stacks, "stacks"):
        if v:
            windows += stack_items(v)

for info in windows:
    w = u64(info + 0x48)
    if not w:
        continue
    wcls = u64(w)
    wn = cstr(u64(wcls + 0x10)) if wcls else None
    if wn == "PreFightScreen":
        print("\n=== PreFightScreen", hex(w), "===")
        for off, lab in [(0x88, "_config"), (0x90, "_presentationSCI"), (0x98, "_model"),
                         (0xA0, "_presentation"), (0x20, "windowManager"), (0x30, "windowInfo")]:
            val = u64(w + off)
            vcls = cstr(u64(val)) if val else None
            print(f"  +{off:#x} {lab} = {hex(val) if val else None} class={vcls}")
        model = u64(w + 0x98)
        if model:
            print("  model fields:")
            for off, lab in [(0x28, "_config"), (0x30, "_currentTeam"), (0x38, "_enemy"),
                             (0x40, "_tower"), (0x48, "_controller"), (0x50, "_activeQuest"),
                             (0x70, "baseEnemyPI"), (0x7C, "_timeRemaining")]:
                val = u64(model + off)
                if off in (0x70, 0x7C):
                    print(f"    +{off:#x} {lab} = {u32(model + off)}")
                else:
                    print(f"    +{off:#x} {lab} = {hex(val) if val else None} class={cstr(u64(val)) if val else None}")
        cfg = u64(w + 0x88)
        if cfg:
            print("  config fields:")
            for off, lab in [(0x10, "enemy"), (0x18, "tower"), (0x20, "qid"), (0x28, "mapTile"),
                             (0x30, "ModeSpecificData"), (0x38, "questboardCharacter")]:
                val = u64(cfg + off)
                print(f"    +{off:#x} {lab} = {hex(val) if val else None} class={cstr(u64(val)) if val else None}")
        pres = u64(w + 0xA0)
        if pres:
            print("  presentation", hex(pres), "class", cstr(u64(pres)))
        break
else:
    print("PreFightScreen not in window stacks")

