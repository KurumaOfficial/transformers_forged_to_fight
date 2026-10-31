from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM
import json

cs = Cs(CS_ARCH_ARM64, CS_MODE_ARM)

with open("work/il2cpp_dump/script.json", "r", encoding="utf-8") as f:
    data = json.load(f)

methods = data.get("ScriptMethod", [])
by_name = {m["Name"]: m["Address"] for m in methods}

with open("work/unpacked/lib/arm64-v8a/libil2cpp.so", "rb") as f:
    lib = f.read()

targets = [
    "EB.Sparx.LoginManager$$HandlePreLoginData",
    "EB.Sparx.LoginManager$$_PostLogin",
    "EB.Sparx.LoginManager$$_Authorize",
    "EB.Sparx.LoginManager$$_PostInit"
]

for t in targets:
    addr = by_name.get(t)
    print(f"\n==========================================")
    print(f"{t} @ {hex(addr) if addr else 'Not found'}")
    if addr:
        code = lib[addr:addr+200]
        for i in cs.disasm(code, addr):
            print(f"  0x{i.address:x}: {i.mnemonic:8s} {i.op_str}")
            if i.mnemonic == 'ret':
                break
