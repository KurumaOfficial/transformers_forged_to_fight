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

targets = [
    (0x2D09890, "suffix1 (DeserializeAvailableBuildings)"),
    (0x2D23750, "suffix2 (DeserializeOwnedBuildings)"),
    (0x2D4A070, "suffix3 (DeserializeUnlocks)"),
    (0x2D4E1E8, "suffix4 (base object)"),
]

for off, label in targets:
    mem_addr = base_rw + (off - off_rw)
    raw = read_mem(mem_addr, 8)
    ptr = struct.unpack('<Q', raw)[0] if raw else 0
    print(f"{label} at 0x{mem_addr:X}: ptr = 0x{ptr:X}")
    if ptr != 0:
        str_hdr = read_mem(ptr, 24)
        if len(str_hdr) >= 24:
            slen = struct.unpack('<I', str_hdr[0x10:0x14])[0]
            if 0 <= slen < 100:
                sraw = read_mem(ptr + 0x14, slen * 2)
                s = sraw.decode('utf-16le', errors='replace')
                print(f"  String ({slen}): {repr(s)}")
            else:
                print(f"  Header length={slen}")
                # Maybe ptr is Il2CppClass or MethodInfo?
                # Let's inspect class name
                name_ptr_raw = read_mem(ptr + 0x10, 8)
                if name_ptr_raw:
                    name_ptr = struct.unpack('<Q', name_ptr_raw)[0]
                    name_bytes = read_mem(name_ptr, 32)
                    print(f"  Class name: {name_bytes.split(b'\\x00')[0]}")
