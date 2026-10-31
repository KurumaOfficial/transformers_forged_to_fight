import struct

with open("work/unpacked/lib/arm64-v8a/libil2cpp.so", "rb") as f:
    lib = f.read()

def read_u64(addr):
    return struct.unpack('<Q', lib[addr:addr+8])[0]

def get_str_obj(ptr):
    l = struct.unpack('<I', lib[ptr+16:ptr+20])[0]
    return lib[ptr+20:ptr+20+l*2].decode('utf-16le', errors='ignore')

addrs = [
    0x2c28320,
    0x2bea210,
    0x2c2ec30,
    0x2c14060,
    0x2c3ace0,
    0x2be5028,
]

for a in addrs:
    p = read_u64(a)
    print(f"0x{a:x} -> 0x{p:x}")
    if p:
        try:
            print("  Str:", repr(get_str_obj(p)))
        except Exception as e:
            print("  Err:", e)
