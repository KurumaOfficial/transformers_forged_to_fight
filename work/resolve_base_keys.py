import struct

ELF_PATH = 'work/unpacked/lib/arm64-v8a/libil2cpp.so'
with open(ELF_PATH, 'rb') as f:
    elf_data = f.read()

def read_u64(offset):
    return struct.unpack('<Q', elf_data[offset:offset+8])[0]

offsets = [0x2C07FF8, 0x2BBCF98, 0x2BD9A60, 0x2BEC1A0]
for off in offsets:
    ptr = read_u64(off)
    print(f"Off 0x{off:X} -> Ptr 0x{ptr:X}")
    length = struct.unpack('<I', elf_data[ptr+0x10 : ptr+0x14])[0]
    raw = elf_data[ptr+0x14 : ptr+0x14 + length*2]
    chars = raw.decode('utf-16le', errors='replace')
    print(f"  Length: {length}, Chars: {ascii(chars)}")
