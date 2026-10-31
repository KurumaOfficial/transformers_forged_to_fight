from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM
import struct

cs = Cs(CS_ARCH_ARM64, CS_MODE_ARM)

with open("work/unpacked/lib/arm64-v8a/libil2cpp.so", "rb") as f:
    lib = f.read()

def read_u64(addr):
    if 0 <= addr < len(lib) - 8:
        return struct.unpack("<Q", lib[addr:addr+8])[0]
    return 0

def get_il2cpp_string(ptr):
    # string object: class_ptr (8), monitor (8), length (4), chars (2*length)
    if ptr <= 0 or ptr + 20 >= len(lib):
        return None
    length = struct.unpack("<I", lib[ptr+16:ptr+20])[0]
    if 0 < length < 256 and ptr + 20 + length*2 <= len(lib):
        try:
            return lib[ptr+20:ptr+20+length*2].decode('utf-16le')
        except:
            return None
    return None

# Disassemble LoginAPI range: 0x14682c4 to 0x146bf00
start_addr = 0x14682c4
end_addr = 0x146bf00
code = lib[start_addr:end_addr]

current_regs = {}
for i in cs.disasm(code, start_addr):
    # track adrp / ldr
    if i.mnemonic == 'adrp':
        reg = i.op_str.split(',')[0].strip()
        imm = int(i.op_str.split('#')[1].strip(), 16)
        current_regs[reg] = imm
    elif i.mnemonic == 'ldr':
        # ldr reg, [base, #offset]
        parts = [p.strip() for p in i.op_str.split(',')]
        if len(parts) == 2 and '[' in parts[1]:
            reg = parts[0]
            inside = parts[1].replace('[', '').replace(']', '')
            in_parts = [p.strip() for p in inside.split(',')]
            base = in_parts[0]
            offset = int(in_parts[1].replace('#', ''), 16) if len(in_parts) > 1 else 0
            if base in current_regs:
                ptr_addr = current_regs[base] + offset
                val = read_u64(ptr_addr)
                current_regs[reg] = val
                st = get_il2cpp_string(val)
                if st:
                    current_regs[reg + "_str"] = st
    elif i.mnemonic in ('bl', 'b'):
        target = i.op_str.replace('#', '')
        try:
            target_addr = int(target, 16)
            if target_addr in (0x1468858, 0x14688a0): # Post or Get
                method = "POST" if target_addr == 0x1468858 else "GET"
                path_str = current_regs.get("x1_str", "<unknown>")
                print(f"0x{i.address:x}: {method} {path_str!r} (x1=0x{current_regs.get('x1', 0):x})")
        except:
            pass
