"""Scan app heap mappings for live PlayerController objects and their attributes."""
import re
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADB = str(ROOT / "work" / "platform-tools" / "adb.exe")
ELF = ROOT / "work" / "unpacked" / "lib" / "arm64-v8a" / "libil2cpp.so"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def adb(args, timeout=120):
    return subprocess.run([ADB] + args, capture_output=True, timeout=timeout)


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
maps_text = adb(["shell", f"su 0 cat /proc/{PID}/maps"]).stdout.decode("latin1", "replace")
BASE = None
for line in maps_text.splitlines():
    if "libil2cpp.so" in line and "rw-p" in line and "02a97000" in line:
        BASE = int(line.split("-")[0], 16) - wv
        break


def u64(a):
    b = adb(["exec-out", "su", "0", "dd", f"if=/proc/{PID}/mem", "bs=1", "count=8",
             f"skip={a}", "status=none"]).stdout
    return struct.unpack("<Q", b)[0] if len(b) == 8 else None


def u32(a):
    b = adb(["exec-out", "su", "0", "dd", f"if=/proc/{PID}/mem", "bs=1", "count=4",
             f"skip={a}", "status=none"]).stdout
    return struct.unpack("<I", b)[0] if len(b) == 4 else None


def i32(a):
    b = adb(["exec-out", "su", "0", "dd", f"if=/proc/{PID}/mem", "bs=1", "count=4",
             f"skip={a}", "status=none"]).stdout
    return struct.unpack("<i", b)[0] if len(b) == 4 else None


def mem(a, n):
    return adb(["exec-out", "su", "0", "dd", f"if=/proc/{PID}/mem", "bs=1", f"count={n}",
                f"skip={a}", "status=none"]).stdout


def cstr(a, n=64):
    if not a:
        return None
    b = mem(a, n)
    return b.split(b"\x00")[0].decode("latin1", "replace") if b else None


def ilstr(a):
    if not a:
        return None
    n = u32(a + 0x10)
    if n is None or n > 100:
        return None
    b = mem(a + 0x14, n * 2)
    return b.decode("utf-16le", "replace") if b else None


def cname(o):
    if not o:
        return None
    c = u64(o)
    return cstr(u64(c + 0x10)) if c else None


pc_cls = u64(BASE + 47241784)
print("pid", PID, "PC class", hex(pc_cls) if pc_cls else None)
ranges = []
for line in maps_text.splitlines():
    m = re.match(r"([0-9a-f]+)-([0-9a-f]+)\s+rw-p\s+00000000\s+00:00\s+0\s*$", line.strip())
    if not m:
        continue
    a, b = int(m.group(1), 16), int(m.group(2), 16)
    if 0x787700000000 <= a < 0x787900000000 and 0 < b - a <= 64 * 1024 * 1024:
        ranges.append((a, b))
print("ranges", len(ranges), "MB", round(sum(b - a for a, b in ranges) / 1048576, 1))
needle = struct.pack("<Q", pc_cls)
CHUNK = 2 * 1024 * 1024
hits = []
for a, b in ranges:
    off = a
    while off < b:
        n = min(CHUNK, b - off)
        data = adb(["exec-out", "su", "0", "dd", f"if=/proc/{PID}/mem", "bs=4096",
                    f"skip={off//4096}", f"count={n//4096}", "status=none"], timeout=180).stdout
        start = 0
        while True:
            i = data.find(needle, start)
            if i < 0:
                break
            if i % 8 == 0:
                hits.append(off + i)
            start = i + 1
        off += n
print("hits", len(hits))
for h in hits:
    attrs = u64(h + 0x80)
    print("\nPC", hex(h), "Id", i32(h + 0xF4), "attrs", hex(attrs) if attrs else None,
          cname(attrs))
    if attrs:
        bp = u64(attrs + 0x48)
        tags = u64(bp + 0xB8) if bp else None
        print("  bp", hex(bp) if bp else None, cname(bp), "tags",
              hex(tags) if tags else None, "size", u32(tags + 0x18) if tags else None,
              "owner", hex(u64(attrs + 0x28) or 0))
