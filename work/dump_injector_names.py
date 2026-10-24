"""Resolve InterfaceInjector interface/tag/implementation names.

RuntimeType +0x10 points to a Mono/Il2Cpp type descriptor; for class types
u64(descriptor) points at an Il2CppTypeDefinition whose first int is the
nameIndex into global-metadata's string table.
"""
import json
import re
import struct
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ADB = r"C:\Users\gameg\Desktop\TFTF\work\platform-tools\adb.exe"
ROOT = r"C:\Users\gameg\Desktop\TFTF"
PID = subprocess.run([ADB, "shell", "pidof com.kabam.bigrobot"], capture_output=True, text=True).stdout.strip()
if not PID:
    raise SystemExit("app not running")
maps = subprocess.run([ADB, "shell", f"su 0 cat /proc/{PID}/maps"], capture_output=True, text=True).stdout
rw = [int(l.split("-")[0], 16) for l in maps.splitlines() if "libil2cpp.so" in l and "rw-p" in l and "2a97000" in l][0]
BASE = rw - 0x2AA7000
META = open(ROOT + r"\work\unpacked\assets\bin\Data\Managed\Metadata\global-metadata.dat", "rb").read()
STR_OFF = struct.unpack_from("<I", META, 0x18)[0]
STR_SIZE = struct.unpack_from("<I", META, 0x1C)[0]


def mem(a, n=8):
    p = subprocess.run([ADB, "shell", f"su 0 dd if=/proc/{PID}/mem bs=1 count={n} skip={a} 2>/dev/null | xxd -p"], capture_output=True, text=True)
    h = "".join(p.stdout.split())
    return bytes.fromhex(h) if h and re.fullmatch(r"[0-9a-fA-F]+", h) else b""


def u64(a):
    b = mem(a, 8); return struct.unpack("<Q", b)[0] if len(b) == 8 else None


def u32(a):
    b = mem(a, 4); return struct.unpack("<I", b)[0] if len(b) == 4 else None


def meta_str(idx):
    off = STR_OFF + idx
    if off < STR_OFF or off >= STR_OFF + STR_SIZE:
        return None
    end = META.find(b"\x00", off)
    if end < 0:
        return None
    return META[off:end].decode("utf-8", "replace")


def type_def_name(t):
    """RuntimeType -> (namespace, name) or None."""
    if not t:
        return None
    desc = u64(t + 0x10)
    if not desc:
        return None
    td = u64(desc)
    if not td:
        return None
    name_idx = u32(td)
    ns_idx = u32(td + 4)
    if name_idx is None:
        return None
    name = meta_str(name_idx)
    ns = meta_str(ns_idx) if ns_idx is not None else None
    if not name:
        return None
    return (ns, name)


def ilstr(p, n=100):
    if not p: return None
    b = mem(p + 0x10, 4)
    if len(b) < 4: return None
    ln = struct.unpack("<I", b)[0]
    if ln > n: return None
    b = mem(p + 0x14, ln * 2); return b.decode("utf-16-le", "replace") if b else None


def list_items(l):
    if not l: return []
    cnt = u32(l + 0x18); arr = u64(l + 0x10)
    if not cnt or not arr or cnt > 10: return []
    raw = mem(arr + 0x20, cnt * 8)
    return [struct.unpack_from("<Q", raw, i * 8)[0] for i in range(cnt) if len(raw) >= (i + 1) * 8]


slot = BASE + 0x2C33650
cls = u64(u64(slot)); sf = u64(cls + 0xB8)
g = u64(sf); cnt = u32(g + 0x20); ent = u64(g + 0x18)
print("tag", repr(ilstr(u64(sf + 8))), "interfaces", cnt)
raw = mem(ent + 0x20, cnt * 24)
out = []
for i in range(cnt):
    e = raw[i * 24:(i + 1) * 24]
    if len(e) < 24: break
    h, k, v = struct.unpack_from("<I", e, 0)[0], struct.unpack_from("<Q", e, 8)[0], struct.unpack_from("<Q", e, 16)[0]
    iname = type_def_name(k)
    rows = []
    for tup in list_items(v):
        tag = ilstr(u64(tup + 0x10), 40)
        impl = u64(tup + 0x18)
        rows.append((tag, type_def_name(impl)))
    out.append({"index": i, "interface": iname, "implementations": rows})
    print(f"{i:3d} {iname} -> {rows}")

with open(ROOT + r"\work\injector_registry.json", "w", encoding="utf-8") as fh:
    json.dump({"tag": ilstr(u64(sf + 8)), "interfaces": out}, fh, ensure_ascii=False, indent=1)
print("wrote work/injector_registry.json")
