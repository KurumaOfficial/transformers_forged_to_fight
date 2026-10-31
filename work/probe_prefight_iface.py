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
def cstr(p, n=200):
    b = mem(p, n); return b.split(b"\x00")[0].decode("latin1", "replace") if b else None
def ilstr(p, n=200):
    if not p: return None
    b = mem(p + 0x10, 4)
    if len(b) < 4: return None
    ln = struct.unpack("<I", b)[0]
    if ln > n: return None
    b = mem(p + 0x14, ln * 2); return b.decode("utf-16-le", "replace") if b else None
def klass_name(k):
    if not k: return None
    np = u64(k + 0x10)
    return cstr(np) if np else None
def list_items(l, limit=10):
    if not l: return []
    cnt = u32(l + 0x18); arr = u64(l + 0x10)
    if not cnt or not arr or cnt > limit: return []
    raw = mem(arr + 0x20, cnt * 8)
    return [struct.unpack_from("<Q", raw, i*8)[0] for i in range(cnt) if len(raw) >= (i+1)*8]

# interface class from TypeInfo slot
iface_slot = BASE + 0x2D0C2C0
iface_cls = u64(iface_slot)
print("iface class", hex(iface_cls) if iface_cls else None, "name", klass_name(iface_cls))
# also resolve through one deref if needed
if iface_cls:
    print("iface class+0", hex(u64(iface_cls)) if u64(iface_cls) else None)

slot = BASE + 0x2C33650
p1 = u64(slot); cls = u64(p1); sf = u64(cls + 0xB8)
g = u64(sf + 0x0); cnt = u32(g + 0x20); ent = u64(g + 0x18)
print("tag", repr(ilstr(u64(sf + 8))), "interfaces", cnt)
raw = mem(ent, cnt * 24)
found = []
for i in range(cnt):
    e = raw[i*24:(i+1)*24]
    h, k, v = struct.unpack_from("<I", e, 0)[0], struct.unpack_from("<Q", e, 8)[0], struct.unpack_from("<Q", e, 16)[0]
    # scan key object's first 0x40 bytes for class pointer
    kr = mem(k, 0x40) if k else b""
    vals = [struct.unpack_from("<Q", kr, off)[0] for off in range(0, len(kr)-7, 8)] if kr else []
    if iface_cls and (iface_cls in vals or k == iface_cls):
        found.append((i, k, v, vals))
        print("MATCH key entry", i, hex(k), "vals", [hex(x) for x in vals], "value", hex(v))
print("found", len(found))
for i, k, v, vals in found:
    print("list", hex(v) if v else None)
    for tup in list_items(v):
        tag = ilstr(u64(tup + 0x10), 40)
        impl = u64(tup + 0x18)
        print("   tag", repr(tag), "impl", hex(impl) if impl else None)
