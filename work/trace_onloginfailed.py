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
off = 0x102B1A8
end_off = 0x102B928
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
                name = resolve_ptr(mem_addr)
                if not name.startswith('0x'):
                    print(f'{hex(ins.address)}: ldr {dst} -> "{name}"')
    elif ins.mnemonic in ('cbz', 'cbnz', 'b.eq', 'b.ne'):
        # branching
        pass
    elif ins.mnemonic == 'bl':
        target = ins.op_str.replace('#', '').strip()
        # check if string formatting or comparison
        addr = cur_addr.get('x1', cur_addr.get('x0', 0))
        name = resolve_ptr(addr)
        if not name.startswith('0x'):
            print(f'  bl at {hex(ins.address)} -> {target} with "{name}"')
