from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM
import json
import struct

with open("work/il2cpp_dump/script.json", "r", encoding="utf-8") as f:
    data = json.load(f)

methods = data.get("ScriptMethod", [])
by_name = {m["Name"]: m["Address"] for m in methods}

# Find EB.Sparx.Config..ctor
cfg_ctor = by_name.get("EB.Sparx.Config$$.ctor")
print(f"EB.Sparx.Config..ctor: {hex(cfg_ctor) if cfg_ctor else 'Not found'}")

with open("work/unpacked/lib/arm64-v8a/libil2cpp.so", "rb") as f:
    lib = f.read()

# Let's search for BL to cfg_ctor
if cfg_ctor:
    for pc in range(0, len(lib)-4, 4):
        instr = struct.unpack("<I", lib[pc:pc+4])[0]
        if (instr & 0xFC000000) == 0x94000000:
            imm26 = instr & 0x03FFFFFF
            if imm26 & 0x02000000:
                imm26 -= 0x04000000
            dest = pc + (imm26 << 2)
            if dest == cfg_ctor:
                print(f"Caller of Config..ctor at: {hex(pc)}")
