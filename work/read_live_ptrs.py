import subprocess
import struct

def run_adb(cmd):
    full_cmd = f"work\\platform-tools\\adb.exe shell \"{cmd}\""
    p = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    return p.stdout.strip()

def read_mem(addr, size):
    hex_str = run_adb(f"xxd -p -s +0x{addr:x} -l {size} /proc/7192/mem")
    clean = "".join(hex_str.split())
    if not clean:
        return b""
    return bytes.fromhex(clean)

# From maps: rw-p 02a97000 is at 0x7589156bc000
# So offset OFF in file -> 0x7589156bc000 + (OFF - 0x02a97000)
base_rw = 0x7589156bc000
off_rw = 0x02a97000

offsets = [0x2C07FF8, 0x2BBCF98, 0x2BD9A60, 0x2BEC1A0]
for off in offsets:
    addr = base_rw + (off - off_rw)
    raw = read_mem(addr, 8)
    if len(raw) == 8:
        ptr = struct.unpack('<Q', raw)[0]
        print(f"Off 0x{off:X} (mem 0x{addr:X}) -> Ptr 0x{ptr:X}")
        # If ptr is an Il2CppString: [Class*] [Monitor*] [length: int32] [chars...]
        str_hdr = read_mem(ptr, 24)
        if len(str_hdr) >= 24:
            str_len = struct.unpack('<I', str_hdr[0x10:0x14])[0]
            if 0 <= str_len < 200:
                chars_raw = read_mem(ptr + 0x14, str_len * 2)
                s = chars_raw.decode('utf-16le', errors='replace')
                print(f"  String: {repr(s)}")
            else:
                print(f"  Invalid string length: {str_len}")
        else:
            print("  Could not read string header")
