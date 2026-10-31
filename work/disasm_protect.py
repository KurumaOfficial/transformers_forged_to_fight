from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM
import json

cs = Cs(CS_ARCH_ARM64, CS_MODE_ARM)

with open("work/il2cpp_dump/script.json", "r", encoding="utf-8") as f:
    data = json.load(f)

methods = data.get("ScriptMethod", [])
by_name = {m["Name"]: m["Address"] for m in methods}

protect_methods = [
    "EB.Sparx.Protect$$BuildLoginData",
    "EB.Sparx.Protect$$CalculateSha1",
    "EB.Sparx.Protect$$CalculateHmac",
    "EB.Sparx.Protect$$GetNativeLibrarySignature"
]

with open("work/unpacked/lib/arm64-v8a/libil2cpp.so", "rb") as f:
    for name in protect_methods:
        addr = by_name.get(name)
        if not addr:
            print(f"Method {name} not found!")
            continue
        print(f"\n==========================================")
        print(f"{name} @ 0x{addr:x}")
        f.seek(addr)
        code = f.read(512)
        count = 0
        for i in cs.disasm(code, addr):
            print(f"  0x{i.address:x}: {i.mnemonic:8s} {i.op_str}")
            count += 1
            if i.mnemonic == "ret" or count > 50:
                break
