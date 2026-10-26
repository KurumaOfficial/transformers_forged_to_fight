"""Read live BCGManager.Instance.BaseHeroData[bid][rank].AttributeData (read-only)."""
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADB = str(ROOT / "work" / "platform-tools" / "adb.exe")
ELF = str(ROOT / "work" / "unpacked" / "lib" / "arm64-v8a" / "libil2cpp.so")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def adb(args, timeout=120):
    return subprocess.run([ADB] + args, capture_output=True, timeout=timeout)


pid = adb(["shell", "pidof com.kabam.bigrobot"]).stdout.decode().strip()
elf = open(ELF, "rb").read()
e_phoff = struct.unpack_from("<Q", elf, 32)[0]
e_phentsize = struct.unpack_from("<H", elf, 54)[0]
e_phnum = struct.unpack_from("<H", elf, 56)[0]
wv = None
for i in range(e_phnum):
    o = e_phoff + i * e_phentsize
    t, fl, fo, va, pa, fs, ms, al = struct.unpack_from("<IIQQQQQQ", elf, o)
    if t == 1 and (fl & 2):
        wv = va
maps = adb(["shell", f"su 0 cat /proc/{pid}/maps"]).stdout.decode("latin1", "replace")
BASE = None
for line in maps.splitlines():
    if "libil2cpp.so" in line and "rw-p" in line and "02a97000" in line:
        BASE = int(line.split("-")[0], 16) - wv
        break
print("pid", pid, "base", hex(BASE))


def mem(a, n=8):
    return adb(["exec-out", "su", "0", "dd", f"if=/proc/{pid}/mem", "bs=1", f"count={n}",
                f"skip={a}", "status=none"]).stdout


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


def cstr(a, n=80):
    if not a:
        return None
    b = mem(a, n)
    return b.split(b"\x00")[0].decode("latin1", "replace") if b else None


def ilstr(a):
    if not a:
        return None
    n = u32(a + 0x10)
    if n is None or n > 200:
        return None
    b = mem(a + 0x14, n * 2)
    return b.decode("utf-16le", "replace") if b else None


def cname(o):
    if not o:
        return None
    c = u64(o)
    return cstr(u64(c + 0x10)) if c else None


def dict_entries(d):
    """Return [(key_ptr, value_ptr)] for a .NET Dictionary."""
    if not d:
        return []
    buckets = u64(d + 0x10)
    entries = u64(d + 0x18)
    count = i32(d + 0x20)
    out = []
    if not entries or not count:
        return out
    for i in range(min(count, 2000)):
        e = entries + 0x20 + i * 24
        h = i32(e)
        nxt = i32(e + 4)
        k = u64(e + 8)
        v = u64(e + 16)
        if h is not None and h >= 0 and k:
            out.append((k, v))
    return out


# BCGManager.get_Instance: slot -> type info -> class -> +0x18 -> +0xc0 -> +0xb8 -> instance
slot = u64(BASE + 0x2BC1000 + 0xC68)
cls0 = u64(slot) if slot else None
wrap = u64(cls0 + 0x18) if cls0 else None
x = u64(wrap + 0xC0) if wrap else None
cls = u64(x) if x else None
sf = u64(cls + 0xB8) if cls else None
inst = u64(sf) if sf else None
print("slots", hex(slot) if slot else None, hex(cls0) if cls0 else None, hex(wrap) if wrap else None,
      hex(cls) if cls else None, "instance", hex(inst) if inst else None, cname(inst) if inst else None)
if not inst:
    raise SystemExit("no BCGManager")
base_hero = u64(inst + 0x48)
print("BaseHeroData", hex(base_hero) if base_hero else None, cname(base_hero) if base_hero else None)
for k, v in dict_entries(base_hero):
    name = ilstr(k)
    if name not in ("bumblebee_cin_dotm_2", "sideswipe_gs"):
        continue
    print("\nbid", name, "ranks obj", hex(v) if v else None, cname(v) if v else None)
    # BCGHeroBase may be a List<BCGHeroBaseCommon> or Dictionary<int,...>
    print("  keys/entries", len(dict_entries(v)))
    for rk, rv in dict_entries(v):
        rank = i32(rk) if rk and rk > 0x1000 else rk
        print("  rank key", rank if isinstance(rank, int) else ilstr(rk), "entry", hex(rv) if rv else None,
              cname(rv) if rv else None)
        # try both direct list item and dictionary value
        attr = u64(rv + 0x48) if rv else None
        print("    attr", hex(attr) if attr else None, cname(attr) if attr else None)
        if attr:
            for off, lab in [(0x2C, "HPMax"), (0x38, "Attack"), (0x40, "Armor"),
                             (0x44, "CritChance"), (0x48, "CritDamage"), (0x50, "BlockProf"),
                             (0x54, "ManaGain"), (0x58, "ManaStart")]:
                if lab in ("HPMax", "Attack"):
                    val = i32(attr + off)
                else:
                    val = f32(attr + off)
                print(f"      +{off:#x} {lab} {val}")
