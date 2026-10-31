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
    if not clean: return b""
    try: return bytes.fromhex(clean)
    except: return b""

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
maps = run_adb(f"grep libil2cpp.so /proc/{pid}/maps").splitlines()
lib_base = None
for line in maps:
    parts = line.split()
    if len(parts) >= 5 and parts[1] == 'r--p' and parts[2] == '00000000':
        lib_base = int(parts[0].split('-')[0], 16)

hub_slot = lib_base + 0x2BC7D18
ptr1 = read_u64(pid, hub_slot)
ptr2 = read_u64(pid, ptr1)
sf = read_u64(pid, ptr2 + 0xB8)
hub = read_u64(pid, sf)
print(f"Hub: {hex(hub)}")

tut_mgr = read_u64(pid, hub + 0x158)
print(f"TutorialManager: {hex(tut_mgr)}")

user_data_dict = read_u64(pid, tut_mgr + 0x28)
print(f"UserData dict: {hex(user_data_dict)}")

entries = read_u64(pid, user_data_dict + 0x18)
count = read_u32(pid, user_data_dict + 0x20)
print(f"UserData count: {count}, entries: {hex(entries)}")

raw_entries = read_mem(pid, entries + 0x20, count * 24)
for i in range(count):
    entry_bytes = raw_entries[i*24:(i+1)*24]
    if len(entry_bytes) < 24: continue
    key_ptr = struct.unpack('<Q', entry_bytes[8:16])[0]
    val_ptr = struct.unpack('<Q', entry_bytes[16:24])[0]
    if key_ptr:
        k_len = read_u32(pid, key_ptr + 0x10)
        k_str = read_mem(pid, key_ptr + 0x14, k_len * 2).decode('utf-16le', errors='ignore')
        state = read_u32(pid, val_ptr + 0x20) if val_ptr else -1
        cur_branch_ptr = read_u64(pid, val_ptr + 0x18) if val_ptr else 0
        b_len = read_u32(pid, cur_branch_ptr + 0x10) if cur_branch_ptr else 0
        b_str = read_mem(pid, cur_branch_ptr + 0x14, b_len * 2).decode('utf-16le', errors='ignore') if b_len else ""
        print(f"  Key '{k_str}': TutorialUserData={hex(val_ptr)}, State={state}, curBranch='{b_str}'")
