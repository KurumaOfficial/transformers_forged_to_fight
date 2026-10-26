"""Scan app heap mappings for live PlayerAttributes objects (read-only)."""
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
if BASE is None:
    raise SystemExit("no base")


def u64(a):
    b = adb(["exec-out", "su", "0", "dd", f"if=/proc/{PID}/mem", "bs=1", "count=8",
             f"skip={a}", "status=none"]).stdout
    return struct.unpack("<Q", b)[0] if len(b) == 8 else None


def u32(a):
    b = adb(["exec-out", "su", "0", "dd", f"if=/proc/{PID}/mem", "bs=1", "count=4",
             f"skip={a}", "status=none"]).stdout
    return struct.unpack("<I", b)[0] if len(b) == 4 else None


def cstr(a, n=64):
    if not a:
        return None
    b = adb(["exec-out", "su", "0", "dd", f"if=/proc/{PID}/mem", "bs=1", f"count={n}",
             f"skip={a}", "status=none"]).stdout
    return b.split(b"\x00")[0].decode("latin1", "replace") if b else None


def cname(o):
    if not o:
        return None
    c = u64(o)
    return cstr(u64(c + 0x10)) if c else None


def ilstr(a):
    if not a:
        return None
    n = u32(a + 0x10)
    if n is None or n > 100:
        return None
    b = adb(["exec-out", "su", "0", "dd", f"if=/proc/{PID}/mem", "bs=1", f"count={n*2}",
             f"skip={a+0x14}", "status=none"]).stdout
    return b.decode("utf-16le", "replace") if b else None


# class pointers from script.json slots
PA_SLOT = 47241760
PC_SLOT = 47241784
pa_cls = u64(BASE + PA_SLOT)
pc_cls = u64(BASE + PC_SLOT)
print("pid", PID, "base", hex(BASE), "PA", hex(pa_cls) if pa_cls else None,
      "PC", hex(pc_cls) if pc_cls else None,
      "name", cname_from := (cstr(u64(pa_cls + 0x10)) if pa_cls else None))

# candidate mappings: unnamed rw, 0x7877a0000000..0x787800000000, <=32MB
ranges = []
for line in maps_text.splitlines():
    m = re.match(r"([0-9a-f]+)-([0-9a-f]+)\s+rw-p\s+00000000\s+00:00\s+0\s*$", line.strip())
    if not m:
        continue
    a, b = int(m.group(1), 16), int(m.group(2), 16)
    if 0x7877A0000000 <= a < 0x787800000000 and 0 < b - a <= 32 * 1024 * 1024:
        ranges.append((a, b))
print("ranges", len(ranges), "MB", round(sum(b - a for a, b in ranges) / 1048576, 1))

needle = struct.pack("<Q", pa_cls)
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
    print("\nobject", hex(h), "owner", hex(u64(h + 0x28) or 0), cname(u64(h + 0x28)),
          "tags_set", hex(u64(h + 0x40) or 0), "bp", hex(u64(h + 0x48) or 0),
          cname(u64(h + 0x48)))
    bp = u64(h + 0x48)
    if bp:
        tags = u64(bp + 0xB8)
        print("  bp tags", hex(tags) if tags else None, "size", u32(tags + 0x18) if tags else None,
              "model", ilstr(u64(bp + 0x40)), "character", ilstr(u64(bp + 0x28)))
    for off, lab in [(0x50, "baseAttrs"), (0x58, "attrs"), (0x68, "health"), (0x70, "mana"),
                     (0x78, "attack")]:
        v = u64(h + off)
        print(f"  +{off:#x} {lab}", hex(v) if v else None, cname(v) if v else None)
