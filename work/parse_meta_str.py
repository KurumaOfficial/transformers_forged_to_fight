import struct

with open('work/unpacked/assets/bin/Data/Managed/Metadata/global-metadata.dat', 'rb') as f:
    data = f.read()

# Header fields (all uint32):
# 0: sanity
# 1: version
# 2: stringLiteralOffset
# 3: stringLiteralSize
# 4: stringLiteralDataOffset
# 5: stringLiteralDataSize
# Let's inspect first 30 integers
hdr = struct.unpack('<30I', data[:120])
print("Header:")
for i, v in enumerate(hdr):
    print(f"  [{i}] = 0x{v:X} ({v})")
