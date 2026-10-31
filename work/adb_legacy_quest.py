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

def cstr(p, n=80):
    b = mem(p, n)
    return b.split(b"\x00")[0].decode("latin1", "replace") if b else None

def name_of(o):
    c = u64(o) if o else None
    np = u64(c + 0x10) if c else None
    return cstr(np) if np else "?"

def ilstr(p, n=120):
    if not p:
        return None
    ln = u32(p + 0x10)
    if ln is None or ln > n:
        return None
    b = mem(p + 0x14, ln * 2)
    return b.decode("utf-16-le", "replace") if b else None

print("pid", PID, "base", hex(BASE))
# Legacy.QuestsManager.Instance via get_Instance at 0xD63A60
slot = BASE + 0x2C08D68
a = u64(slot)
cls = u64(a) if a else None
sf = u64(cls + 0xB8) if cls else None
inst = u64(sf + 8) if sf else None
print("legacy QuestsManager: slot", hex(slot), "a", a and hex(a), "class", cls and hex(cls), name_of(cls), "statics", sf and hex(sf), "instance", inst and hex(inst), name_of(inst))
if not inst:
    raise SystemExit("no legacy manager instance")
db = u64(inst + 0x70)
print("QuestDB", db and hex(db), name_of(db))
if not db:
    raise SystemExit("no DB")
active = u64(db + 0x18)
print("ActiveQuests dict", active and hex(active), name_of(active))
if not active:
    raise SystemExit("no active dict")
cnt = u32(active + 0x20)
entries = u64(active + 0x18)
print("count", cnt, "entries", entries and hex(entries))
for i in range(min(cnt or 0, 20)):
    e = entries + 0x20 + i * 24
    k = u64(e + 8)
    v = u64(e + 16)
    print(f"  [{i}] key={ilstr(k)!r} value={v and hex(v)} class={name_of(v) if v else None}")
    if v:
        print("    qid", ilstr(u64(v + 0x40)), "category", ilstr(u64(v + 0x38)))
        print("    pendingCount", u32(v + 0xC8), "pendingUpdates", u64(v + 0xD0))
        prog = u64(v + 0x50)
        print("    progression", prog and hex(prog))
        if prog:
            print("      version", u32(prog + 0x10), "outOfSync", mem(prog + 0x14, 1).hex())
            pos = mem(prog + 0x18, 8)
            if len(pos) == 8:
                print("      currentPos", struct.unpack("<ff", pos))
            print("      currentFightId", ilstr(u64(prog + 0x38)))
            print("      currentBattleId", ilstr(u64(prog + 0x40)))
            print("      currentBattlePos", mem(prog + 0x50, 8).hex())
            print("      cleared", u64(prog + 0x20))
