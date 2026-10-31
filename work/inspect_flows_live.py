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

def read_u32(pid, addr):
    data = read_mem(pid, addr, 4)
    if len(data) == 4:
        return struct.unpack('<I', data)[0]
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
base = 0x7b686a7d3000

print(f"=== Inspecting PID {pid} (base: 0x{base:X}) ===")

# 1. FlowManager
# FlowManager.get_Instance RVA 0xDC8D58 uses adrp to 0x2bff000 + 0xe18 = 0x2bffe18
fm_slot = read_u64(pid, base + 0x2bffe18)
print(f"FlowManager slot: 0x{fm_slot:X}")
if fm_slot:
    fm_klass = read_u64(pid, fm_slot)
    print(f"FlowManager klass: 0x{fm_klass:X}")
    fm_static = read_u64(pid, fm_klass + 0xB8)
    print(f"FlowManager static_fields: 0x{fm_static:X}")
    fm_inst = read_u64(pid, fm_static)
    print(f"FlowManager.Instance: 0x{fm_inst:X} ({get_class_name(pid, fm_inst)})")
    if fm_inst:
        in_prog = read_u64(pid, fm_inst + 0x20)
        fte_flow = read_u64(pid, fm_inst + 0x40)
        stack = read_u64(pid, fm_inst + 0x18)
        op_queue = read_u64(pid, fm_inst + 0x38)
        print(f"  _inProgressFlow: 0x{in_prog:X} ({get_class_name(pid, in_prog)})")
        print(f"  <FTEFlow>: 0x{fte_flow:X} ({get_class_name(pid, fte_flow)})")
        print(f"  _flowStack: 0x{stack:X} ({get_class_name(pid, stack)})")
        if stack:
            stack_items = read_u64(pid, stack + 0x10)
            stack_size = read_i32(pid, stack + 0x18)
            print(f"    _flowStack size: {stack_size}")
            for i in range(stack_size):
                item = read_u64(pid, stack_items + 0x20 + i * 8)
                print(f"      [{i}]: 0x{item:X} ({get_class_name(pid, item)})")
        print(f"  _opQueue: 0x{op_queue:X} ({get_class_name(pid, op_queue)})")
        if op_queue:
            q_size = read_i32(pid, op_queue + 0x20)
            print(f"    _opQueue size: {q_size}")

        
        # If _inProgressFlow exists, inspect its fields!
        if in_prog:
            cls = get_class_name(pid, in_prog)
            print(f"  Inspecting inProgressFlow ({cls}):")
            for off in range(0x10, 0x80, 8):
                val = read_u64(pid, in_prog + off)
                cname = get_class_name(pid, val) if val > 0x10000 else ""
                print(f"    +0x{off:02X}: 0x{val:X} {cname}")

# 2. GameboardManager
gm_slot = read_u64(pid, base + 0x2c14120)
print(f"\nGameboardManager slot: 0x{gm_slot:X}")
if gm_slot:
    gm_klass = read_u64(pid, gm_slot)
    print(f"GameboardManager klass: 0x{gm_klass:X}")
    gm_static = read_u64(pid, gm_klass + 0xB8)
    print(f"GameboardManager static_fields: 0x{gm_static:X}")
    gm_inst = read_u64(pid, gm_static)
    print(f"GameboardManager.Instance: 0x{gm_inst:X} ({get_class_name(pid, gm_inst)})")
    if gm_inst:
        baseboard = read_u64(pid, gm_inst + 0x30)
        quest_tuning = read_u64(pid, gm_inst + 0x50)
        base_tuning = read_u64(pid, gm_inst + 0x58)
        raw_ready = read_u32(pid, gm_inst + 0x60)
        quest_ready = raw_ready & 0xFF
        base_ready = (raw_ready >> 8) & 0xFF
        raid_ready = (raw_ready >> 16) & 0xFF
        print(f"  _baseBoard: 0x{baseboard:X} ({get_class_name(pid, baseboard)})")
        print(f"  _questNodeTuning: 0x{quest_tuning:X} ({get_class_name(pid, quest_tuning)})")
        print(f"  _baseNodeTuning: 0x{base_tuning:X} ({get_class_name(pid, base_tuning)})")
        print(f"  _questNodeTuningReady (0x60): {quest_ready}")
        print(f"  _baseNodeTuningReady (0x61): {base_ready}")
        print(f"  _raidTutorialCompleteOnBaseLoad (0x62): {raid_ready}")
