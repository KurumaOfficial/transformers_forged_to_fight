import sys, struct, re, json
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM

ROOT = r"."
SO = ROOT + r"\work\unpacked\lib\arm64-v8a\libil2cpp.so"
BIN = open(SO, 'rb').read()
LIT = {}
try:
    for _e in json.load(open(ROOT + r"\work\il2cpp_dump\stringliteral.json", encoding="utf-8")):
        LIT[int(_e["address"], 16)] = _e["value"]
except Exception as _ex:
    print("stringliteral load failed", _ex)
RVAMAP = {int(k): v for k, v in json.load(open(ROOT + r"\work\rva_map.json", encoding="utf-8")).items()}

e_phoff = struct.unpack_from('<Q', BIN, 32)[0]
e_phentsize = struct.unpack_from('<H', BIN, 54)[0]
e_phnum = struct.unpack_from('<H', BIN, 56)[0]
segs = []
for i in range(e_phnum):
    off = e_phoff + i * e_phentsize
    t, fl, fo, va, pa, fs, ms, al = struct.unpack_from('<IIQQQQQQ', BIN, off)
    if t == 1:
        segs.append((va, va + fs, fo, fs))
segs.sort()

def va_to_off(va):
    for start, end, off, fs in segs:
        if start <= va < end:
            return off + (va - start)
    return None

def read_va(va, n=64):
    off = va_to_off(va)
    if off is None:
        return None
    return BIN[off:off+n]

def decode_cstr(va, maxlen=200):
    b = read_va(va, maxlen)
    if not b:
        return None
    s = b.split(b'\x00')[0]
    try:
        return s.decode('utf-8')
    except Exception:
        return None

def decode_utf16(va, maxlen=400):
    b = read_va(va, maxlen)
    if not b:
        return None
    out = []
    for i in range(0, len(b) - 1, 2):
        c = b[i] | (b[i+1] << 8)
        if c == 0:
            break
        out.append(chr(c))
    s = ''.join(out)
    return s if s else None

def method_name(addr):
    v = RVAMAP.get(addr)
    if not v:
        return None
    return f"{v['class']}::{v['name']}"

md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
md.detail = True

def dump(start, length=0x400, strings=True):
    print(f"=== {start:#x} ===")
    code = read_va(start, length)
    if code is None:
        print("no code"); return
    regs = {}
    insns = list(md.disasm(code, start))
    for ins in insns:
        line = f"{ins.address:#x}: {ins.mnemonic:<8} {ins.op_str}"
        extra = ""
        if ins.mnemonic == 'adrp' and len(ins.operands) >= 2:
            try:
                reg = ins.reg_name(ins.operands[0].reg)
                imm = ins.operands[1].imm
                regs[reg] = imm
            except Exception:
                pass
        elif ins.mnemonic in ('add', 'ldr') and len(ins.operands) >= 2:
            try:
                dst = ins.reg_name(ins.operands[0].reg)
                src = ins.reg_name(ins.operands[1].reg)
                if src in regs:
                    base = regs[src]
                    if ins.mnemonic == 'add' and len(ins.operands) >= 3 and ins.operands[2].type == 2:
                        va = base + ins.operands[2].imm
                        if strings:
                            s1 = decode_cstr(va, 120)
                            s2 = decode_utf16(va, 240)
                            if s1 and all(32 <= ord(c) < 127 for c in s1) and len(s1) >= 2:
                                extra = f"  ; CSTR {s1!r}"
                            elif s2 and len(s2) >= 2:
                                extra = f"  ; UTF16 {s2!r}"
                    elif ins.mnemonic == 'ldr' and ins.operands[1].type == 3:
                        va = base + ins.operands[1].mem.disp
                        if va in LIT:
                            extra = f"  ; KEY {LIT[va]!r}"
                            regs[dst] = va
                        else:
                            off = va_to_off(va)
                            if off is not None:
                                ptr = struct.unpack_from('<Q', BIN, off)[0]
                                if ptr in LIT:
                                    extra = f"  ; PTR->KEY {LIT[ptr]!r}"
                                    regs[dst] = ptr
                                elif strings:
                                    s1 = decode_cstr(ptr, 120)
                                    s2 = decode_utf16(ptr, 240)
                                    if s1 and len(s1) >= 2 and all(32 <= ord(c) < 127 for c in s1):
                                        extra = f"  ; PTR->CSTR {s1!r}"
                                    elif s2 and len(s2) >= 2:
                                        extra = f"  ; PTR->UTF16 {s2!r}"
            except Exception:
                pass
        elif ins.mnemonic in ('bl', 'b') and ins.operands and ins.operands[0].type == 2:
            tgt = ins.operands[0].imm
            nm = method_name(tgt)
            if nm:
                extra = f"  ; -> {nm}"
        print(line + extra)

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        print("usage: disasm_calls.py <hexaddr> [len] [--nostrings]")
        sys.exit(1)
    start = int(args[0], 0)
    length = int(args[1], 0) if len(args) > 1 and not args[1].startswith('-') else 0x400
    dump(start, length, strings='--nostrings' not in args)
