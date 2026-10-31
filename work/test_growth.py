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

md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
off = 0xC154F0
code = data[off : off + 0x130]

cur_adrp = {}
cur_addr = {}
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
    elif ins.mnemonic == 'bl':
        target = ins.op_str.replace('#', '').strip()
        addr0 = cur_addr.get('x0', 0)
        addr8 = cur_addr.get('x8', 0)
        s0 = resolve_ptr(addr0)
        s8 = resolve_ptr(addr8)
        if not s0.startswith('0x'):
            print(f'bl at {hex(ins.address)} -> {target}, x0="{s0}"')
        elif not s8.startswith('0x'):
            print(f'bl at {hex(ins.address)} -> {target}, x8="{s8}"')
