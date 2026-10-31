import struct

with open('work/unpacked/assets/bin/Data/Managed/Metadata/global-metadata.dat', 'rb') as f:
    meta = f.read()

def get_literal(idx):
    entry_offset = 256 + idx * 8
    length, data_index = struct.unpack('<II', meta[entry_offset:entry_offset+8])
    data_start = 195224 + data_index
    return meta[data_start:data_start+length].decode('utf-8', errors='ignore')

pairs_offset = 9464880
pairs_count = 376056 // 8

rva_to_literal = {}
for i in range(pairs_count):
    dest, encoded = struct.unpack('<II', meta[pairs_offset + i*8 : pairs_offset + (i+1)*8])
    usage_type = encoded >> 29
    idx = encoded & 0x1FFFFFFF
    # If usage_type == 5 (kIl2CppMetadataUsageStringLiteral)
    if usage_type == 5:
        rva_to_literal[dest] = get_literal(idx)

print(f"Total string literal mappings: {len(rva_to_literal)}")

# Test looking up the destinations from EndPointFactory (0x2c10dc0, 0x2bffa68)
print("0x2c10dc0 ->", rva_to_literal.get(0x2c10dc0))
print("0x2bffa68 ->", rva_to_literal.get(0x2bffa68))
print("0x2bc1898 ->", rva_to_literal.get(0x2bc1898))
print("0x2bd16b0 ->", rva_to_literal.get(0x2bd16b0))
