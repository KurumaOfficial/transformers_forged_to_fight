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

def read_i32(pid, addr):
    d = read_mem(pid, addr, 4)
    return struct.unpack('<i', d)[0] if len(d) == 4 else 0

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

def main():
    pids = run_adb('pidof com.kabam.bigrobot').split()
    if not pids:
        print("No game PID found!")
        return
    pid = int(pids[0])
    print(f"Game PID: {pid}")

    maps_output = run_adb(f"grep libil2cpp.so /proc/{pid}/maps")
    lib_base = None
    for line in maps_output.strip().splitlines():
        parts = line.split()
        if len(parts) >= 5 and parts[1] == 'r--p' and parts[2] == '00000000':
            addr_start = int(parts[0].split('-')[0], 16)
            lib_base = addr_start

    print(f"libil2cpp base: 0x{lib_base:X}")

    slot_addr = lib_base + 0x2BC7D18
    ptr1 = read_u64(pid, slot_addr)
    ptr2 = read_u64(pid, ptr1)
    static_fields = read_u64(pid, ptr2 + 0xB8)
    hub_inst = read_u64(pid, static_fields)

    print(f"Hub.Instance: 0x{hub_inst:X} ({get_class_name(pid, hub_inst)})")
    if not hub_inst:
        return

    hub_state = read_i32(pid, hub_inst + 0x20)
    state_names = {0: "Disconnected", 1: "Connecting", 2: "Connected", 3: "Error"}
    print(f"Hub.State (0x20): {hub_state} ({state_names.get(hub_state, 'Unknown')})")

    subsystems_list = read_u64(pid, hub_inst + 0x268)
    if not subsystems_list:
        print("No subsystems list!")
        return

    items_arr = read_u64(pid, subsystems_list + 0x10)
    size = read_i32(pid, subsystems_list + 0x18)
    print(f"Subsystems count: {size}")

    # Read all element pointers at once!
    arr_bytes = read_mem(pid, items_arr + 0x20, size * 8)
    elem_addrs = [struct.unpack('<Q', arr_bytes[i*8:(i+1)*8])[0] for i in range(size)]

    not_connected = []
    for i, elem_addr in enumerate(elem_addrs):
        if not elem_addr:
            continue
        # Read state (at elem_addr + 0x18)
        state = read_i32(pid, elem_addr + 0x18)
        sname = state_names.get(state, f"Unknown({state})")
        if state != 2:
            cname = get_class_name(pid, elem_addr)
            not_connected.append((i, cname, state, sname, elem_addr))
            print(f"  [{i:02d}] {cname:40s} -> State: {state} ({sname})")

    print(f"\nTotal not Connected: {len(not_connected)} / {size}")
    if not not_connected:
        print(">>> ALL 71 SUBSYSTEMS ARE CONNECTED! <<<")

if __name__ == '__main__':
    main()
