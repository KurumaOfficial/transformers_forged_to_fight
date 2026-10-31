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
def cstr(p, n=80):
    b = mem(p, n)
    return b.split(b"\x00")[0].decode("latin1", "replace") if b else None
def ilstr(p, n=120):
    if not p: return None
    ln = u32(p + 0x10)
    if ln is None or ln > n: return None
    b = mem(p + 0x14, ln * 2)
    return b.decode("utf-16-le", "replace") if b else None
def name_of(o):
    c = u64(o) if o else None
    np = u64(c + 0x10) if c else None
    return cstr(np) if np else "?"
def dump_dict(d, label):
    print(label, hex(d) if d else None, name_of(d) if d else None)
    if not d: return
    cnt = u32(d + 0x20)
    ent = u64(d + 0x18)
    print(" count", cnt, "entries", hex(ent) if ent else None)
    if not ent: return
    for i in range(min(cnt or 0, 10)):
        e = ent + 0x20 + i * 24
        k = u64(e + 8); v = u64(e + 16)
        print("  ", i, "key", repr(ilstr(k)), "value", hex(v) if v else None,
              name_of(v) if v else None)
        if v:
            for off, lab in [(0x10,"uid"),(0x18,"name"),(0x20,"tag"),(0x28,"strongest"),
                             (0x38,"battleId"),(0x40,"battleState"),(0x68,"team")]:
                if off in (0x10,0x18,0x20,0x28,0x38):
                    print("    ", lab, repr(ilstr(u64(v+off))))
                elif off == 0x40:
                    print("    ", lab, u32(v+off))
                else:
                    print("    ", lab, hex(u64(v+off)) if u64(v+off) else None)
# locate active quest via QuestsManager
slot = BASE + 0x2C08D68
a = u64(slot); cls = u64(a) if a else None; sf = u64(cls + 0xB8) if cls else None
inst = u64(sf + 8) if sf else None
db = u64(inst + 0x70) if inst else None
active = u64(db + 0x18) if db else None
if not active: raise SystemExit("no active")
cnt = u32(active + 0x20); entries = u64(active + 0x18)
for i in range(min(cnt or 0, 5)):
    e = entries + 0x20 + i * 24
    v = u64(e + 16)
    if not v: continue
    print("QUEST", repr(ilstr(u64(v + 0x40))))
    prog = u64(v + 0x50)
    print("progression", hex(prog))
    for off, lab in [(0x38,"cfid"),(0x40,"cbid"),(0x48,"cboss"),(0x58,"enemyHp"),
                     (0x80,"localPlayer"),(0x88,"users")]:
        if off in (0x38,0x40,0x48):
            print(lab, repr(ilstr(u64(prog+off))))
        elif off == 0x58:
            b = mem(prog+off,4); print(lab, struct.unpack("<f",b)[0] if len(b)==4 else None)
        else:
            p = u64(prog+off); print(lab, hex(p) if p else None, name_of(p) if p else None)
    lp = u64(prog+0x80)
    if lp:
        print("LOCAL PLAYER", hex(lp), name_of(lp))
        print("  uid", repr(ilstr(u64(lp+0x10))), "name", repr(ilstr(u64(lp+0x18))),
              "strongest", repr(ilstr(u64(lp+0x28))))
        print("  team", hex(u64(lp+0x68)) if u64(lp+0x68) else None)
        dump_dict(u64(prog+0x88), "users")
        team = u64(lp + 0x68)
        if team:
            tname = name_of(team)
            if tname and "List" in tname:
                lc = u32(team + 0x18)
                print("local team", hex(team), tname, "count", lc)
                arr = u64(team + 0x10)
                if arr and lc:
                    for i in range(min(lc, 10)):
                        item = u64(arr + 0x20 + i * 8)
                        print("   hero", i, hex(item) if item else None,
                              name_of(item) if item else None,
                              "blueprint", repr(ilstr(u64(item + 0x10))) if item else None,
                              "hp", u32(item + 0x18) if item else None)
            else:
                dump_dict(team, "local team")
