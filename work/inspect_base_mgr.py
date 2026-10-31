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

def read_u8(pid, addr):
    data = read_mem(pid, addr, 1)
    if len(data) == 1:
        return data[0]
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

# BaseManager is at Hub + 0x208
base_mgr = read_u64(pid, hub_addr + 0x208)
print(f"BaseManager: 0x{base_mgr:X} ({get_class_name(pid, base_mgr)})")

if base_mgr:
    # BaseManager.user (BaseSubManager)
    # let's inspect fields of BaseManager
    for off in range(0x18, 0x50, 8):
        val = read_u64(pid, base_mgr + off)
        cname = get_class_name(pid, val) if val > 0x10000 else ""
        print(f"  BaseManager +0x{off:02X}: 0x{val:X} ({cname})")
        if "BaseSubManager" in cname:
            sub = val
            base_obj = read_u64(pid, sub + 0x28)
            out_of_date = read_u8(pid, sub + 0x30)
            print(f"    BaseSubManager.base_ (0x28): 0x{base_obj:X} ({get_class_name(pid, base_obj)})")
            print(f"    BaseSubManager.isBaseOutOfDate (0x30): {out_of_date}")
