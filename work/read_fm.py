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

pid = 12670
base = 0x75b9cad5e000
slot_off = 0x2BFCE18
slot = read_u64(pid, base + slot_off)
print(f"slot at 0x{slot_off:X}: 0x{slot:X}")
if slot < base:
    slot = base + slot
klass = read_u64(pid, slot)
print(f"klass: 0x{klass:X}")
if klass:
    static_fields = read_u64(pid, klass + 0xB8)
    print(f"static_fields: 0x{static_fields:X}")
    if static_fields:
        inst = read_u64(pid, static_fields)
        print(f"FlowManager.Instance: 0x{inst:X}")
