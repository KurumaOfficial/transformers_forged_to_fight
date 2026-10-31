"""Read-only probe: WindowManager -> PreFightScreen -> PrefightScreenData -> TeamData.

No Frida/gadget/patches. Reads /proc/<pid>/mem through `su 0 dd`.
"""
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
    p = subprocess.run([ADB, "shell", f"su 0 dd if=/proc/{PID}/mem bs=1 count={n} skip={a} 2>/dev/null | xxd -p"],
                       capture_output=True, text=True)
    h = "".join(p.stdout.split())
    return bytes.fromhex(h) if h and re.fullmatch(r"[0-9a-fA-F]+", h) else b""


def u64(a):
    b = mem(a, 8)
    return struct.unpack("<Q", b)[0] if len(b) == 8 else None


def u32(a):
    b = mem(a, 4)
    return struct.unpack("<I", b)[0] if len(b) == 4 else None


def i32(a):
    b = mem(a, 4)
    return struct.unpack("<i", b)[0] if len(b) == 4 else None


def f32(a):
    b = mem(a, 4)
    return struct.unpack("<f", b)[0] if len(b) == 4 else None


def cstr(p, n=120):
    b = mem(p, n)
    return b.split(b"\x00")[0].decode("latin1", "replace") if b else None


def ilstr(p, n=160):
    if not p:
        return None
    ln = u32(p + 0x10)
    if ln is None or ln > n:
        return None
    b = mem(p + 0x14, ln * 2)
    return b.decode("utf-16-le", "replace") if b else None


def name_of(o):
    if not o:
        return None
    c = u64(o)
    np = u64(c + 0x10) if c else None
    return cstr(np) if np else "?"


def dict_items(d, limit=40):
    if not d:
        return []
    cnt = u32(d + 0x20)
    ent = u64(d + 0x18)
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
    cnt = u32(l + 0x18)
    arr = u64(l + 0x10)
    if not arr:
        return []
    return [u64(arr + 0x20 + i * 8) for i in range(min(cnt or 0, limit))]


print("pid", PID, "base", hex(BASE))

# WindowManager.Instance: get_Instance at 0x1586354.
# slot -> pointer-to-class-pointer -> Il2CppClass -> static_fields -> Instance
slot = BASE + 0x2BE5B18
p = u64(slot)
klass = u64(p) if p else None
sf = u64(klass + 0xB8) if klass else None
wm = u64(sf + 8) if sf else None
print("WindowManager slot", hex(slot), "p", hex(p) if p else None,
      "class", hex(klass) if klass else None, name_of(klass) if klass else None)
print("WindowManager", hex(wm) if wm else None, name_of(wm) if wm else None)
if not wm:
    # fallback: single indirection
    klass2 = p
    sf2 = u64(klass2 + 0xB8) if klass2 else None
    wm = u64(sf2 + 8) if sf2 else None
    print("fallback WindowManager", hex(wm) if wm else None, name_of(wm) if wm else None)
if not wm:
    raise SystemExit("no WindowManager")

stacks = u64(wm + 0x98)
print("windowStacks", hex(stacks) if stacks else None, name_of(stacks) if stacks else None)
windows = []
for k, v in dict_items(stacks, 20):
    print(" layer key", k, "stack", hex(v) if v else None, name_of(v) if v else None)
    for wi in list_items(v, 30):
        nm = ilstr(u64(wi + 0x10)) if wi else None
        win = u64(wi + 0x48) if wi else None
        wn = name_of(win) if win else None
        print("   WindowInfo", hex(wi) if wi else None, "name", repr(nm), "window", hex(win) if win else None, wn)
        windows.append((nm, wi, win))

# also scan preloadedWindows list at +0xF0
print("preloadedWindows", hex(u64(wm + 0xF0)) if u64(wm + 0xF0) else None)
for wi in list_items(u64(wm + 0xF0), 20):
    nm = ilstr(u64(wi + 0x10)) if wi else None
    win = u64(wi + 0x48) if wi else None
    print("   preload", hex(wi) if wi else None, repr(nm), hex(win) if win else None, name_of(win) if win else None)
    windows.append((nm, wi, win))

target = None
for nm, wi, win in windows:
    if win and name_of(win) == "PreFightScreen":
        target = (nm, wi, win)
        break
if not target:
    for nm, wi, win in windows:
        if nm and "refight" in nm.lower():
            target = (nm, wi, win)
            break
print("TARGET", target)
if target:
    nm, wi, win = target
    model = u64(win + 0x98)
    pres = u64(win + 0xA0)
    print("PreFightScreen model", hex(model) if model else None, name_of(model) if model else None)
    print("PreFightScreen presentation", hex(pres) if pres else None, name_of(pres) if pres else None)
    if model:
        cur = u64(model + 0x30)
        enemy = u64(model + 0x38)
        tower = u64(model + 0x40)
        aq = u64(model + 0x50)
        idx = i32(model + 0x20)
        print(" PrefightScreenData currentTeam", hex(cur) if cur else None, name_of(cur) if cur else None)
        print("  enemy", hex(enemy) if enemy else None, name_of(enemy) if enemy else None,
              "tower", hex(tower) if tower else None, name_of(tower) if tower else None)
        print("  activeQuest", hex(aq) if aq else None, name_of(aq) if aq else None, "currentHeroIndex", idx)
        if cur:
            active = u64(cur + 0x10)
            saved = u64(cur + 0x18)
            mode = i32(cur + 0x20)
            heroes = u64(cur + 0x30)
            print("  TeamData mActiveTeam", hex(active) if active else None, name_of(active) if active else None)
            print("  TeamData mSavedTeam", hex(saved) if saved else None, name_of(saved) if saved else None)
            print("  TeamData mMode", mode, "mHeroes", hex(heroes) if heroes else None,
                  name_of(heroes) if heroes else None, "count", u32(heroes + 0x18) if heroes else None)
            for h in list_items(heroes, 8):
                print("    HeroData", hex(h) if h else None, name_of(h) if h else None,
                      "level", i32(h + 0x38) if h else None,
                      "blueprintPtr", hex(u64(h + 0x48)) if h and u64(h + 0x48) else None,
                      "blueprint", repr(ilstr(u64(h + 0x48))) if h and u64(h + 0x48) else None)
        if aq:
            print("  ActiveQuest mode", repr(ilstr(u64(aq + 0x18))), "qid", repr(ilstr(u64(aq + 0x40))),
                  "prog", hex(u64(aq + 0x50)) if u64(aq + 0x50) else None)

# BCG heroes dict values and blueprint catalog
bslot = BASE + 0x2BC1C68
p1 = u64(bslot); p2 = u64(p1) if p1 else None
p3 = u64(p2 + 0x18) if p2 else None
p4 = u64(p3 + 0xC0) if p3 else None
p5 = u64(p4) if p4 else None
bsf = u64(p5 + 0xB8) if p5 else None
bcg = u64(bsf) if bsf else None
print("BCGManager", hex(bcg) if bcg else None)
if bcg:
    ud = u64(bcg + 0x30)
    print("UserData", hex(ud) if ud else None)
    heroes = u64(ud + 0x10) if ud else None
    print("heroes dict", hex(heroes) if heroes else None, name_of(heroes) if heroes else None)
    for k, v in dict_items(heroes, 10):
        key = ilstr(k)
        print("  hero key", repr(key), "value", hex(v) if v else None, name_of(v) if v else None)
        if v:
            print("    EntityType", repr(ilstr(u64(v + 0x10))), "Blueprint", repr(ilstr(u64(v + 0x18))),
                  "Rank", i32(v + 0x20), "Level", i32(v + 0x24), "Sig", i32(v + 0x28),
                  "Attr", hex(u64(v + 0x38)) if u64(v + 0x38) else None)
    bp = u64(bcg + 0x50)
    print("blueprint dict (BCGManager+0x50)", hex(bp) if bp else None, name_of(bp) if bp else None,
          "count", u32(bp + 0x20) if bp else None)
    for k, v in dict_items(bp, 20):
        print("  bp", repr(ilstr(k)), "->", hex(v) if v else None, name_of(v) if v else None)
