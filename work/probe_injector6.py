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
def cstr(p, n=160):
    b = mem(p, n); return b.split(b"\x00")[0].decode("latin1", "replace") if b else None
def ilstr(p, n=200):
    if not p: return None
    b = mem(p + 0x10, 4)
    if len(b) < 4: return None
    ln = struct.unpack("<I", b)[0]
    if ln > n: return None
    b = mem(p + 0x14, ln * 2); return b.decode("utf-16-le", "replace") if b else None
def type_name(t):
    if not t: return None
    for off in (0x10, 0x8, 0x18):
        k = u64(t + off)
        if k:
            np = u64(k + 0x10)
            s = cstr(np) if np else None
            if s and len(s) > 1 and all(32 <= ord(c) < 127 for c in s):
                return s
    return None
def klass_name(k):
    if not k: return None
    np = u64(k + 0x10)
    return cstr(np) if np else None

slot = BASE + 0x2C33650
p1 = u64(slot); cls = u64(p1); sf = u64(cls + 0xB8)
print("base", hex(BASE), "class", hex(cls), "sf", hex(sf))
print("currentTag", repr(ilstr(u64(sf+8))), "init byte", mem(sf + 0x10, 1).hex())
g = u64(sf + 0x0)
cnt = u32(g + 0x20); ent = u64(g + 0x18)
print("gameInterfaces count", cnt, "entries", hex(ent))
raw = mem(ent, cnt * 24)
for i in range(cnt):
    e = raw[i*24:(i+1)*24]
    h, k, v = struct.unpack_from("<I", e, 0)[0], struct.unpack_from("<Q", e, 8)[0], struct.unpack_from("<Q", e, 16)[0]
    tn = type_name(k)
    print(f"{i:3d} key={k:#x} type={tn!r} list={v:#x}")
    if v:
        lc = u32(v + 0x18); arr = u64(v + 0x10)
        if lc and lc < 20 and arr:
            araw = mem(arr + 0x20, lc * 8)
            for j in range(lc):
                tup = struct.unpack_from("<Q", araw, j*8)[0]
                if not tup: continue
                # Tuple<string,Type>: item1 at +0x10, item2 at +0x18
                s = ilstr(u64(tup + 0x10), 60)
                impl = u64(tup + 0x18)
                print(f"      tag={s!r} impl={impl and hex(impl)} impltype={type_name(impl)}")
