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

pid = 4204
base = 0x7b686a7d3000

slot = read_u64(pid, base + 0x2D0AD98)
print(f"GDPRHelper slot: 0x{slot:X}")
if slot:
    klass = read_u64(pid, slot)
    print(f"GDPRHelper klass: 0x{klass:X}")
    static_fields = read_u64(pid, klass + 0xB8)
    print(f"GDPRHelper static_fields: 0x{static_fields:X}")
    if static_fields:
        checking = read_u8(pid, static_fields)
        odr = read_u8(pid, static_fields + 1)
        print(f"GDPRHelper.CheckingConsent: {checking}")
        print(f"GDPRHelper._odrBlockerDisabled: {odr}")
