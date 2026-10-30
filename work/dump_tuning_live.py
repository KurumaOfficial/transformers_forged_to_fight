"""Dump live Tuning fields and flag zero/empty values (read-only)."""
import re
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADB = str(ROOT / "work" / "platform-tools" / "adb.exe")
ELF = str(ROOT / "work" / "unpacked" / "lib" / "arm64-v8a" / "libil2cpp.so")
DUMP = ROOT / "work" / "il2cpp_dump" / "dump.cs"
OUT = ROOT / "spec" / "tuning_live.md"
SLOT = 0x2BC9268
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


def mem(a, n=8):
    return adb(["exec-out", "su", "0", "dd", f"if=/proc/{pid}/mem", "bs=1",
                f"count={n}", f"skip={a}", "status=none"]).stdout


def u64(a):
    b = mem(a, 8)
    return struct.unpack("<Q", b)[0] if len(b) == 8 else None


def read_num(a, typ):
    if typ == "bool":
        b = mem(a, 1)
        return bool(b[0]) if b else None
    if typ in ("int", "uint"):
        b = mem(a, 4)
        return struct.unpack("<i", b)[0] if len(b) == 4 else None
    if typ == "float":
        b = mem(a, 4)
        return struct.unpack("<f", b)[0] if len(b) == 4 else None
    if typ == "long":
        b = mem(a, 8)
        return struct.unpack("<q", b)[0] if len(b) == 8 else None
    if typ == "string":
        p = u64(a)
        if not p:
            return ""
        n = struct.unpack("<I", mem(p + 0x10, 4))[0]
        if n > 200:
            return ""
        return mem(p + 0x14, n * 2).decode("utf-16le", "replace")
    return None


txt = DUMP.read_text(encoding="utf-8", errors="replace")
start = txt.index("public class Tuning :")
end = txt.index("// Properties", start)
fields = []
for line in txt[start:end].splitlines():
    m = re.match(r"\s*public\s+([\w\.\<\>\[\]]+)\s+(\w+);\s*//\s*0x([0-9A-Fa-f]+)", line)
    if m:
        fields.append((m.group(2), m.group(1), int(m.group(3), 16)))

p = u64(BASE + SLOT)
cls = u64(p) if p else None
sf = u64(cls + 0xB8) if cls else None
inst = u64(sf) if sf else None
print("pid", pid, "instance", hex(inst) if inst else None, "fields", len(fields))
if not inst:
    raise SystemExit("no Tuning instance")

rows = []
for name, typ, off in fields:
    simple = typ in ("bool", "int", "uint", "float", "long", "string")
    val = read_num(inst + off, typ) if simple else None
    zero = (val == 0 or val == 0.0 or val is False or val == "" or val is None)
    rows.append((name, typ, off, val, zero, simple))

lines = [
    "# Live Tuning values (Step 1.2)",
    "",
    f"Source: `Tuning.Instance` live memory, pid {pid}. Read-only.",
    "Zero/empty fields are marked; custom structs/arrays show `n/a` and need",
    "a separate decoder. Do not fill a field blindly just because it is zero.",
    "",
    "| field | type | offset | live value | zero/empty |",
    "|---|---|---:|---|---|",
]
for name, typ, off, val, zero, simple in rows:
    shown = "n/a" if not simple else repr(val)
    lines.append(f"| `{name}` | `{typ}` | 0x{off:X} | {shown} | {'**yes**' if zero else ''} |")

zero_rows = [r for r in rows if r[4]]
lines += ["", f"Zero/empty fields: **{len(zero_rows)} / {len(rows)}**.", ""]
for name, typ, off, val, zero, simple in zero_rows:
    lines.append(f"- `{name}` (`{typ}`, 0x{off:X})")
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote", OUT, "zero", len(zero_rows), "of", len(rows))
