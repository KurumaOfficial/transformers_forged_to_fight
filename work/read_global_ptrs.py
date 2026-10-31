import json
import struct

with open("work/unpacked/lib/arm64-v8a/libil2cpp.so", "rb") as f:
    lib = f.read()

def read_u64(addr):
    if 0 <= addr < len(lib) - 8:
        return struct.unpack("<Q", lib[addr:addr+8])[0]
    return 0

# Check stringliterals around those addresses
# Let's inspect the pointers at 0x2bc1898 and 0x2bd16b0
for ptr_addr in [0x2bc1898, 0x2bd16b0]:
    val = read_u64(ptr_addr)
    print(f"Ptr at 0x{ptr_addr:x} -> 0x{val:x}")
    if val:
        # Il2CppString: header is 16 bytes, then length (u32), then utf16 chars
        length = struct.unpack("<I", lib[val+16:val+20])[0] if val + 20 < len(lib) else 0
        if 0 < length < 200:
            s = lib[val+20:val+20+length*2].decode('utf-16le', errors='ignore')
            print(f"  String: {s!r}")
