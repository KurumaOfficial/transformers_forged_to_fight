import subprocess, struct, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ADB = r"C:\Users\gameg\Desktop\TFTF\work\platform-tools\adb.exe"
PID = subprocess.run([ADB, "shell", "pidof com.kabam.bigrobot"], capture_output=True, text=True).stdout.strip()
maps = subprocess.run([ADB, "shell", f"su 0 cat /proc/{PID}/maps"], capture_output=True, text=True).stdout
rw = [int(l.split("-")[0], 16) for l in maps.splitlines() if "libil2cpp.so" in l and "rw-p" in l and "2a97000" in l][0]
BASE = rw - 0x2AA7000

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
def ilstr(p, n=100):
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
def runtime_type_name(t):
    if not t: return None
    # RuntimeType +0x18 -> MonoTypeInfo, +0x10 -> full_name
    info = u64(t + 0x18)
    if info:
        full = ilstr(u64(info + 0x10), 120)
        if full: return full
    # maybe +0x10 is a name string directly in some runtime versions
    return None
def list_items(l, limit=10):
    if not l: return []
    cnt = u32(l + 0x18); arr = u64(l + 0x10)
    if not cnt or not arr or cnt > limit: return []
    raw = mem(arr + 0x20, cnt * 8)
    return [struct.unpack_from("<Q", raw, i*8)[0] for i in range(cnt) if len(raw) >= (i+1)*8]

slot = BASE + 0x2C33650
p1 = u64(slot); cls = u64(p1); sf = u64(cls + 0xB8)
g = u64(sf + 0); cnt = u32(g + 0x20); ent = u64(g + 0x18)
print("interfaces", cnt, "tag", repr(ilstr(u64(sf + 8))))
raw = mem(ent, cnt * 24)
for i in range(cnt):
    e = raw[i*24:(i+1)*24]
    if len(e) < 24: break
    h, k, v = struct.unpack_from("<I", e, 0)[0], struct.unpack_from("<Q", e, 8)[0], struct.unpack_from("<Q", e, 16)[0]
    iname = runtime_type_name(k)
    rows = []
    for tup in list_items(v):
        tag = ilstr(u64(tup + 0x10), 40)
        impl = u64(tup + 0x18)
        rows.append((tag, runtime_type_name(impl)))
    print(f"{i:3d} iface={iname!r} tags={rows}")
