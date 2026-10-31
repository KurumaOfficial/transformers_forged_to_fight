import struct
import json

ELF_PATH = 'work/unpacked/lib/arm64-v8a/libil2cpp.so'
with open(ELF_PATH, 'rb') as f:
    elf_data = f.read()

with open('work/il2cpp_dump/script.json', 'r', encoding='utf-8') as f:
    script = json.load(f)

methods = script.get('ScriptMethod', [])
methods.sort(key=lambda x: x['Address'])

def find_method_for_addr(pc):
    lo = 0
    hi = len(methods) - 1
    best = None
    while lo <= hi:
        mid = (lo + hi) // 2
        if methods[mid]['Address'] <= pc:
            best = methods[mid]
            lo = mid + 1
        else:
            hi = mid - 1
    return best

TARGET = 0xFC0734 # Hub.FatalError

callers = []
for pc in range(0, len(elf_data) - 4, 4):
    insn = struct.unpack('<I', elf_data[pc:pc+4])[0]
    # BL opcode: 0x94000000
    if (insn & 0xFC000000) == 0x94000000:
        imm26 = insn & 0x03FFFFFF
        if imm26 & (1 << 25):
            imm26 -= (1 << 26)
        dest = pc + (imm26 << 2)
        if dest == TARGET:
            m = find_method_for_addr(pc)
            m_name = m['Name'] if m else 'Unknown'
            m_addr = m['Address'] if m else 0
            callers.append((pc, m_addr, m_name))

print(f"Total callers of Hub.FatalError (0x{TARGET:X}): {len(callers)}")
for pc, m_addr, m_name in callers:
    print(f"  At 0x{pc:X} in method 0x{m_addr:X} ({m_name})")
