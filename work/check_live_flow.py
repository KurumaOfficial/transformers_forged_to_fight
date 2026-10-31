import subprocess
import struct

def run_adb(cmd):
    p = subprocess.run(["work\\platform-tools\\adb.exe", "shell", f"su 0 sh -c '{cmd}'"], capture_output=True, text=True)
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

def read_c_str(pid, addr, max_len=128):
    if not addr: return ""
    raw = read_mem(pid, addr, max_len)
    if not raw: return ""
    null_idx = raw.find(b'\x00')
    if null_idx != -1: raw = raw[:null_idx]
    return raw.decode('utf-8', errors='replace')

def get_class_name(pid, obj_addr):
    if not obj_addr: return "null"
    klass = read_u64(pid, obj_addr)
    if not klass: return "invalid_klass"
    name_ptr = read_u64(pid, klass + 0x10)
    name = read_c_str(pid, name_ptr)
    namesp_ptr = read_u64(pid, klass + 0x18)
    namesp = read_c_str(pid, namesp_ptr)
    return f"{namesp}.{name}" if namesp else name

pid = 5655
base = 0x75bae25c6000

fm_slot = read_u64(pid, base + 0x2bffe18)
if fm_slot:
    fm_klass = read_u64(pid, fm_slot)
    fm_static = read_u64(pid, fm_klass + 0xB8)
    fm_inst = read_u64(pid, fm_static)
    print(f"FlowManager.Instance: 0x{fm_inst:X} ({get_class_name(pid, fm_inst)})")
    if fm_inst:
        in_prog = read_u64(pid, fm_inst + 0x20)
        stack = read_u64(pid, fm_inst + 0x18)
        print(f"  _inProgressFlow: 0x{in_prog:X} ({get_class_name(pid, in_prog)})")
        if stack:
            stack_items = read_u64(pid, stack + 0x10)
            stack_size = struct.unpack('<i', read_mem(pid, stack + 0x18, 4))[0]
            print(f"  _flowStack size: {stack_size}")
            for i in range(stack_size):
                item = read_u64(pid, stack_items + 0x20 + i * 8)
                print(f"    [{i}]: 0x{item:X} ({get_class_name(pid, item)})")

gm_slot = read_u64(pid, base + 0x2c14120)
if gm_slot:
    gm_klass = read_u64(pid, gm_slot)
    gm_static = read_u64(pid, gm_klass + 0xB8)
    gm_inst = read_u64(pid, gm_static)
    print(f"\nGameboardManager.Instance: 0x{gm_inst:X} ({get_class_name(pid, gm_inst)})")
    if gm_inst:
        baseboard = read_u64(pid, gm_inst + 0x30)
        print(f"  _baseBoard: 0x{baseboard:X} ({get_class_name(pid, baseboard)})")
        ready_raw = read_mem(pid, gm_inst + 0x60, 4)
        if ready_raw:
            print(f"  ready flags (0x60): {ready_raw.hex()}")
