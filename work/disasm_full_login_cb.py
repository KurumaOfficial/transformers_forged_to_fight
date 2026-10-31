import capstone

cs = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
with open('work/unpacked/lib/arm64-v8a/libil2cpp.so', 'rb') as f:
    so = f.read()

start = 0x1628440
code = so[start : start + 0x300]

for i in cs.disasm(code, start):
    branch_info = ""
    if i.mnemonic.startswith('cbz') or i.mnemonic.startswith('b'):
        branch_info = f" -> {i.op_str}"
    print(f"0x{i.address:x}: {i.mnemonic:8s} {i.op_str:30s} {branch_info}")
