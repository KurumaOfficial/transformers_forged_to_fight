from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM
import json
import struct

cs = Cs(CS_ARCH_ARM64, CS_MODE_ARM)

with open("work/il2cpp_dump/script.json", "r", encoding="utf-8") as f:
    data = json.load(f)

methods = data.get("ScriptMethod", [])
by_name = {m["Name"]: m["Address"] for m in methods}

with open("work/il2cpp_dump/stringliteral.json", "r", encoding="utf-8") as f:
    literals = json.load(f)
lit_by_addr = {int(l["address"], 16): l["value"] for l in literals if "address" in l}

with open("work/unpacked/lib/arm64-v8a/libil2cpp.so", "rb") as f:
    lib = f.read()

def read_u64(addr):
    if 0 <= addr < len(lib) - 8:
        return struct.unpack("<Q", lib[addr:addr+8])[0]
    return 0

targets = [
    ("LoginAPI$$Init", by_name.get("EB.Sparx.LoginAPI$$Init")),
    ("LoginAPI$$PreLogin", by_name.get("EB.Sparx.LoginAPI$$PreLogin")),
    ("LoginAPI$$Login", by_name.get("EB.Sparx.LoginAPI$$Login")),
    ("LoginAPI$$AddData", by_name.get("EB.Sparx.LoginAPI$$AddData")),
    ("LoginAPI$$ExchangeLoginToken", by_name.get("EB.Sparx.LoginAPI$$ExchangeLoginToken")),
    ("LoginAPI$$LoginData", by_name.get("EB.Sparx.LoginAPI$$LoginData")),
]

for name, addr in targets:
    if not addr:
        print(f"Target {name} not found!")
        continue
    print(f"\n==========================================")
    print(f"{name} @ 0x{addr:x}")
    code = lib[addr:addr+400]
    for i in cs.disasm(code, addr):
        # check if it references literal or adrp
        print(f"  0x{i.address:x}: {i.mnemonic:8s} {i.op_str}")
        if i.mnemonic == "ret":
            break
