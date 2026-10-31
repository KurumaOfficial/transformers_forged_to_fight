import struct

ELF_PATH = 'work/unpacked/lib/arm64-v8a/libil2cpp.so'
with open(ELF_PATH, 'rb') as f:
    elf_data = f.read()

import json
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

def find_xrefs(target):
    target_page = target & ~0xFFF
    target_off = target & 0xFFF
    results = []
    # Search for ADRP instructions
    for pc in range(0, len(elf_data) - 4, 4):
        insn = struct.unpack('<I', elf_data[pc:pc+4])[0]
        # ADRP opcode: [1:bit31] [immlo:2] 10000 [immhi:19] [Rd:5]
        if (insn & 0x9F000000) == 0x90000000:
            rd = insn & 0x1F
            immlo = (insn >> 29) & 3
            immhi = (insn >> 5) & 0x7FFFF
            imm = (immhi << 2) | immlo
            if imm & (1 << 20):
                imm -= (1 << 21)
            page = (pc & ~0xFFF) + (imm << 12)
            if page == target_page:
                # Check next few instructions for LDR or ADD using rd
                for step in range(1, 4):
                    next_pc = pc + step * 4
                    if next_pc >= len(elf_data): break
                    next_insn = struct.unpack('<I', elf_data[next_pc:next_pc+4])[0]
                    # ADD (immediate): [31:0] 00 100010 [shift:2] [imm12:12] [Rn:5] [Rd:5]
                    if (next_insn & 0x7F800000) == 0x11000000:
                        rn = (next_insn >> 5) & 0x1F
                        imm12 = (next_insn >> 10) & 0xFFF
                        if rn == rd and imm12 == target_off:
                            results.append((pc, next_pc, "ADD"))
                    # LDR (literal/imm): [31:0] 11 111 0 01 [size] [imm12] [Rn:5] [Rt:5]
                    # 64-bit LDR unsigned: 0xF9400000
                    if (next_insn & 0xFFC00000) == 0xF9400000:
                        rn = (next_insn >> 5) & 0x1F
                        imm12 = ((next_insn >> 10) & 0xFFF) * 8
                        if rn == rd and imm12 == target_off:
                            results.append((pc, next_pc, "LDR"))
    return results

targets = [
    (0x2D6B810, "Unexpected: no BaseSubManager for local user"),
    (0x2D59D80, "Could not fetch the user's base from the server"),
    (0x2D7AC80, "uid {0} has no base"),
    (0x2D6DCA8, "[SparxHub] Sparx Fatal Error: ")
]

for tgt, label in targets:
    print(f"\n--- Xrefs for {label} (0x{tgt:X}) ---")
    xrefs = find_xrefs(tgt)
    for adrp_pc, use_pc, op in xrefs:
        m = find_method_for_addr(adrp_pc)
        m_name = m['Name'] if m else 'Unknown'
        m_addr = m['Address'] if m else 0
        print(f"  At 0x{use_pc:X} ({op}) in method 0x{m_addr:X} ({m_name})")
