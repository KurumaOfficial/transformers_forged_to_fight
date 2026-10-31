import capstone

cs = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
cs.detail = True
with open('work/unpacked/lib/arm64-v8a/libil2cpp.so', 'rb') as f:
    f.seek(0x103adfc)
    code = f.read(0x10)

for insn in cs.disasm(code, 0x103adfc):
    print(f'0x{insn.address:x}: {insn.mnemonic} {insn.op_str}')
    for op in insn.operands:
        if op.type == capstone.arm64.ARM64_OP_IMM:
            print(f'  imm: 0x{op.imm:x}')
        elif op.type == capstone.arm64.ARM64_OP_MEM:
            print(f'  mem: base={op.mem.base}, disp=0x{op.mem.disp:x}')
