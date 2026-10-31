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


p = u64(BASE + 0x2BC1C68)
print("slot ptr", hex(p) if p else None)
p2 = u64(p) if p else None
print("p2", hex(p2) if p2 else None)
t = u64(p2 + 0x18) if p2 else None
print("thread", hex(t) if t else None)
q = u64(t + 0xC0) if t else None
print("q", hex(q) if q else None)
q2 = u64(q) if q else None
print("q2", hex(q2) if q2 else None)
r = u64(q2 + 0xB8) if q2 else None
print("r", hex(r) if r else None)
inst = u64(r) if r else None
print("instance", hex(inst) if inst else None, cname(inst) if inst else None)
if inst:
    for off in (0x10, 0x18, 0x20, 0x28, 0x30, 0x38, 0x40, 0x48, 0x50, 0x58, 0x60):
        o = u64(inst + off)
        print(hex(off), hex(o) if o else None, cname(o) if o else None,
              "count18", i32(o + 0x18) if o else None,
              "count20", i32(o + 0x20) if o else None)
