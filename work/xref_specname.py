import json
import struct

ROOT = r"."
BIN = open(ROOT + r"\work\unpacked\lib\arm64-v8a\libil2cpp.so", "rb").read()
RVAMAP = {int(k): v for k, v in json.load(open(ROOT + r"\work\rva_map.json", encoding="utf-8")).items()}

e_phoff = struct.unpack_from("<Q", BIN, 32)[0]
e_phentsize = struct.unpack_from("<H", BIN, 54)[0]
e_phnum = struct.unpack_from("<H", BIN, 56)[0]
segs = []
for i in range(e_phnum):
    off = e_phoff + i * e_phentsize
    t, fl, fo, va, pa, fs, ms, al = struct.unpack_from("<IIQQQQQQ", BIN, off)
    if t == 1 and (fl & 1):
        segs.append((va, fo, fs))

targets = {0xC1B154, 0xC1B21C}
for va, fo, fs in segs:
    for off in range(0, fs - 4, 4):
        w = struct.unpack_from("<I", BIN, fo + off)[0]
        if (w & 0xFC000000) == 0x94000000:
            pc = va + off
            imm = w & 0x03FFFFFF
            if imm & 0x02000000:
                imm -= 0x04000000
            tgt = pc + (imm << 2)
            if tgt in targets:
                v = RVAMAP.get(pc)
                name = f"{v['class']}::{v['name']}" if v else "?"
                print(f"target {tgt:#x} <- {pc:#x} {name}")
