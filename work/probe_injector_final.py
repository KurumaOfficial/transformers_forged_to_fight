import subprocess, struct, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ADB = r".\work\platform-tools\adb.exe"
PID = subprocess.run([ADB, "shell", "pidof com.kabam.bigrobot"], capture_output=True, text=True).stdout.strip()
maps = subprocess.run([ADB, "shell", f"su 0 cat /proc/{PID}/maps"], capture_output=True, text=True).stdout
rw = None
for line in maps.splitlines():
    if "libil2cpp.so" in line and "rw-p" in line and "2a97000" in line:
        rw = int(line.split("-")[0], 16)
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
def ilstr(p, n=200):
    if not p: return None
    b = mem(p + 0x10, 4)
    if len(b) < 4: return None
    ln = struct.unpack("<I", b)[0]
    if ln > n: return None
    b = mem(p + 0x14, ln * 2); return b.decode("utf-16-le", "replace") if b else None
def name_of(o):
    if not o: return None
    k = u64(o)
    if not k: return None
    np = u64(k + 0x10)
    return cstr(np) if np else None
def list_items(l, limit=10):
    if not l: return []
    cnt = u32(l + 0x18); arr = u64(l + 0x10)
    if not cnt or not arr or cnt > limit: return []
    raw = mem(arr + 0x20, cnt * 8)
    return [struct.unpack_from("<Q", raw, i*8)[0] for i in range(cnt) if len(raw) >= (i+1)*8]
def type_name(t):
    if not t: return None
    # System.RuntimeType object: try +0x10 as Il2CppType*, then data
    tp = u64(t + 0x10)
    if tp:
        k = u64(tp)
        if k:
            n = name_of(k)
            if n and n not in ("RuntimeType",): return n
    # try +0x18
    for off in (0x18, 0x20, 0x8):
        v = u64(t + off)
        if v:
            n = name_of(v)
            if n and n != "RuntimeType": return n
    return None

slot = BASE + 0x2C33650
p1 = u64(slot); cls = u64(p1); sf = u64(cls + 0xB8)
print("base", hex(BASE), "class", hex(cls), "sf", hex(sf), "classname", name_of(p1))
print("tag", repr(ilstr(u64(sf + 8))), "init", mem(sf + 0x10, 1).hex())
g = u64(sf + 0)
cnt = u32(g + 0x20); ent = u64(g + 0x18)
print("game dict", hex(g), "count", cnt, "entries", hex(ent) if ent else None)
raw = mem(ent, cnt * 24) if ent else b""
print("raw", len(raw))
for i in range(cnt):
    e = raw[i*24:(i+1)*24]
    if len(e) < 24: break
    h, k, v = struct.unpack_from("<I", e, 0)[0], struct.unpack_from("<Q", e, 8)[0], struct.unpack_from("<Q", e, 16)[0]
    print(f"{i:3d} hash={h:#x} key={k:#x} keyclass={name_of(k)!r} val={v:#x} valclass={name_of(v)!r}")
    for tup in list_items(v):
        tag = ilstr(u64(tup + 0x10), 40)
        impl = u64(tup + 0x18)
        print(f"      tuple={tup:#x} tag={tag!r} impl={impl:#x} implclass={name_of(impl)!r} impltype={type_name(impl)!r}")
p = u64(sf + 0x18); pc = u32(p + 0x20); pe = u64(p + 0x18)
print("persistent", hex(p) if p else None, "count", pc)
raw2 = mem(pe, max(pc,1)*24) if pe else b""
for i in range(min(pc, 10)):
    e = raw2[i*24:(i+1)*24]
    if len(e) < 24: break
    h, k, v = struct.unpack_from("<I", e, 0)[0], struct.unpack_from("<Q", e, 8)[0], struct.unpack_from("<Q", e, 16)[0]
    print(f"  P{i} key={k:#x} keyclass={name_of(k)!r} val={v:#x} valclass={name_of(v)!r}")
