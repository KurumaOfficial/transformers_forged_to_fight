from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM
import struct

cs = Cs(CS_ARCH_ARM64, CS_MODE_ARM)

with open("work/unpacked/lib/arm64-v8a/libil2cpp.so", "rb") as f:
    lib = f.read()

targets = [0x1236dc4, 0x1236d54]

# Search for BL / B instructions calling targets
import re

for target in targets:
    print(f"\nSearching callers of 0x{target:x}...")
    # BL instruction encoding: op=0x94000000 | (imm26 & 0x3FFFFFF)
    # diff = (target - pc) >> 2
    # Let's search by capstone or direct formula
    callers = []
    for pc in range(0, len(lib)-4, 4):
        instr = struct.unpack("<I", lib[pc:pc+4])[0]
        # check if bl
        if (instr & 0xFC000000) == 0x94000000:
            imm26 = instr & 0x03FFFFFF
            if imm26 & 0x02000000:
                imm26 -= 0x04000000
            dest = pc + (imm26 << 2)
            if dest == target:
                callers.append(pc)
    print(f"Found {len(callers)} callers:")
    for c in callers:
        print(f"  Caller at 0x{c:x}")
