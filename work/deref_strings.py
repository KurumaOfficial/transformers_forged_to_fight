import struct

ELF_PATH = 'work/unpacked/lib/arm64-v8a/libil2cpp.so'
with open(ELF_PATH, 'rb') as f:
    elf_data = f.read()

def read_u64(offset):
    return struct.unpack('<Q', elf_data[offset:offset+8])[0]

offsets = [0x2C07FF8, 0x2BBCF98, 0x2BD9A60, 0x2BEC1A0]
for off in offsets:
    ptr1 = read_u64(off)
    ptr2 = read_u64(ptr1)
    print(f"Off 0x{off:X} -> Ptr1 0x{ptr1:X} -> Ptr2 0x{ptr2:X}")
    length = struct.unpack('<I', elf_data[ptr2+0x10 : ptr2+0x14])[0]
    raw = elf_data[ptr2+0x14 : ptr2+0x14 + length*2]
    chars = raw.decode('utf-16le', errors='replace')
    print(f"  Result string: {repr(chars)}")
