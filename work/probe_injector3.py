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
    ln = u32(p + 0x10)
    if ln is None or ln > n: return None
    b = mem(p + 0x14, ln * 2); return b.decode("utf-16-le", "replace") if b else None
def klass_name(k):
    if not k: return None
    np = u64(k + 0x10)
    return cstr(np) if np else None
def type_name(t):
    if not t: return None
    # Il2CppReflectionType.type
    k = u64(t + 0x10)
    return klass_name(k)
def name_of(o):
    k = u64(o) if o else None
    return klass_name(k)
def dict_entries(d):
    if not d: return []
    cnt = u32(d + 0x20); ent = u64(d + 0x18)
    out = []
    if not ent: return out
    for i in range(min(cnt or 0, 20000)):
        e = ent + 0x20 + i * 24
        out.append((u32(e), u64(e + 8), u64(e + 16)))
    return out

slot = BASE + 0x2C33650
cls = u64(slot)
sf = u64(cls + 0xB8)
print("base", hex(BASE), "class", hex(cls), "sf", hex(sf))
for off in range(0, 0x28, 8):
    v = u64(sf + off)
    print(f"sf+{off:#x} = {hex(v) if v else None}  {name_of(v) if v else ''}")
# try dict at sf+0
for base_off in (0, 8, 0x10, 0x18):
    d = u64(sf + base_off)
    if not d: continue
    cnt = u32(d + 0x20)
    ent = u64(d + 0x18)
    print(f"--- candidate dict at sf+{base_off:#x} d={d:#x} count={cnt} entries={ent and hex(ent)}")
    if not ent or not cnt or cnt > 100000: continue
    for i, (h, k, v) in enumerate(dict_entries(d)[:20]):
        print(f"  entry {i}: hash={h} key={k and hex(k)} keytype={type_name(k)} keyname={name_of(k)} val={v and hex(v)} valname={name_of(v)}")
