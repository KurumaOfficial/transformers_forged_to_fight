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
    return f'unknown(addr={hex(addr)})'

md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
off = 0x168C7C4
end_off = 0x1690500
code = data[off : end_off]

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
        if target == '0x1451998': # EB.Dot.Object
            addr = cur_addr.get('x8', cur_addr.get('x0', 0))
            name = resolve_ptr(addr)
            print(f'EB.Dot.Object at {hex(ins.address)}: "{name}"')
        elif target == '0x144f534': # EB.Dot.String
            addr = cur_addr.get('x9', cur_addr.get('x0', 0))
            name = resolve_ptr(addr)
            print(f'EB.Dot.String at {hex(ins.address)}: "{name}"')
        elif target in ('0x1455c68', '0x145fea8'): # EB.Dot.Integer
            addr = cur_addr.get('x8', cur_addr.get('x0', 0))
            name = resolve_ptr(addr)
            print(f'EB.Dot.Integer at {hex(ins.address)}: "{name}"')
        elif target == '0x1455ca8': # EB.Dot.Single
            addr = cur_addr.get('x8', cur_addr.get('x0', 0))
            name = resolve_ptr(addr)
            print(f'EB.Dot.Single at {hex(ins.address)}: "{name}"')
