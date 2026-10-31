import subprocess, struct, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ADB = r".\work\platform-tools\adb.exe"
PID = subprocess.run([ADB, "shell", "pidof com.kabam.bigrobot"], capture_output=True, text=True).stdout.strip()
if not PID:
    raise SystemExit("app not running")
elf = open(r".\work\unpacked\lib\arm64-v8a\libil2cpp.so", "rb").read()
e_phoff = struct.unpack_from("<Q", elf, 32)[0]
e_phentsize = struct.unpack_from("<H", elf, 54)[0]
e_phnum = struct.unpack_from("<H", elf, 56)[0]
wv = None
for i in range(e_phnum):
    o = e_phoff + i * e_phentsize
    t, fl, fo, va, pa, fs, ms, al = struct.unpack_from("<IIQQQQQQ", elf, o)
    if t == 1 and (fl & 2):
        wv = va
maps = subprocess.run([ADB, "shell", f"su 0 cat /proc/{PID}/maps"], capture_output=True, text=True).stdout
BASE = None
for line in maps.splitlines():
    if "libil2cpp.so" in line and "rw-p" in line:
        BASE = int(line.split("-")[0], 16) - wv
        break
if BASE is None:
    raise SystemExit("no libil2cpp map")

def mem(a, n=8):
    p = subprocess.run([ADB, "shell", f"su 0 dd if=/proc/{PID}/mem bs=1 count={n} skip={a} 2>/dev/null | xxd -p"], capture_output=True, text=True)
    h = "".join(p.stdout.split())
    return bytes.fromhex(h) if h and re.fullmatch(r"[0-9a-fA-F]+", h) else b""

def u64(a):
    b = mem(a, 8)
    return struct.unpack("<Q", b)[0] if len(b) == 8 else None

def u32(a):
    b = mem(a, 4)
    return struct.unpack("<I", b)[0] if len(b) == 4 else None

def cstr(p, n=160):
    b = mem(p, n)
    return b.split(b"\x00")[0].decode("latin1", "replace") if b else None

def ilstr(p, n=200):
    if not p:
        return None
    ln = u32(p + 0x10)
    if ln is None or ln > n:
        return None
    b = mem(p + 0x14, ln * 2)
    return b.decode("utf-16-le", "replace") if b else None

def name_of(o):
    c = u64(o) if o else None
    np = u64(c + 0x10) if c else None
    return cstr(np) if np else "?"

def dict_items(d, limit=200):
    if not d:
        return []
    cnt = u32(d + 0x20); ent = u64(d + 0x18)
    out = []
    if not ent:
        return out
    for i in range(min(cnt or 0, limit)):
        e = ent + 0x20 + i * 24
        out.append((u64(e + 8), u64(e + 16)))
    return out

print("pid", PID, "base", hex(BASE))
slot = BASE + 0x2C33650
cls = u64(slot)
print("Injector class", hex(cls) if cls else None)
sf = u64(cls + 0xB8) if cls else None
print("static_fields", hex(sf) if sf else None)
if not sf:
    raise SystemExit("no static fields")
print("_currentTag", repr(ilstr(u64(sf + 8))))
print("_hasBeenInitialized", mem(sf + 0x10, 1).hex())
g = u64(sf + 0)
p = u64(sf + 0x18)
print("_gameInterfaces", hex(g) if g else None, "count", u32(g + 0x20) if g else None)
print("_persistentInterfaces", hex(p) if p else None, "count", u32(p + 0x20) if p else None)

print("\n-- game interface keys --")
for k, v in dict_items(g, 400):
    print(" ", name_of(k), "->", hex(v) if v else None, name_of(v) if v else None,
          "listcount", u32(v + 0x18) if v else None)

print("\n-- persistent interfaces --")
for k, v in dict_items(p, 200):
    print(" ", name_of(k), "->", hex(v) if v else None, name_of(v) if v else None)
