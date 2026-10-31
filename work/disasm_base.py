import capstone
import struct

ELF_PATH = 'work/unpacked/lib/arm64-v8a/libil2cpp.so'

with open(ELF_PATH, 'rb') as f:
    elf_data = f.read()

md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)

def disassemble_func(rva, size=200):
    code = elf_data[rva : rva + size]
    disasm = []
    for insn in md.disasm(code, rva):
        disasm.append(f"0x{insn.address:X}:  {insn.mnemonic:8s} {insn.op_str}")
    return disasm

print("=== BaseManager$$Connect (0x173407C) ===")
for line in disassemble_func(0x173407C, 256)[:30]:
    print(line)

print("\n=== BaseManager$$DeserializeData (0x17343F8) ===")
for line in disassemble_func(0x17343F8, 300)[:40]:
    print(line)
