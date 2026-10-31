import struct

path = r'work\unpacked\assets\bin\Data\e1917cd7a6bdb4492a247b8f758df2ae'
with open(path, 'rb') as f:
    data = f.read()

# Unity SerializedFile header (version 22):
# metadataSize (u32, big-endian)
# fileSize (u64 / u32)
# version (u32)
# dataOffset (u64 / u32)
# endianness (u8)
# reserved (u8[3])

meta_size = struct.unpack('>I', data[:4])[0]
file_size = struct.unpack('>I', data[4:8])[0]
version = struct.unpack('>I', data[8:12])[0]
data_offset = struct.unpack('>I', data[12:16])[0]
endian = data[16]

print(f"Header: meta_size={meta_size}, file_size={file_size}, version={version}, data_offset={data_offset}, endian={endian}")

# Let's inspect object table
# At offset 20 or 22:
# Unity 22 header has unity_version string at offset 48
print("Header preview:", data[:100])
