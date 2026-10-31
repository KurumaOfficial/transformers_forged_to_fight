import subprocess
import struct

def run_adb(cmd):
    full_cmd = f"work\\platform-tools\\adb.exe shell \"{cmd}\""
    p = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    return p.stdout.strip()

def read_mem(addr, size):
    hex_str = run_adb(f"xxd -p -s +0x{addr:x} -l {size} /proc/7192/mem")
    clean = "".join(hex_str.split())
    if not clean: return b""
    return bytes.fromhex(clean)

base_rw = 0x7589156bc000
off_rw = 0x02a97000

# 0x2E4AD70:
arr_ptr_addr = base_rw + (0x2E4AD70 - off_rw)
raw = read_mem(arr_ptr_addr, 8)
arr_ptr = struct.unpack('<Q', raw)[0]
print(f"Table pointer at 0x{arr_ptr_addr:X} is 0x{arr_ptr:X}")

tokens = [0x2C07FF8, 0x2BBCF98, 0x2BD9A60, 0x2BEC1A0]
for off in tokens:
    addr = base_rw + (off - off_rw)
    raw_ptr = read_mem(addr, 8)
    ptr1 = struct.unpack('<Q', raw_ptr)[0]
    raw_val = read_mem(ptr1, 8)
    val = struct.unpack('<Q', raw_val)[0]
    usage_type = ((val >> 29) & 7) - 1
    idx = (val >> 1) & 0x1FFFFFFF
    print(f"Off 0x{off:X} -> Val 0x{val:X} -> Type {usage_type+1}, Idx {idx}")
    if arr_ptr != 0:
        elem_addr = arr_ptr + idx * 8
        elem_raw = read_mem(elem_addr, 8)
        if elem_raw:
            elem_ptr = struct.unpack('<Q', elem_raw)[0]
            print(f"  Elem at index {idx} -> 0x{elem_ptr:X}")
            if elem_ptr != 0:
                str_hdr = read_mem(elem_ptr, 24)
                if len(str_hdr) >= 24:
                    slen = struct.unpack('<I', str_hdr[0x10:0x14])[0]
                    if 0 <= slen < 100:
                        sraw = read_mem(elem_ptr + 0x14, slen * 2)
                        print(f"    String: {repr(sraw.decode('utf-16le', errors='replace'))}")
                    else:
                        print(f"    Length {slen}")
