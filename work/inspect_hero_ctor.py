import json, capstone, sys

sys.stdout.reconfigure(encoding='utf-8')
with open('work/unpacked/lib/arm64-v8a/libil2cpp.so', 'rb') as f:
    data = f.read()

with open('work/il2cpp_dump/stringliteral.json', 'r', encoding='utf-8') as f:
    strings = json.load(f)
s_map = {int(s['address'], 16): s['value'] for s in strings}

def resolve_ptr(addr):
    off = addr - 0x10000
    if 0 <= off < len(data) - 8:
        val = int.from_bytes(data[off:off+8], 'little')
        if val in s_map:
            return s_map[val]
    return f'0x{addr:x}'

def analyze_func(func_name, off, size=0x600):
    end_off = off + size
    print(f'=== {func_name} ({hex(off)} - {hex(end_off)}) ===')
    md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
    code = data[off : end_off]
    cur_adrp = {}
    cur_addr = {}
    found_keys = []
    for ins in md.disasm(code, off):
        if ins.mnemonic == 'adrp':
            reg = ins.op_str.split(',')[0].strip()
            page = int(ins.op_str.split(',')[1].strip().replace('#', ''), 16)
            cur_adrp[reg] = page
        elif ins.mnemonic == 'ldr':
            parts = [p.strip() for p in ins.op_str.split(',')]
            dst = parts[0]
            if len(parts) >= 2 and '[' in parts[1]:
                mem = parts[1].replace('[', '').replace(']', '').replace('!', '')
                reg = mem.split()[0]
                offset = 0
                if len(parts) > 2:
                    offset_str = parts[2].replace(']', '').replace('!', '').replace('#', '').strip()
                    try:
                        offset = int(offset_str, 16)
                    except Exception:
                        continue
                if reg in cur_adrp:
                    mem_addr = cur_adrp[reg] + offset
                    cur_addr[dst] = mem_addr
                    # Check if this memory address directly holds a string literal
                    name = resolve_ptr(mem_addr)
                    if name and not name.startswith('0x') and name not in found_keys:
                        # only add if reasonable identifier
                        found_keys.append(name)
                        print(f'  key: "{name}"')
        elif ins.mnemonic == 'ret':
            break

ctors = [
    ('BCGEvoBlueprintBase..ctor', 0xC182F0),
    ('BCGStatModifierAppearance..ctor', 0xA5F51C),
    ('BCGHeroBase..ctor', 0xC21AC4),
    ('BCGHeroBaseCommon..ctor', 0xC21EA0),
    ('TFBCGBlueprintBase..ctor', 0xB030A8),
    ('BCGBlueprintBase..ctor', 0xC1C320),
    ('TFBCGCharacterData..ctor', 0xB034E4),
    ('BCGCharacterData..ctor', 0xC175E4),
    ('BCGSynergyBonus..ctor', 0xA5FD38),
    ('BCGAttackValue..ctor', 0xC145BC),
    ('BCGBlueprintBonuses..ctor', 0xC17490),
    ('BCGStaminaRegen..ctor', 0xA5DB18),
    ('BCGEvoCosts..ctor', 0xC19EFC),
    ('BCGCurve..ctor', 0xC17C98)
]

for name, addr in ctors:
    analyze_func(name, addr)
