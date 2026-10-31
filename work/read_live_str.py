import subprocess
import struct

def run_adb(cmd):
    full_cmd = ["work\\platform-tools\\adb.exe", "shell", "su 0 sh -c '" + cmd + "'"]
    p = subprocess.run(full_cmd, capture_output=True, text=True)
    return p.stdout.strip()

def read_mem(addr, size):
    hex_str = run_adb(f"xxd -p -s +0x{addr:x} -l {size} /proc/4634/mem")
    clean = "".join(hex_str.split())
    if not clean:
        return b""
    return bytes.fromhex(clean)

rw_base = 0x75bae50c1000
rw_file_off = 0x02a97000

# offset in libil2cpp.so: 0x2C01920
off = 0x2C01920
addr = rw_base + (off - rw_file_off)
raw = read_mem(addr, 8)
print(f"Address in mem: 0x{addr:x}, Raw: {raw.hex()}")
if raw:
    ptr = struct.unpack('<Q', raw)[0]
    print(f"ptr = 0x{ptr:x}")
    str_raw = read_mem(ptr, 64)
    print("Raw at ptr:", str_raw.hex())
    if len(str_raw) >= 20:
        slen = struct.unpack('<I', str_raw[16:20])[0]
        s_chars = str_raw[20:20+slen*2].decode('utf-16le', errors='replace')
        print("String length=", slen, "ascii=", ascii(s_chars))
