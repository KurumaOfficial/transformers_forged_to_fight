import capstone

ELF_PATH = 'work/unpacked/lib/arm64-v8a/libil2cpp.so'
with open(ELF_PATH, 'rb') as f:
    elf_data = f.read()

md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)

print("=== BaseSubManager$$DeserializeData (0x173511C) ===")
code = elf_data[0x173511C : 0x173511C + 500]
for insn in md.disasm(code, 0x173511C):
    print(f"0x{insn.address:X}:  {insn.mnemonic:8s} {insn.op_str}")
