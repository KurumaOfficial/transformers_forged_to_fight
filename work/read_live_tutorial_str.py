import subprocess
import struct

def run_adb(cmd):
    p = subprocess.run(['work\\android-sdk\\platform-tools\\adb.exe', '-s', 'emulator-5554', 'shell', cmd],
                       capture_output=True, text=True)
    return p.stdout.strip()

def read_mem(pid, addr, size):
    cmd = f"dd if=/proc/{pid}/mem bs=1 count={size} skip={addr} 2>/dev/null | xxd -p"
    out = run_adb(cmd)
    clean = "".join(out.split())
    if not clean:
        return b""
    try:
        return bytes.fromhex(clean)
    except:
        return b""

def read_u64(pid, addr):
    d = read_mem(pid, addr, 8)
    return struct.unpack('<Q', d)[0] if len(d) == 8 else 0

def read_u32(pid, addr):
    d = read_mem(pid, addr, 4)
    return struct.unpack('<I', d)[0] if len(d) == 4 else 0

pids = run_adb('pidof com.kabam.bigrobot').split()
if not pids:
    print("No game PID found!")
    exit()
pid = int(pids[0])

# Find libil2cpp.so base
maps = run_adb(f"cat /proc/{pid}/maps | grep libil2cpp.so").splitlines()
lib_bases = []
for m in maps:
    parts = m.split()
    if 'r-xp' in parts[1] or 'r--p' in parts[1]:
        addr = int(parts[0].split('-')[0], 16)
        lib_bases.append((addr, parts[1]))
print("lib_bases:", [(hex(a), p) for a, p in lib_bases])
lib_base = lib_bases[1][0] # standard libil2cpp base in get_live_hub_fast

slot_addr = lib_base + 0x2bda7c0
ptr = read_u64(pid, slot_addr)
print("slot_addr:", hex(slot_addr), "ptr:", hex(ptr))

s_ptr = read_u64(pid, ptr)
print("s_ptr:", hex(s_ptr))

length = read_u32(pid, s_ptr + 0x10)
print("string length:", length)
raw_chars = read_mem(pid, s_ptr + 0x14, length * 2)
chars = raw_chars.decode('utf-16le', errors='ignore')
print("TUTORIAL ID STRING:", repr(chars))
