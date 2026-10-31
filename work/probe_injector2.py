import subprocess, struct, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ADB = r".\work\platform-tools\adb.exe"
PID = subprocess.run([ADB, "shell", "pidof com.kabam.bigrobot"], capture_output=True, text=True).stdout.strip()
elf = open(r".\work\unpacked\lib\arm64-v8a\libil2cpp.so", "rb").read()
e_phoff = struct.unpack_from("<Q", elf, 32)[0]; e_phentsize = struct.unpack_from("<H", elf, 54)[0]; e_phnum = struct.unpack_from("<H", elf, 56)[0]
wv = None
for i in range(e_phnum):
    o = e_phoff + i * e_phentsize; t, fl, fo, va, pa, fs, ms, al = struct.unpack_from("<IIQQQQQQ", elf, o)
    if t == 1 and (fl & 2): wv = va
maps = subprocess.run([ADB, "shell", f"su 0 cat /proc/{PID}/maps"], capture_output=True, text=True).stdout
BASE = None
for line in maps.splitlines():
    if "libil2cpp.so" in line and "rw-p" in line:
        BASE = int(line.split("-")[0], 16) - wv; break

def mem(a, n=8):
    p = subprocess.run([ADB, "shell", f"su 0 dd if=/proc/{PID}/mem bs=1 count={n} skip={a} 2>/dev/null | xxd -p"], capture_output=True, text=True)
    h = "".join(p.stdout.split())
    return bytes.fromhex(h) if h and re.fullmatch(r"[0-9a-fA-F]+", h) else b""
def u64(a):
    b = mem(a, 8); return struct.unpack("<Q", b)[0] if len(b) == 8 else None
def u32(a):
    b = mem(a, 4); return struct.unpack("<I", b)[0] if len(b) == 4 else None
def cstr(p, n=120):
    b = mem(p, n); return b.split(b"\x00")[0].decode("latin1", "replace") if b else None
def ilstr(p, n=200):
    if not p: return None
    ln = u32(p + 0x10)
    if ln is None or ln > n: return None
    b = mem(p + 0x14, ln * 2); return b.decode("utf-16-le", "replace") if b else None
def name_of(o):
    c = u64(o) if o else None
    np = u64(c + 0x10) if c else None
    return cstr(np) if np else "?"
def dump_ptr(label, p):
    print(f"{label}: {hex(p) if p else None}  name={name_of(p) if p else None}")
    if p:
        for off in range(0, 0x40, 8):
            v = u64(p + off)
            s = ilstr(v, 40) if v else None
            print(f"   +{off:#04x} = {hex(v) if v else None}" + (f"  ilstr={s!r}" if s else ""))

print("base", hex(BASE))
slot = BASE + 0x2C33650
print("slot raw")
for off in range(0, 0x40, 8):
    v = u64(slot + off)
    s = ilstr(v, 40) if v else None
    print(f"  slot+{off:#04x} = {hex(v) if v else None}" + (f" ilstr={s!r}" if s else ""))
p1 = u64(slot); print("p1", hex(p1) if p1 else None, name_of(p1) if p1 else None)
if p1:
    for off in range(0, 0x20, 8):
        v = u64(p1 + off)
        print(f"  p1+{off:#04x} = {hex(v) if v else None} name={name_of(v) if v else None}")
    sf = u64(p1 + 0xB8)
    print("sf", hex(sf) if sf else None)
    if sf:
        for off in range(0, 0x30, 8):
            v = u64(sf + off)
            print(f"  sf+{off:#04x} = {hex(v) if v else None} name={name_of(v) if v else None}")
