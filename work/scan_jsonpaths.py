import sys, re, struct
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM

ROOT = r"."
SO = ROOT + r"\work\unpacked\lib\arm64-v8a\libil2cpp.so"
BIN = open(SO, 'rb').read()

# JSONPaths TypeDefIndex 7516 field -> offset
lines = open(ROOT + r"\work\il2cpp_dump\dump.cs", encoding="utf-8", errors="replace").read().splitlines()
start = None
for i, l in enumerate(lines):
    if "public static class JSONPaths // TypeDefIndex: 7516" in l:
        start = i
        break
path_names = {}
for l in lines[start:start + 900]:
    m = re.search(r"JSONPath (\w+); // 0x([0-9A-Fa-f]+)", l)
    if m:
        path_names[int(m.group(2), 16)] = m.group(1)

e_phoff = struct.unpack_from('<Q', BIN, 32)[0]
e_phentsize = struct.unpack_from('<H', BIN, 54)[0]
e_phnum = struct.unpack_from('<H', BIN, 56)[0]
segs = []
for i in range(e_phnum):
    off = e_phoff + i * e_phentsize
    t, fl, fo, va, pa, fs, ms, al = struct.unpack_from('<IIQQQQQQ', BIN, off)
    if t == 1:
        segs.append((va, va + fs, fo, fs))

def read_va(va, n):
    for s, e, off, fs in segs:
        if s <= va < e:
            return BIN[off + (va - s): off + (va - s) + n]
    return None

md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
md.detail = True

def norm(imm):
    for d in (0, 8, 0x10):
        if (imm - d) % 0x18 == 0:
            return imm - d
    return None

def scan(start_va, length):
    code = read_va(start_va, length)
    if not code:
        return
    seen = []
    for ins in md.disasm(code, start_va):
        if ins.mnemonic in ('ldr', 'ldur') and len(ins.operands) >= 2 and ins.operands[1].type == 3:
            mem = ins.operands[1].mem
            base = ins.reg_name(mem.base)
            if base == 'x8':
                off = mem.disp
                key = norm(off)
                if key is not None and key not in seen:
                    seen.append(key)
        if ins.mnemonic in ('ret', 'b') and ins.address > start_va:
            # crude end; keep going anyway
            pass
    for off in seen:
        print(f"  {off:#06x}  {path_names.get(off, '??')}")

if __name__ == '__main__':
    start_va = int(sys.argv[1], 0)
    length = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x400
    print(f"=== {start_va:#x} len {length:#x} ===")
    scan(start_va, length)
