import re
import struct
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ADB = r".\work\platform-tools\adb.exe"
ROOT = r"."
PID = subprocess.run([ADB, "shell", "pidof com.kabam.bigrobot"], capture_output=True, text=True).stdout.strip()
if not PID:
    raise SystemExit("app not running")
maps_text = subprocess.run([ADB, "shell", f"su 0 cat /proc/{PID}/maps"], capture_output=True, text=True).stdout
MAPS = []
for line in maps_text.splitlines():
    m = re.match(r"([0-9a-f]+)-([0-9a-f]+)\s+(\S+)\s+\S+\s+\S+\s+\S+\s*(.*)", line)
    if m:
        MAPS.append((int(m.group(1), 16), int(m.group(2), 16), m.group(3), m.group(4).strip()))
rw = [s for s, e, p, n in MAPS if "libil2cpp.so" in n and p == "rw-p" and "2a97000" in ""]
# find the rw mapping by its file offset from maps: use the first rw-p libil2cpp line with offset 02a97000
for line in maps_text.splitlines():
    if "libil2cpp.so" in line and "rw-p" in line and "02a97000" in line:
        rw_start = int(line.split("-")[0], 16)
        break
else:
    raise SystemExit("no libil2cpp rw mapping")
BASE = rw_start - 0x2AA7000
META = open(ROOT + r"\work\unpacked\assets\bin\Data\Managed\Metadata\global-metadata.dat", "rb").read()
STR_OFF = struct.unpack_from("<I", META, 0x18)[0]
STR_SIZE = struct.unpack_from("<I", META, 0x1C)[0]


def read_mem(addr, size):
    p = subprocess.run([ADB, "shell", f"su 0 dd if=/proc/{PID}/mem bs=1 count={size} skip={addr} 2>/dev/null | xxd -p"], capture_output=True, text=True)
    h = "".join(p.stdout.split())
    return bytes.fromhex(h) if h and re.fullmatch(r"[0-9a-fA-F]+", h) else b""


def u64(a):
    b = read_mem(a, 8); return struct.unpack("<Q", b)[0] if len(b) == 8 else None


def u32(a):
    b = read_mem(a, 4); return struct.unpack("<I", b)[0] if len(b) == 4 else None


def meta_offset(name):
    needle = name.encode() + b"\x00"
    off = META.find(needle, STR_OFF, STR_OFF + STR_SIZE)
    return off - STR_OFF if off >= 0 else None


def cstr_at(addr, n=80):
    b = read_mem(addr, n)
    return b.split(b"\x00")[0].decode("latin1", "replace") if b else None


# metadata base from a known class name
slot = BASE + 0x2C33650
cls = u64(u64(slot))
name_ptr = u64(cls + 0x10)
inj_off = meta_offset("InterfaceInjector")
meta_base = name_ptr - inj_off
print("pid", PID, "base", hex(BASE), "iface_class", hex(cls), "meta_base", hex(meta_base))

occurrences = []
st = STR_OFF
needle = b"PreFightScreen\x00"
while True:
    i = META.find(needle, st, STR_OFF + STR_SIZE)
    if i < 0:
        break
    occurrences.append(i - STR_OFF)
    st = i + 1
print("name offsets", [hex(x) for x in occurrences])
class_ptr = None
for off in occurrences:
    target_name_ptr = meta_base + off
    print("try name ptr", hex(target_name_ptr), "cstr", cstr_at(target_name_ptr))
    pat = struct.pack("<Q", target_name_ptr)
    for line in maps_text.splitlines():
        if "libil2cpp.so" not in line:
            continue
        start = int(line.split("-")[0], 16)
        end = int(line.split("-")[1].split()[0], 16)
        blob = read_mem(start, end - start)
        idx = blob.find(pat)
        if idx >= 0:
            hit = start + idx
            class_ptr = hit - 0x10
            print("name ptr at", hex(hit), "class", hex(class_ptr),
                  "verify", hex(u64(class_ptr + 0x10) or 0),
                  "name", cstr_at(u64(class_ptr + 0x10)))
            break
    if class_ptr:
        break
if not class_ptr:
    raise SystemExit("PreFightScreen class not found")
print("class", hex(class_ptr), "name", cstr_at(u64(class_ptr + 0x10)))

# scan rw-p anon/heap regions for objects whose first qword == class_ptr
pat = struct.pack("<Q", class_ptr)
found = []
for s, e, p, n in MAPS:
    if p != "rw-p":
        continue
    if "libil2cpp" in n or "/system/" in n or "/data/app/" in n:
        continue
    size = e - s
    if size <= 0 or size > 150 * 1024 * 1024:
        continue
    step = 4 * 1024 * 1024
    for off in range(0, size, step):
        nbytes = min(step, size - off)
        blob = read_mem(s + off, nbytes)
        if not blob:
            continue
        pos = 0
        while True:
            i = blob.find(pat, pos)
            if i < 0:
                break
            addr = s + off + i
            if addr % 8 == 0:
                found.append(addr)
            pos = i + 1

print("candidate PreFightScreen objects", len(found))
for a in found[:20]:
    print("obj", hex(a))
    for off in (0x80, 0x88, 0x90, 0x98, 0xA0, 0xA8, 0xA9):
        if off in (0xA8, 0xA9):
            print(f"  +{off:#x} byte", read_mem(a + off, 1).hex())
        else:
            v = u64(a + off)
            print(f"  +{off:#x} = {v:#x}" if v else f"  +{off:#x} = None")
