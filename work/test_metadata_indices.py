import struct

with open('work/unpacked/assets/bin/Data/Managed/Metadata/global-metadata.dat', 'rb') as f:
    data = f.read()

hdr = struct.unpack('<30I', data[:120])
str_lit_data_off = hdr[4] # 0x2FA98
str_lit_off = hdr[6]      # 0xB45C0

def get_str(idx):
    entry_off = str_lit_off + idx * 8
    length, data_idx = struct.unpack('<II', data[entry_off : entry_off + 8])
    data_off = str_lit_data_off + data_idx
    return data[data_off : data_off + length].decode('utf-8', errors='replace')

for idx in [0x207B, 0x8FB, 0x10D63, 0x227B, 0x32DD, 2048]:
    try:
        val = get_str(idx)
        print(f"Index {idx} (0x{idx:X}): {repr(val)}")
    except Exception as e:
        print(f"Index {idx} error: {e}")
