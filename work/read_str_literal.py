import subprocess, struct
def run_adb(cmd):
    p = subprocess.run(["work\\platform-tools\\adb.exe", "shell", f"su 0 sh -c '{cmd}'"], capture_output=True, text=True)
    return p.stdout.strip()
pid = 12670
base = 0x75b9cad5e000
addr = base + 0x2D807E0
out = run_adb(f"dd if=/proc/{pid}/mem bs=1 count=32 skip={addr} 2>/dev/null | xxd -p")
raw = bytes.fromhex("".join(out.split()))
str_ptr = struct.unpack('<Q', raw[:8])[0]
print(f"str_ptr raw: 0x{str_ptr:X}")
if str_ptr < base:
    str_ptr += base
print(f"str_ptr resolved: 0x{str_ptr:X}")
if str_ptr > base:
    slen_bytes = bytes.fromhex("".join(run_adb(f"dd if=/proc/{pid}/mem bs=1 count=4 skip={str_ptr + 0x10} 2>/dev/null | xxd -p").split()))
    slen = struct.unpack('<I', slen_bytes)[0]
    sbytes = bytes.fromhex("".join(run_adb(f"dd if=/proc/{pid}/mem bs=1 count={slen*2} skip={str_ptr + 0x14} 2>/dev/null | xxd -p").split()))
    print("String value:", ascii(sbytes.decode('utf-16le', errors='replace')))
