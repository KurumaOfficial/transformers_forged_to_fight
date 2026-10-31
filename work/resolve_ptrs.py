import struct

ELF_PATH = 'work/unpacked/lib/arm64-v8a/libil2cpp.so'
with open(ELF_PATH, 'rb') as f:
    elf_data = f.read()

def read_u64(offset):
    return struct.unpack('<Q', elf_data[offset:offset+8])[0]

def read_str_from_global_metadata(offset):
    # If it points to an IL2CPP string object:
    # IL2CPP String struct: [Class*] [Monitor*] [length: int32] [chars: utf-16]
    # Let's inspect bytes at offset
    ptr = read_u64(offset)
    print(f"Ptr at 0x{offset:X} -> 0x{ptr:X}")
    if ptr < len(elf_data) and ptr > 0:
        # Check if it looks like a String object
        length = struct.unpack('<I', elf_data[ptr+0x10 : ptr+0x14])[0]
        if length < 200:
            chars = elf_data[ptr+0x14 : ptr+0x14 + length*2].decode('utf-16le', errors='ignore')
            print(f"  String ({length}): {chars}")

print("Checking 0x2C09E98:")
read_str_from_global_metadata(0x2C09E98)

print("Checking 0x2C16FE8:")
read_str_from_global_metadata(0x2C16FE8)
