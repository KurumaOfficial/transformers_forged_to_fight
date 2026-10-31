import struct

SO_PATH = 'work/unpacked/lib/arm64-v8a/libil2cpp.so'
with open(SO_PATH, 'rb') as f:
    # Read ELF header
    e_ident = f.read(16)
    e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags, e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx = struct.unpack('<HHIQQQIHHHHHH', f.read(48))

    # Read section headers
    f.seek(e_shoff)
    sections = []
    for i in range(e_shnum):
        f.seek(e_shoff + i * e_shentsize)
        sh_name, sh_type, sh_flags, sh_addr, sh_offset, sh_size, sh_link, sh_info, sh_addralign, sh_entsize = struct.unpack('<IIQQQQIIQQ', f.read(64))
        sections.append((sh_name, sh_addr, sh_offset, sh_size))

    # Read section string table
    sh_str_offset = sections[e_shstrndx][2]
    for sh_name, sh_addr, sh_offset, sh_size in sections:
        f.seek(sh_str_offset + sh_name)
        name = b''
        while True:
            ch = f.read(1)
            if ch == b'\x00': break
            name += ch
        if sh_addr <= 0x2c2ea10 < sh_addr + sh_size:
            print(f'0x2c2ea10 is in section {name.decode("ascii")}: addr=0x{sh_addr:x}, off=0x{sh_offset:x}, size=0x{sh_size:x}')
        if sh_addr <= 0x2bbdf38 < sh_addr + sh_size:
            print(f'0x2bbdf38 is in section {name.decode("ascii")}: addr=0x{sh_addr:x}, off=0x{sh_offset:x}, size=0x{sh_size:x}')
