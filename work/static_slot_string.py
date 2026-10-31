import struct
import sys
from pathlib import Path

ROOT = Path(r".")
ELF = (ROOT / "work" / "unpacked" / "lib" / "arm64-v8a" / "libil2cpp.so").read_bytes()
META = (ROOT / "work" / "unpacked" / "assets" / "bin" / "Data" / "Managed" /
        "Metadata" / "global-metadata.dat").read_bytes()

e_phoff = struct.unpack_from("<Q", ELF, 32)[0]
e_phentsize = struct.unpack_from("<H", ELF, 54)[0]
e_phnum = struct.unpack_from("<H", ELF, 56)[0]
segs = []
for i in range(e_phnum):
    o = e_phoff + i * e_phentsize
    t, fl, fo, va, pa, fs, ms, al = struct.unpack_from("<IIQQQQQQ", ELF, o)
    if t == 1:
        segs.append((va, fo, fs))

sl_off, sl_cnt, sl_data_off = struct.unpack_from("<iii", META, 0x08)


def file_at(va):
    for v, o, sz in segs:
        if v <= va < v + sz:
            return o + (va - v)
    return None


def lit(index):
    if index < 0 or index >= sl_cnt // 8:
        return None
    ln, di = struct.unpack_from("<II", META, sl_off + index * 8)
    return META[sl_data_off + di:sl_data_off + di + ln].decode("utf-8", "replace")


def resolve(slot):
    off = file_at(slot)
    if off is None:
        return None
    q = struct.unpack_from("<Q", ELF, off)[0]
    if 0xA0000000 <= q <= 0xBFFFFFFF:
        return lit((q & 0x1FFFFFFF) >> 1)
    # Sometimes the slot holds a pointer to a metadata usage cell. Try one deref.
    off2 = file_at(q)
    if off2 is not None:
        q2 = struct.unpack_from("<Q", ELF, off2)[0]
        if 0xA0000000 <= q2 <= 0xBFFFFFFF:
            return lit((q2 & 0x1FFFFFFF) >> 1)
    return None


for arg in sys.argv[1:]:
    va = int(arg, 16)
    print(hex(va), repr(resolve(va)))
