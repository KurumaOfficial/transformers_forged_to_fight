import struct

with open('work/unpacked/assets/bin/Data/Managed/Metadata/global-metadata.dat', 'rb') as f:
    meta = f.read()

def get_literal(idx):
    # stringLiteralOffset is 256
    entry_offset = 256 + idx * 8
    length, data_index = struct.unpack('<II', meta[entry_offset:entry_offset+8])
    data_start = 195224 + data_index
    return meta[data_start:data_start+length].decode('utf-8', errors='ignore')

# Check first 10
for i in range(10):
    print(i, repr(get_literal(i)))
