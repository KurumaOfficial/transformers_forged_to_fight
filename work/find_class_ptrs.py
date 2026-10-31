import struct
from pathlib import Path
elf_path = Path(r".\work\unpacked\lib\arm64-v8a\libil2cpp.so")
b = elf_path.read_bytes()
e_phoff = struct.unpack_from("<Q", b, 32)[0]
e_phentsize = struct.unpack_from("<H", b, 54)[0]
e_phnum = struct.unpack_from("<H", b, 56)[0]
segs = []
for i in range(e_phnum):
    o = e_phoff + i * e_phentsize
    t, fl, fo, va, pa, fs, ms, al = struct.unpack_from("<IIQQQQQQ", b, o)
    if t == 1:
        segs.append((fo, fo + fs, va, fl))

def off_to_va(off):
    for fo, fe, va, fl in segs:
        if fo <= off < fe:
            return va + (off - fo)
    return None

def va_to_off(va):
    for fo, fe, sva, fl in segs:
        if sva <= va < sva + (fe - fo):
            return fo + (va - sva)
    return None

for name in [b"TeamData", b"PrefightScreenData", b"BCGUserActiveTeam", b"HeroData"]:
    print("###", name.decode())
    start = 0
    found = []
    while True:
        i = b.find(name, start)
        if i < 0:
            break
        va = off_to_va(i)
        found.append((i, va))
        start = i + 1
    print("string candidates", [(off, hex(va) if va else None) for off, va in found[:10]])
    for off, va in found[:5]:
        if not va:
            continue
        needle = struct.pack("<Q", va)
        ptrs = []
        j = 0
        while True:
            j = b.find(needle, j)
            if j < 0:
                break
            pva = off_to_va(j)
            ptrs.append((j, pva))
            j += 1
        print("  va", hex(va), "ptr refs", len(ptrs), [(hex(o), hex(v) if v else None) for o, v in ptrs[:8]])
