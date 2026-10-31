from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM
import struct

cs = Cs(CS_ARCH_ARM64, CS_MODE_ARM)

# Find JNI_OnLoad in libapkprotect.so (arm64-v8a)
path = 'work/unpacked/lib/arm64-v8a/libapkprotect.so'
with open(path, 'rb') as f:
    data = f.read()

# Let's parse ELF64 to find symbol JNI_OnLoad
# ELF header: e_shoff at 40
e_shoff = struct.unpack('<Q', data[40:48])[0]
e_shentsize = struct.unpack('<H', data[58:60])[0]
e_shnum = struct.unpack('<H', data[60:62])[0]
e_shstrndx = struct.unpack('<H', data[62:64])[0]

# Read section headers
sections = []
for i in range(e_shnum):
    sh = data[e_shoff + i*e_shentsize : e_shoff + (i+1)*e_shentsize]
    sh_name, sh_type, sh_flags, sh_addr, sh_offset, sh_size, sh_link, sh_info, sh_addralign, sh_entsize = struct.unpack('<IIQQQQIIQQ', sh)
    sections.append({
        'name_idx': sh_name, 'type': sh_type, 'addr': sh_addr, 'offset': sh_offset, 'size': sh_size,
        'link': sh_link, 'info': sh_info, 'entsize': sh_entsize
    })

shstr = data[sections[e_shstrndx]['offset'] : sections[e_shstrndx]['offset'] + sections[e_shstrndx]['size']]
def get_sh_name(idx):
    end = shstr.find(b'\x00', idx)
    return shstr[idx:end].decode()

for s in sections:
    s['name'] = get_sh_name(s['name_idx'])

# Find .dynsym and .dynstr
dynsym = next(s for s in sections if s['name'] == '.dynsym')
dynstr = data[sections[dynsym['link']]['offset'] : sections[dynsym['link']]['offset'] + sections[dynsym['link']]['size']]

symbols = {}
num_syms = dynsym['size'] // dynsym['entsize']
for i in range(num_syms):
    sym_entry = data[dynsym['offset'] + i*dynsym['entsize'] : dynsym['offset'] + (i+1)*dynsym['entsize']]
    st_name, st_info, st_other, st_shndx, st_value, st_size = struct.unpack('<IBBHQQ', sym_entry)
    end = dynstr.find(b'\x00', st_name)
    sym_name = dynstr[st_name:end].decode('ascii', errors='ignore')
    if sym_name:
        symbols[sym_name] = (st_value, st_size)

print("Symbols in libapkprotect.so:")
for sym, (val, size) in sorted(symbols.items()):
    if any(k in sym for k in ['JNI', 'APK', 'Check']):
        print(f"  {sym} @ 0x{val:x} (size {size})")

# Disassemble JNI_OnLoad
jni_onload = symbols.get('JNI_OnLoad')
if jni_onload:
    val, size = jni_onload
    print(f"\nDisassembling JNI_OnLoad @ 0x{val:x}:")
    code = data[val:val+min(size, 200)]
    for i in cs.disasm(code, val):
        print(f"  0x{i.address:x}: {i.mnemonic:8s} {i.op_str}")
        if i.mnemonic == 'ret':
            break
