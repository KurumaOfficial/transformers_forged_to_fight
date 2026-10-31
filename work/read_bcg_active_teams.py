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
    raise SystemExit("no lib base")
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
def cstr(p, n=100):
    b = mem(p, n)
    return b.split(b"\x00")[0].decode("latin1", "replace") if b else None
def ilstr(p, n=160):
    if not p: return None
    ln = u32(p + 0x10)
    if ln is None or ln > n: return None
    b = mem(p + 0x14, ln * 2)
    return b.decode("utf-16-le", "replace") if b else None
def name_of(o):
    c = u64(o) if o else None
    np = u64(c + 0x10) if c else None
    return cstr(np) if np else "?"
def dump_dict(d, label, maxn=20):
    print(label, hex(d) if d else None, name_of(d) if d else None)
    if not d: return
    cnt = u32(d + 0x20); ent = u64(d + 0x18)
    print(" count", cnt, "entries", hex(ent) if ent else None)
    if not ent: return
    for i in range(min(cnt or 0, maxn)):
        e = ent + 0x20 + i * 24
        k = u64(e + 8); v = u64(e + 16)
        print("  ", i, "key", repr(ilstr(k)), "value", hex(v) if v else None, name_of(v) if v else None)
print("BASE", hex(BASE))
slot = BASE + 0x2BC1C68
a = u64(slot); cls = u64(a) if a else None; sf = u64(cls + 0xB8) if cls else None
inst = u64(sf + 8) if sf else None
print("slot", hex(slot), "a", hex(a) if a else None, "cls", hex(cls) if cls else None, "sf", hex(sf) if sf else None, "inst", hex(inst) if inst else None, name_of(inst) if inst else None)
if inst:
    for off in range(0x10, 0x80, 8):
        p = u64(inst + off)
        if p:
            print(f"inst+0x{off:x} -> {hex(p)} {name_of(p)}")
    ud = u64(inst + 0x30)
    print("userData", hex(ud) if ud else None, name_of(ud) if ud else None)
    if ud:
        for off in range(0x10, 0x60, 8):
            p = u64(ud + off)
            if p:
                print(f"  ud+0x{off:x} -> {hex(p)} {name_of(p)}")
        for off in (0x28, 0x30, 0x38):
            p = u64(ud + off)
            if p and "Dictionary" in (name_of(p) or ""):
                dump_dict(p, f"activeTeams? ud+0x{off:x}")
