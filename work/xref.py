import sys, struct, json
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM

ROOT = r"."
SO = ROOT + r"\work\unpacked\lib\arm64-v8a\libil2cpp.so"
BIN = open(SO, 'rb').read()
RVAMAP = {int(k): v for k, v in json.load(open(ROOT + r"\work\rva_map.json", encoding="utf-8")).items()}

targets = set(int(x, 0) for x in sys.argv[1:])
if not targets:
    print("usage: xref.py <addr> [addr...]")
    sys.exit(1)

e_phoff = struct.unpack_from('<Q', BIN, 32)[0]
e_phentsize = struct.unpack_from('<H', BIN, 54)[0]
e_phnum = struct.unpack_from('<H', BIN, 56)[0]
segs = []
for i in range(e_phnum):
    off = e_phoff + i * e_phentsize
    t, fl, fo, va, pa, fs, ms, al = struct.unpack_from('<IIQQQQQQ', BIN, off)
    if t == 1 and (fl & 1):  # executable
        segs.append((va, va + fs, fo, fs))

md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
md.detail = True
md.skipdata = True
found = {}
for va, end, off, fs in segs:
    code = BIN[off:off + fs]
    for ins in md.disasm(code, va):
        if ins.mnemonic in ('bl', 'b') and ins.operands and ins.operands[0].type == 2:
            tgt = ins.operands[0].imm
            if tgt in targets:
                found.setdefault(tgt, []).append(ins.address)
for t in sorted(targets):
    print(f"target {t:#x}:")
    for a in found.get(t, []):
        v = RVAMAP.get(a)
        name = f"{v['class']}::{v['name']}" if v else "?"
        print(f"  from {a:#x}  {name}")
