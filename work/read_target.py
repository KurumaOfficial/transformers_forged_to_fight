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
target = base + 0x2D32B68
print(f'Reading at target: 0x{target:X}')
data = read_mem(pid, target, 32)
print('Data:', data.hex())
if len(data) >= 8:
    ptr = struct.unpack('<Q', data[:8])[0]
    print(f'Pointer at target: 0x{ptr:X}')
