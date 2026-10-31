import subprocess
import struct

def run_adb(cmd):
    p = subprocess.run(f'work\\android-sdk\\platform-tools\\adb.exe -s emulator-5554 shell "{cmd}"', shell=True, capture_output=True, text=True)
    return p.stdout.strip()

def read_mem(pid, addr, size):
    cmd = f'dd if=/proc/{pid}/mem bs=1 count={size} skip={addr} 2>/dev/null | xxd -p'
    out = run_adb(cmd)
    clean = "".join(out.split())
    if not clean:
        return b""
    try:
        return bytes.fromhex(clean)
    except Exception:
        return b""

def read_u64(pid, addr):
    data = read_mem(pid, addr, 8)
    if len(data) == 8:
        return struct.unpack('<Q', data)[0]
    return 0

def read_i32(pid, addr):
    data = read_mem(pid, addr, 4)
    if len(data) == 4:
        return struct.unpack('<i', data)[0]
    return 0

def read_c_str(pid, addr, max_len=128):
    if not addr:
        return ""
    raw = read_mem(pid, addr, max_len)
    if not raw:
        return ""
    null_idx = raw.find(b'\x00')
    if null_idx != -1:
        raw = raw[:null_idx]
    return raw.decode('utf-8', errors='replace')

def get_class_name(pid, obj_addr):
    if not obj_addr:
        return "null"
    klass = read_u64(pid, obj_addr)
    if not klass:
        return "invalid_klass"
    name_ptr = read_u64(pid, klass + 0x10)
    name = read_c_str(pid, name_ptr)
    namesp_ptr = read_u64(pid, klass + 0x18)
    namesp = read_c_str(pid, namesp_ptr)
    if namesp:
        return f"{namesp}.{name}"
    return name

pid = 4204
hub_addr = 0x7B686F82D000

print(f"=== Inspecting Hub at 0x{hub_addr:X} ===")
hub_state = read_i32(pid, hub_addr + 0x20)
print(f"Hub.State (0x20): {hub_state} (0=Disc, 1=Connecting, 2=Connected, 3=Error)")

subsystems_list = read_u64(pid, hub_addr + 0x268)
print(f"Hub._subsystems: 0x{subsystems_list:X}")

state_names = {0: "Disconnected", 1: "Connecting", 2: "Connected", 3: "Error"}
if subsystems_list:
    items_arr = read_u64(pid, subsystems_list + 0x10)
    size = read_i32(pid, subsystems_list + 0x18)
    print(f"List size: {size}")
    
    not_connected = []
    for i in range(size):
        elem_addr = read_u64(pid, items_arr + 0x20 + i * 8)
        if not elem_addr:
            continue
        cname = get_class_name(pid, elem_addr)
        state = read_i32(pid, elem_addr + 0x18)
        sname = state_names.get(state, f"Unknown({state})")
        if state != 2:
            not_connected.append((i, cname, state, sname, elem_addr))
            print(f"  [{i:02d}] {cname:35s} -> State: {state} ({sname}) (0x{elem_addr:X}) [!]")
    
    print(f"\nTotal subsystems not in Connected state: {len(not_connected)} / {size}")
    if not not_connected:
        print("ALL SUBSYSTEMS ARE CONNECTED!")
