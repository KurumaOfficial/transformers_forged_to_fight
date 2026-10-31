import subprocess
import struct
import sys

def run_adb(cmd):
    p = subprocess.run(f"work\\android-sdk\\platform-tools\\adb.exe shell \"{cmd}\"",
                       shell=True, capture_output=True, text=True)
    return p.stdout.strip()

def read_mem(pid, addr, size):
    cmd = f"dd if=/proc/{pid}/mem bs=1 count={size} skip={addr} 2>/dev/null | xxd -p"
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
        return struct.unpack("<Q", data)[0]
    return 0

def read_u32(pid, addr):
    data = read_mem(pid, addr, 4)
    if len(data) == 4:
        return struct.unpack("<I", data)[0]
    return 0

def read_i32(pid, addr):
    data = read_mem(pid, addr, 4)
    if len(data) == 4:
        return struct.unpack("<i", data)[0]
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

def read_il2cpp_str(pid, addr):
    if not addr:
        return ""
    # Il2CppString: [Class* 8] [Monitor* 8] [length: int32 4] [chars: wchar 2*len]
    length = read_i32(pid, addr + 0x10)
    if 0 < length < 500:
        raw = read_mem(pid, addr + 0x14, length * 2)
        return raw.decode('utf-16le', errors='replace')
    return ""

def main():
    pid = 5033
    hub_addr = 0x7e9c67972000
    print(f"=== Inspecting EB.Sparx.Hub at 0x{hub_addr:X} (PID {pid}) ===")

    hub_state = read_i32(pid, hub_addr + 0x20)
    print(f"Hub.State: {hub_state}")

    login_mgr_addr = read_u64(pid, hub_addr + 0x40)
    print(f"LoginManager: 0x{login_mgr_addr:X}")
    if login_mgr_addr:
        lm_state = read_i32(pid, login_mgr_addr + 0xA8)
        lm_last_err_ptr = read_u64(pid, login_mgr_addr + 0xA0)
        lm_last_err = read_il2cpp_str(pid, lm_last_err_ptr)
        print(f"  LoginManager.LoginState: {lm_state} (0=Disc, 1=Init, 2=Inited, 3=Auth, 4=LoggingIn, 5=LoggedIn)")
        print(f"  LoginManager._lastError: {repr(lm_last_err)}")

    subsystems_list = read_u64(pid, hub_addr + 0x268)
    print(f"Hub._subsystems: 0x{subsystems_list:X}")
    if subsystems_list:
        items_arr = read_u64(pid, subsystems_list + 0x10)
        size = read_i32(pid, subsystems_list + 0x18)
        print(f"  List size: {size}, items array: 0x{items_arr:X}")
        
        state_names = {0: "Disconnected", 1: "Connecting", 2: "Connected", 3: "Error"}
        
        for i in range(size):
            elem_addr = read_u64(pid, items_arr + 0x20 + i * 8)
            if not elem_addr:
                continue
            klass_ptr = read_u64(pid, elem_addr)
            klass_name_ptr = read_u64(pid, klass_ptr + 0x10)
            klass_name = read_c_str(pid, klass_name_ptr)
            
            # SubSystem.State is at 0x18
            sub_state = read_i32(pid, elem_addr + 0x18)
            state_str = state_names.get(sub_state, f"Unknown({sub_state})")
            
            status_flag = " [!] ERROR" if sub_state == 3 else ""
            print(f"  [{i:02d}] {klass_name:30s} -> State: {sub_state} ({state_str}){status_flag} (0x{elem_addr:X})")
            
            if sub_state == 3:
                # Let's inspect fields of the errored subsystem!
                print(f"      DUMPING ERROR SUBSYSTEM: {klass_name}")
                for off in range(0x18, 0x100, 8):
                    val = read_u64(pid, elem_addr + off)
                    s = read_il2cpp_str(pid, val)
                    if s:
                        print(f"      +0x{off:02X}: 0x{val:X} -> string: {repr(s)}")

if __name__ == "__main__":
    main()
