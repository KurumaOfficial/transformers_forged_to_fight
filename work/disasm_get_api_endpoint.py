from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM

cs = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
addr = 0x1c077b0
with open("work/unpacked/lib/arm64-v8a/libil2cpp.so", "rb") as f:
    f.seek(addr)
    code = f.read(500)

for i in cs.disasm(code, addr):
    print(f"0x{i.address:x}: {i.mnemonic:8s} {i.op_str}")
    if i.mnemonic == "ret":
        break
