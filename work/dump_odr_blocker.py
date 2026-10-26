"""Dump FuseODRBlocker window/model live state (read-only)."""
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADB = str(ROOT / "work" / "platform-tools" / "adb.exe")
ELF = ROOT / "work" / "unpacked" / "lib" / "arm64-v8a" / "libil2cpp.so"
SLOT_WM = 0x2BE5B18
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def adb(args):
    return subprocess.run([ADB] + args, capture_output=True, timeout=120)


PID = adb(["shell", "pidof", "com.kabam.bigrobot"]).stdout.decode().strip()
if not PID:
    raise SystemExit("app not running")
elf = ELF.read_bytes()
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


def dump_list(label, ptr):
    print(f"  {label} {hex(ptr) if ptr else None} {cname(ptr) if ptr else None}")
    if not ptr:
        return
    n = i32(ptr + 0x18)
    arr = u64(ptr + 0x10)
    print(f"    count={n}")
    for i in range(min(n or 0, 30)):
        it = u64(arr + 0x20 + i * 8) if arr else None
        name = ilstr(u64(it + 0x10)) if it else None
        size = u64(it + 0x18) if it else None
        print(f"    [{i}] {hex(it) if it else None} name={name!r} size={size}")


A = u64(BASE + SLOT_WM)
CLS = u64(A) if A else None
SF = u64(CLS + 0xB8) if CLS else None
WM = u64(SF + 8) if SF else None
print("PID", PID, "WM", hex(WM) if WM else None)
if not WM:
    raise SystemExit("no WM")
stacks = u64(WM + 0x98)
cnt = u32(stacks + 0x20) if stacks else 0
entries = u64(stacks + 0x18) if stacks else None
for i in range(min(cnt or 0, 40)):
    e = entries + 0x20 + i * 24
    v = u64(e + 16)
    if not v:
        continue
    arr = u64(v + 0x10)
    size = u32(v + 0x18)
    for j in range(min(size or 0, 40)):
        info = u64(arr + 0x20 + j * 8)
        win = u64(info + 0x48) if info else None
        name = cname(win) if win else None
        if name == "FuseODRBlocker":
            print("\nFuseODRBlocker window", hex(win), "info", hex(info))
            for off, lab in [(0x88, "_presentation"), (0x90, "_presentationSCI"), (0x98, "_model")]:
                x = u64(win + off)
                print(f"  +{off:#x} {lab} {hex(x) if x else None} {cname(x) if x else None}")
            model = u64(win + 0x98)
            if model:
                for off, lab, typ in [
                    (0x30, "_batchedDownloadInfo", "dict"), (0x38, "_activeODRDownloads", "list"),
                    (0x40, "_requestedODRDownloads", "list"), (0x48, "_isListening", "bool"),
                    (0x50, "_lastPendingWads", "array"), (0x58, "_jobQueueProgress", "int"),
                    (0x5C, "_jobQueueSize", "int"), (0x60, "_lastOdrUpdateFrame", "int"),
                    (0x64, "_prevDownloadingODRProgress", "int"), (0x68, "_downloadTotalSize", "long"),
                    (0x70, "_downloadProgressBytes", "long"), (0x78, "_downloadStartTime", "float"),
                    (0x80, "_prevDownloadingODR", "obj"), (0x88, "_disableBlockingReasons", "set"),
                    (0x90, "_batchAllDownloads", "bool"),
                ]:
                    if typ == "dict":
                        print(f"  model +{off:#x} {lab} {hex(u64(model+off)) if u64(model+off) else None}")
                    elif typ == "list":
                        dump_list(lab, u64(model + off))
                    elif typ == "array":
                        arr2 = u64(model + off)
                        print(f"  model +{off:#x} {lab} {hex(arr2) if arr2 else None} count={i32(arr2+0x18) if arr2 else None}")
                    elif typ == "bool":
                        print(f"  model +{off:#x} {lab} {mem(model+off,1).hex()}")
                    elif typ == "int":
                        print(f"  model +{off:#x} {lab} {i32(model+off)}")
                    elif typ == "long":
                        print(f"  model +{off:#x} {lab} {u64(model+off)}")
                    elif typ == "float":
                        print(f"  model +{off:#x} {lab} {f32(model+off)}")
                    elif typ == "set":
                        print(f"  model +{off:#x} {lab} {hex(u64(model+off)) if u64(model+off) else None}")
                    elif typ == "obj":
                        x = u64(model + off)
                        print(f"  model +{off:#x} {lab} {hex(x) if x else None} {cname(x) if x else None}")
