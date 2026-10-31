import struct
import subprocess
import sys

ADB = "work/platform-tools/adb.exe"
ELF = "work/unpacked/lib/arm64-v8a/libil2cpp.so"
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


def i32(a):
    b = mem(a, 4)
    return struct.unpack("<i", b)[0] if len(b) == 4 else None


def cstr(a, n=80):
    b = mem(a, n)
    return b.split(b"\x00")[0].decode("latin1", "replace") if b else None


def cname(o):
    c = u64(o)
    return cstr(u64(c + 0x10)) if c else None


p = u64(BASE + 0x2BC7D18)
hub = u64(u64(u64(p) + 0xB8)) if p else None
lr = u64(hub + 0x128) if hub else None
st = u64(lr + 0x28) if lr else None
print("hub", hex(hub) if hub else None)
print("manager", hex(lr) if lr else None, cname(lr) if lr else None)
print("status", hex(st) if st else None, cname(st) if st else None)
if st:
    print("Level", i32(st + 0x10), "IsEnabled", mem(st + 0x14, 1).hex())
    types = u64(st + 0x18)
    print("types", hex(types) if types else None, "count", i32(types + 0x18) if types else None)
