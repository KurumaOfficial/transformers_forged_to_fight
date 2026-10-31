import subprocess, struct, re, sys

ADB = r".\work\platform-tools\adb.exe"
PID = sys.argv[1]

def sh(cmd):
    return subprocess.run([ADB, "shell", f"su 0 {cmd}"], capture_output=True, text=True).stdout

def get_base():
    maps = sh(f"cat /proc/{PID}/maps")
    elf = open(r".\work\unpacked\lib\arm64-v8a\libil2cpp.so", "rb").read()
    e_phoff = struct.unpack_from("<Q", elf, 32)[0]
    e_phentsize = struct.unpack_from("<H", elf, 54)[0]
    e_phnum = struct.unpack_from("<H", elf, 56)[0]
    wv = None
    for i in range(e_phnum):
        off = e_phoff + i * e_phentsize
        t, fl, fo, va, pa, fs, ms, al = struct.unpack_from("<IIQQQQQQ", elf, off)
        if t == 1 and (fl & 2):
            wv = (va, fo)
    for line in maps.splitlines():
        if "libil2cpp.so" in line and "rw-p" in line:
            start = int(line.split("-")[0], 16)
            fileoff = int(line.split()[2], 16)
            return start - wv[0]
    for line in maps.splitlines():
        if "libil2cpp.so" in line and " 00000000 " in line:
            return int(line.split("-")[0], 16)
    raise SystemExit("no libil2cpp map")

BASE = get_base()

def mem(addr, size):
    p = subprocess.run([ADB, "shell", f"su 0 dd if=/proc/{PID}/mem bs=1 count={size} skip={addr} 2>/dev/null | xxd -p"], capture_output=True, text=True)
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
    if not p:
        return None
    ln = u32(p + 0x10)
    if ln is None or ln > n:
        return None
    b = mem(p + 0x14, ln * 2)
    return b.decode("utf-16le", "replace") if b else None

def class_name(o):
    if not o:
        return None
    k = u64(o)
    if not k:
        return None
    np = u64(k + 0x10)
    return cstr(np) if np else None

def typeinfo_inst(rva):
    slot = BASE + rva
    cls = u64(slot)
    if not cls:
        return None, None, None
    sf = u64(cls + 0xB8)
    inst = u64(sf) if sf else None
    return cls, sf, inst

def dump_manager(rva, name, fields):
    cls, sf, inst = typeinfo_inst(rva)
    print(f"{name}: class={cls and hex(cls)} sf={sf and hex(sf)} inst={inst and hex(inst)} objclass={class_name(inst)}")
    if not inst:
        return None
    for off, label in fields:
        v = u64(inst + off)
        print(f"  +{off:#04x} {label} = {hex(v) if v else 0}")
    return inst

if __name__ == "__main__":
    print(f"pid={PID} base={BASE:#x}")
    fe = dump_manager(0x2D0ADF0, "FeaturedHeroManager", [(0x18, "state/priority"), (0x20, "Heroes"), (0x28, "OrderType")])
    if fe:
        h = u64(fe + 0x20)
        if h:
            cnt = u32(h + 0x18)
            arr = u64(h + 0x10)
            print(f"  Heroes.Count={cnt} arr={hex(arr) if arr else 0}")
            if arr and cnt:
                for i in range(min(cnt, 20)):
                    it = u64(arr + 0x20 + i * 8)
                    if not it:
                        continue
                    bp = ilstr(u64(it + 0x10))
                    print(f"    [{i}] {hex(it)} bp={bp!r}")
        print(f"  OrderType={ilstr(u64(fe + 0x28))!r}")

    bcg = dump_manager(0x2D091F8, "BCGManager", [(0x30, "UserData")])
    if bcg:
        ud = u64(bcg + 0x30)
        if ud:
            heroes = u64(ud + 0x10)
            print(f"  UserData={hex(ud)} heroesDict={hex(heroes) if heroes else 0}")
            if heroes:
                print(f"    heroes count={u32(heroes + 0x20)}")
