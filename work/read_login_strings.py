import struct
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('work/unpacked/lib/arm64-v8a/libil2cpp.so', 'rb') as f:
    so = f.read()

for p in [0x2d39f98, 0x2d15ed0, 0x2d7dc80]:
    slen = struct.unpack('<I', so[p+0x10:p+0x14])[0]
    raw = so[p+0x14:p+0x14+slen*2]
    chars = raw.decode('utf-16le', errors='replace')
    print(f"{hex(p)}: len={slen}, chars={chars}")
