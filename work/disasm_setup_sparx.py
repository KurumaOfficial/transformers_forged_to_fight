from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM

cs = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
addr = 0xa2c84c
with open("work/unpacked/lib/arm64-v8a/libil2cpp.so", "rb") as f:
    f.seek(addr)
    code = f.read(1000)

for i in cs.disasm(code, addr):
    print(f"0x{i.address:x}: {i.mnemonic:8s} {i.op_str}")
    if i.mnemonic == "ret":
        break
