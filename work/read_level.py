import subprocess, struct

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

def read_u32(pid, addr):
    d = read_mem(pid, addr, 4)
    return struct.unpack('<I', d)[0] if len(d) == 4 else 0

def read_c_str(pid, addr):
    if not addr: return ""
    raw = read_mem(pid, addr, 64)
    return raw.split(b'\x00')[0].decode('utf-8', errors='replace')

pid = 12670
base = 0x75b9cad5e000
slot = read_u64(pid, base + 0x2BC7D18)
print(f"slot: 0x{slot:X}")
if slot < base: slot = base + slot
klass = read_u64(pid, slot)
print(f"klass: 0x{klass:X}")
if klass > base:
    name_ptr = read_u64(pid, klass + 0x10)
    print("Class name:", read_c_str(pid, name_ptr))
    static_fields = read_u64(pid, klass + 0xB8)
    print(f"static_fields: 0x{static_fields:X}")
    if static_fields:
        inst = read_u64(pid, static_fields)
        print(f"inst: 0x{inst:X}")
        if inst:
            inst_klass = read_u64(pid, inst)
            print("Inst class name:", read_c_str(pid, read_u64(pid, inst_klass + 0x10)))
            f40 = read_u64(pid, inst + 0x40)
            print(f"inst+0x40: 0x{f40:X}")
            if f40:
                f40_klass = read_u64(pid, f40)
                print("f40 class name:", read_c_str(pid, read_u64(pid, f40_klass + 0x10)))
                f30 = read_u64(pid, f40 + 0x30)
                print(f"f40+0x30: 0x{f30:X}")
                if f30:
                    f30_klass = read_u64(pid, f30)
                    print("f30 class name:", read_c_str(pid, read_u64(pid, f30_klass + 0x10)))
                    lvl = read_u32(pid, f30 + 0x44)
                    print(f"LEVEL at f30+0x44: {lvl}")
