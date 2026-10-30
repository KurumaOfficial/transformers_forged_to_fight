"""Resolve a static string/JSONPath slot to its UTF-8 key (read-only).

Usage: python work/read_slot_string.py 0x2c33420 [more slots...]
The slot address is a VA in libil2cpp.so. Handles direct Il2CppString
pointers and metadata-usage tokens (0xa0000000 | index<<1 | 1).
"""
import json
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADB = str(ROOT / "work" / "platform-tools" / "adb.exe")
ELF = str(ROOT / "work" / "unpacked" / "lib" / "arm64-v8a" / "libil2cpp.so")
META = str(ROOT / "work" / "unpacked" / "assets" / "bin" / "Data" / "Managed" /
           "Metadata" / "global-metadata.dat")
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

meta = open(META, "rb").read()
sl_off, sl_cnt, sl_data_off = struct.unpack_from("<iii", meta, 0x08)


def lit(index):
    if index < 0 or index >= sl_cnt // 8:
        return None
    ln, di = struct.unpack_from("<II", meta, sl_off + index * 8)
    return meta[sl_data_off + di:sl_data_off + di + ln].decode("utf-8", "replace")


def mem(a, n=8):
    return adb(["exec-out", "su", "0", "dd", f"if=/proc/{pid}/mem", "bs=1",
                f"count={n}", f"skip={a}", "status=none"]).stdout


def u64(a):
    b = mem(a, 8)
    return struct.unpack("<Q", b)[0] if len(b) == 8 else None


def u32(a):
    b = mem(a, 4)
    return struct.unpack("<I", b)[0] if len(b) == 4 else None


def ilstr(a, n=120):
    if not a or a < 0x1000:
        return None
    ln = u32(a + 0x10)
    if ln is None or ln > n:
        return None
    b = mem(a + 0x14, ln * 2)
    return b.decode("utf-16le", "replace") if b else None


def token_string(q):
    if q is None:
        return None
    if 0xA0000000 <= q <= 0xBFFFFFFF:
        return lit((q & 0x1FFFFFFF) >> 1)
    return None


def resolve(slot):
    p = u64(slot)
    if not p:
        return {"slot": hex(slot), "value": None}
    out = {"slot": hex(slot), "ptr": hex(p)}
    # direct Il2CppString
    s = ilstr(p)
    if s:
        out["string"] = s
        return out
    # metadata-usage table: first qword is a token
    q = u64(p)
    s = token_string(q)
    if s:
        out["token"] = hex(q) if q else None
        out["string"] = s
        return out
    # JSONPath-like object: scan a few qwords for a string pointer/token
    for off in range(0, 0x40, 8):
        q = u64(p + off)
        s = ilstr(q) or token_string(q)
        if s:
            out["field"] = hex(off)
            out["string"] = s
            return out
    return out


for arg in sys.argv[1:]:
    va = int(arg, 16)
    print(json.dumps(resolve(BASE + va), ensure_ascii=False))
