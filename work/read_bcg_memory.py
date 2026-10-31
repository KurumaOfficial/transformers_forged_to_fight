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

def f32(a):
    b = mem(a, 4)
    return struct.unpack("<f", b)[0] if len(b) == 4 else None

def cstr(p, n=100):
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

def dict_items(d, limit=30):
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

def list_items(l, limit=20):
    if not l:
        return []
    cnt = u32(l + 0x18); arr = u64(l + 0x10)
    if not arr:
        return []
    return [u64(arr + 0x20 + i * 8) for i in range(min(cnt or 0, limit))]

print("pid", PID, "base", hex(BASE))
# BCGManager.Instance generic-static chain from get_Instance 0xA5C688.
slot = BASE + 0x2BC1C68
p1 = u64(slot); p2 = u64(p1) if p1 else None
p3 = u64(p2 + 0x18) if p2 else None
p4 = u64(p3 + 0xC0) if p3 else None
p5 = u64(p4) if p4 else None
sf = u64(p5 + 0xB8) if p5 else None
inst = u64(sf) if sf else None
print("BCGManager", hex(inst) if inst else None, name_of(inst) if inst else None)
if not inst:
    raise SystemExit("no BCGManager")
ud = u64(inst + 0x30)
print("UserData", hex(ud) if ud else None, name_of(ud) if ud else None)
print("heroes", hex(u64(ud + 0x10)) if ud and u64(ud + 0x10) else None,
      name_of(u64(ud + 0x10)) if ud and u64(ud + 0x10) else None)
hd = u64(ud + 0x10) if ud else None
print("HERO KEYS", [(repr(ilstr(k)), hex(v) if v else None, name_of(v) if v else None)
                    for k, v in dict_items(hd, 10)])
print("savedTeams", hex(u64(ud + 0x28)) if ud and u64(ud + 0x28) else None,
      name_of(u64(ud + 0x28)) if ud and u64(ud + 0x28) else None)
print("activeTeams", hex(u64(ud + 0x30)) if ud and u64(ud + 0x30) else None,
      name_of(u64(ud + 0x30)) if ud and u64(ud + 0x30) else None)
ats = u64(ud + 0x30) if ud else None
for k, v in dict_items(ats, 20):
    key = ilstr(k)
    print("ACTIVE", repr(key), hex(v) if v else None, name_of(v) if v else None)
    if not v:
        continue
    print("  aid", repr(ilstr(u64(v + 0x10))), "type", repr(ilstr(u64(v + 0x18))),
          "expire", u32(v + 0x30))
    modes = u64(v + 0x20)
    print("  modes list", hex(modes) if modes else None, [ilstr(x) for x in list_items(modes, 5)])
    th = u64(v + 0x28)
    print("  TeamHeroes", hex(th) if th else None, name_of(th) if th else None,
          "count", u32(th + 0x18) if th else None)
    for hp in list_items(th, 5):
        print("    hero", hex(hp) if hp else None, name_of(hp) if hp else None,
              "blueprint", repr(ilstr(u64(hp + 0x10))), "rank", u32(hp + 0x18),
              "level", u32(hp + 0x1C), "sig", u32(hp + 0x20),
              "hpRating", u32(hp + 0x24), "hpMax", u32(hp + 0x28),
              "atkRating", u32(hp + 0x2C), "atk", u32(hp + 0x30),
              "owned", mem(hp + 0x38, 1).hex())
# QuestsManager -> active quest -> localPlayer.team
qslot = BASE + 0x2C08D68
qa = u64(qslot); qcls = u64(qa) if qa else None; qsf = u64(qcls + 0xB8) if qcls else None
qinst = u64(qsf + 8) if qsf else None
print("QuestsManager", hex(qinst) if qinst else None, name_of(qinst) if qinst else None)
if qinst:
    db = u64(qinst + 0x70); active = u64(db + 0x18) if db else None
    for k, v in dict_items(active, 5):
        print("QUEST", repr(ilstr(u64(v + 0x40))), "mode", repr(ilstr(u64(v + 0x18))), "ptr", hex(v))
        prog = u64(v + 0x50)
        if prog:
            lp = u64(prog + 0x80)
            print("  localPlayer", hex(lp) if lp else None, name_of(lp) if lp else None)
            if lp:
                print("  team ptr", hex(u64(lp + 0x68)) if u64(lp + 0x68) else None,
                      name_of(u64(lp + 0x68)) if u64(lp + 0x68) else None,
                      "count", u32(u64(lp + 0x68) + 0x18) if u64(lp + 0x68) else None)
