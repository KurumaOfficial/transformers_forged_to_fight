import struct

meta_path = r".\work\unpacked\assets\bin\Data\Managed\Metadata\global-metadata.dat"

with open(meta_path, "rb") as f:
    data = f.read()

# Header size for v27
# Let's inspect all 4-byte integers up to stringLiteral offset (256)
count = 256 // 4
vals = struct.unpack(f"<{count}I", data[:256])

print(f"Magic: 0x{vals[0]:08X}, Version: {vals[1]}")
for i in range(2, count, 2):
    off = vals[i]
    sz = vals[i+1]
    if off > 0 or sz > 0:
        print(f"Index {i//2}: offset=0x{off:08X} ({off:9d}), size=0x{sz:08X} ({sz:9d})")
