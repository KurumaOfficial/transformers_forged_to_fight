import struct
import json

ELF_PATH = 'work/unpacked/lib/arm64-v8a/libil2cpp.so'
with open(ELF_PATH, 'rb') as f:
    elf_data = f.read()

def read_u64(offset):
    return struct.unpack('<Q', elf_data[offset:offset+8])[0]

offsets = [0x2C07FF8, 0x2BBCF98, 0x2BD9A60, 0x2BEC1A0]
indices = []
for off in offsets:
    ptr1 = read_u64(off)
    ptr2 = read_u64(ptr1)
    idx = ptr2 & 0x00FFFFFF
    print(f"Off 0x{off:X} -> Ptr1 0x{ptr1:X} -> Val 0x{ptr2:X} (Token Index: 0x{idx:X} = {idx})")
    indices.append(idx)

# Let's inspect stringliteral.json by index or global-metadata.dat
METADATA_PATH = 'work/unpacked/assets/bin/Data/Managed/Metadata/global-metadata.dat'
with open(METADATA_PATH, 'rb') as f:
    meta = f.read()

# In global-metadata.dat header:
# [0] sanity (0xFAB11BAF)
# [1] version (24)
# StringLiterals offset and size:
# let's parse header
header = struct.unpack('<24I', meta[:96])
print(f"Metadata header: sanity=0x{header[0]:X}, version={header[1]}")
# In IL2CPP v24 metadata header:
# stringLiteralOffset is at index 4 (byte 16)
# stringLiteralCount is at index 5 (byte 20)
# stringLiteralDataOffset is at index 6 (byte 24)
# stringLiteralDataCount is at index 7 (byte 28)
str_lit_off = header[4]
str_lit_size = header[5]
str_lit_data_off = header[6]
str_lit_data_size = header[7]
print(f"stringLiteralOffset: 0x{str_lit_off:X}, stringLiteralDataOffset: 0x{str_lit_data_off:X}")

for idx in indices:
    entry_off = str_lit_off + idx * 8
    length, data_idx = struct.unpack('<II', meta[entry_off : entry_off + 8])
    data_off = str_lit_data_off + data_idx
    str_val = meta[data_off : data_off + length].decode('utf-8', errors='replace')
    print(f"Index {idx} (0x{idx:X}): length={length}, string={repr(str_val)}")
