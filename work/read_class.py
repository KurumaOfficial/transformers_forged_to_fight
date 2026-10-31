import subprocess, struct

def run_adb(cmd):
    p = subprocess.run(['work\\platform-tools\\adb.exe', 'shell', f'su 0 sh -c "{cmd}"'], capture_output=True, text=True)
    return p.stdout.strip()

def read_mem(pid, addr, size):
    out = run_adb(f'dd if=/proc/{pid}/mem bs=1 count={size} skip={addr} 2>/dev/null | xxd -p')
    clean = ''.join(out.split())
    return bytes.fromhex(clean) if clean else b''

pid = 11316
base = 0x75b9cb15e000
slot = struct.unpack('<Q', read_mem(pid, base + 0x2bf0c98, 8))[0]
print(f'slot: 0x{slot:X}')
if slot < base:
    slot = base + slot
klass = struct.unpack('<Q', read_mem(pid, slot, 8))[0]
print(f'klass: 0x{klass:X}')
name_ptr = struct.unpack('<Q', read_mem(pid, klass + 0x10, 8))[0]
name = read_mem(pid, name_ptr, 64).split(b'\x00')[0].decode('utf-8')
print(f'name: {name}')
static_fields = struct.unpack('<Q', read_mem(pid, klass + 0xb8, 8))[0]
print(f'static_fields: 0x{static_fields:X}')
# Read fields at 0x300, 0x310, 0x318, etc. from static_fields
for off in [0x300, 0x308, 0x310, 0x318, 0x320, 0x328, 0x330]:
    val = struct.unpack('<Q', read_mem(pid, static_fields + off, 8))[0]
    # If val is a string pointer (Il2CppString: length at 0x10, chars at 0x14)
    if val:
        slen = struct.unpack('<I', read_mem(pid, val + 0x10, 4))[0]
        if 0 < slen < 100:
            sbytes = read_mem(pid, val + 0x14, slen * 2)
            sval = sbytes.decode('utf-16le', errors='replace')
            print(f'  +0x{off:X}: 0x{val:X} -> string "{sval}"')
        else:
            print(f'  +0x{off:X}: 0x{val:X}')
    else:
        print(f'  +0x{off:X}: 0x0')
