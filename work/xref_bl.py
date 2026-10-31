import struct, json, bisect, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"."
BIN = open(ROOT + r"\work\unpacked\lib\arm64-v8a\libil2cpp.so", "rb").read()
m = json.load(open(ROOT + r"\work\rva_map.json", encoding="utf-8"))
ks = sorted((int(k), v) for k, v in m.items())
a = [k for k, _ in ks]

def containing(addr):
    i = bisect.bisect_right(a, addr) - 1
    if i < 0:
        return None
    k, v = ks[i]
    if addr - k > 0x20000:
        return None
    return k, v

# ELF program headers
e_phoff = struct.unpack_from("<Q", BIN, 32)[0]
e_phentsize = struct.unpack_from("<H", BIN, 54)[0]
e_phnum = struct.unpack_from("<H", BIN, 56)[0]
segs = []
for i in range(e_phnum):
    off = e_phoff + i * e_phentsize
    t, fl, fo, va, pa, fs, ms, al = struct.unpack_from("<IIQQQQQQ", BIN, off)
    if t == 1 and (fl & 1):
        segs.append((va, fo, fs))
targets = [int(x, 0) for x in sys.argv[1:]]
for target in targets:
    print(f"target {target:#x}")
    found = []
    for va, fo, fs in segs:
        code = BIN[fo:fo + fs]
        for i in range(0, len(code) - 3, 4):
            insn = struct.unpack_from("<I", code, i)[0]
            if (insn & 0xFC000000) != 0x94000000:
                continue
            imm = insn & 0x03FFFFFF
            if imm & (1 << 25):
                imm -= (1 << 26)
            dest = va + i + (imm << 2)
            if dest == target:
                found.append(va + i)
    for pc in sorted(found):
        c = containing(pc)
        if c:
            k, v = c
            print(f"  from {pc:#x}  {v['class']}::{v['name']} +{pc-k:#x}")
        else:
            print(f"  from {pc:#x}  ?")
    print("count", len(found))
