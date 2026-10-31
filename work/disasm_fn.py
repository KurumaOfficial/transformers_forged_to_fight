"""Disassemble one function from libil2cpp.so.

Usage: python work/disasm_fn.py 0xE38E24 [0xE39078]
If end is omitted, the next RVA in work/rva_map.json is used.
"""
import json
import struct
import sys
from pathlib import Path

from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM

ROOT = Path(r".")
BIN = (ROOT / "work" / "unpacked" / "lib" / "arm64-v8a" / "libil2cpp.so").read_bytes()
RVA = {int(k): v for k, v in json.loads((ROOT / "work" / "rva_map.json").read_text(encoding="utf-8")).items()}

segs = []
e_phoff = struct.unpack_from("<Q", BIN, 32)[0]
e_phentsize = struct.unpack_from("<H", BIN, 54)[0]
e_phnum = struct.unpack_from("<H", BIN, 56)[0]
for i in range(e_phnum):
    off = e_phoff + i * e_phentsize
    t, fl, fo, va, pa, fs, ms, al = struct.unpack_from("<IIQQQQQQ", BIN, off)
    if t == 1 and (fl & 1):
        segs.append((va, fo, fs))


def file_off(va):
    for sva, sfo, sfs in segs:
        if sva <= va < sva + sfs:
            return sfo + (va - sva)
    return None


def name_at(va):
    v = RVA.get(va)
    if v:
        return f"{v['class']}::{v['name']}"
    return None


def main():
    start = int(sys.argv[1], 16)
    if len(sys.argv) > 2:
        end = int(sys.argv[2], 16)
    else:
        keys = sorted(k for k in RVA if k > start)
        end = keys[0] if keys else start + 0x200
    off = file_off(start)
    code = BIN[off:off + (end - start)]
    md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    md.detail = False
    print(f"; {start:#x}..{end:#x}  ({name_at(start)})")
    for ins in md.disasm(code, start):
        extra = ""
        if ins.mnemonic in ("bl", "b") and ins.op_str.startswith("#"):
            tgt = int(ins.op_str[1:], 16)
            n = name_at(tgt)
            if n:
                extra = f"  ; {n}"
        print(f"{ins.address:#08x}: {ins.mnemonic:8s} {ins.op_str}{extra}")


if __name__ == "__main__":
    main()
