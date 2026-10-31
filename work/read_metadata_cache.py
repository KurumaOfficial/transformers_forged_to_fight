import subprocess
import struct

def run_adb(cmd):
    full_cmd = f"work\\platform-tools\\adb.exe shell \"{cmd}\""
    p = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    return p.stdout.strip()

base_rw = 0x7589156bc000
off_rw = 0x02a97000
target_addr = base_rw + (0x2E4AD00 - off_rw)

hex_str = run_adb(f"xxd -p -s +0x{target_addr:x} -l 128 /proc/7192/mem")
clean = "".join(hex_str.split())
raw = bytes.fromhex(clean)
for i in range(0, len(raw), 8):
    val = struct.unpack('<Q', raw[i:i+8])[0]
    print(f"0x{0x2E4AD00 + i:X} (mem 0x{target_addr + i:X}): 0x{val:X}")
