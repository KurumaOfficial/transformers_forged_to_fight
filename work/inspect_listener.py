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
base = 0x7b686a7d3000

# Let's find Hub.Instance
# In inspect_live_hub.py, Hub is a Subsystem or has Instance
# Let's search Hub_TypeInfo
import json
with open('work/il2cpp_dump/script.json', 'r') as f:
    sdata = json.load(f)

hub_rva = None
for item in sdata.get('ScriptMetadata', []):
    if item.get('Name') == 'EB.Sparx.Hub_TypeInfo':
        hub_rva = item.get('Address')
        break

print(f"Hub_TypeInfo RVA: 0x{hub_rva:X}")
hub_klass = read_u64(pid, base + hub_rva)
print(f"Hub klass: 0x{hub_klass:X}")
hub_static = read_u64(pid, hub_klass + 0xB8)
print(f"Hub static_fields: 0x{hub_static:X}")
# Check static fields
hub_inst = read_u64(pid, hub_static)
print(f"Hub.Instance: 0x{hub_inst:X} ({get_class_name(pid, hub_inst)})")

if hub_inst:
    login_mgr = read_u64(pid, hub_inst + 0x40)
    print(f"LoginManager: 0x{login_mgr:X} ({get_class_name(pid, login_mgr)})")
    if login_mgr:
        # Let's check fields of LoginManager
        listener = read_u64(pid, login_mgr + 0x48) # let's check listeners
        print(f"  LoginManager + 0x48: 0x{listener:X} ({get_class_name(pid, listener)})")
        for off in range(0x18, 0x80, 8):
            val = read_u64(pid, login_mgr + off)
            cname = get_class_name(pid, val) if val > 0x10000 else ""
            if "Listener" in cname or "Login" in cname or "Transformers" in cname:
                print(f"  FOUND LISTENER at +0x{off:02X}: 0x{val:X} ({cname})")
                listener = val

        if listener:
            boot_ready = read_u8(pid, listener + 0x30)
            pre_ready = read_u8(pid, listener + 0x31)
            sel_ready = read_u8(pid, listener + 0x32)
            log_ready = read_u8(pid, listener + 0x33)
            restart = read_u8(pid, listener + 0x34)
            gdpr = read_u8(pid, listener + 0x35)
            print(f"  Listener fields:")
            print(f"    _bootflowReady (0x30): {boot_ready}")
            print(f"    _readyForPreLogin (0x31): {pre_ready}")
            print(f"    _readyForSelectNewOrContinue (0x32): {sel_ready}")
            print(f"    _readyForLogin (0x33): {log_ready}")
            print(f"    _isRestarting (0x34): {restart}")
            print(f"    _showGPDR (0x35): {gdpr}")
