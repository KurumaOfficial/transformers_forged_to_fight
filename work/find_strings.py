import json, struct, capstone

with open('work/il2cpp_dump/stringliteral.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

addr2str = {int(x['address'], 16): x['value'] for x in items}

with open('work/unpacked/lib/arm64-v8a/libil2cpp.so', 'rb') as f:
    so_data = f.read()

rva = 0x12FA8B4
md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
code = so_data[rva:0x12FAEF0]

cur_adrp = {}
for ins in md.disasm(code, rva):
    if ins.mnemonic == 'adrp':
        reg = ins.op_str.split(',')[0].strip()
        imm = int(ins.op_str.split(',')[1].strip().replace('#', ''), 16)
        cur_adrp[reg] = imm
    elif ins.mnemonic == 'ldr':
        parts = ins.op_str.split(',')
        if len(parts) == 2 and '[' in parts[1]:
            dst = parts[0].strip()
            src = parts[1].replace('[', '').replace(']', '').split('#')
            base_reg = src[0].strip()
            offset = int(src[1].strip(), 16) if len(src) > 1 else 0
            if base_reg in cur_adrp:
                target_ptr = cur_adrp[base_reg] + offset
                if target_ptr + 8 <= len(so_data):
                    val = struct.unpack('<Q', so_data[target_ptr:target_ptr+8])[0]
                    if val in addr2str:
                        s = ascii(addr2str[val])
                        print(f'0x{ins.address:x}: loads string {s}')
