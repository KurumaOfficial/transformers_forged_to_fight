import subprocess
import struct

def run_adb(cmd):
    p = subprocess.run(f'work\\android-sdk\\platform-tools\\adb.exe shell "{cmd}"',
                       shell=True, capture_output=True, text=True)
    return p.stdout.strip()

def read_mem(pid, addr, size):
    cmd = f'dd if=/proc/{pid}/mem bs=1 count={size} skip={addr} 2>/dev/null | xxd -p'
    out = run_adb(cmd)
    clean = ''.join(out.split())
    if not clean:
        return b''
    try:
        return bytes.fromhex(clean)
    except Exception:
        return b''

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

pid = 6372
base = 0x7d226d1d4000
slot = read_u64(pid, base + 0x2c14120)
print(f'Slot at base+0x2c14120: 0x{slot:X}')
klass = read_u64(pid, slot)
print(f'Klass: 0x{klass:X}')
static_fields = read_u64(pid, klass + 0xb8)
print(f'Static fields: 0x{static_fields:X}')
instance = read_u64(pid, static_fields)
print(f'GameboardManager.Instance: 0x{instance:X}')

if instance:
    quest_ready = read_u8(pid, instance + 0x60)
    base_ready = read_u8(pid, instance + 0x61)
    raid_ready = read_u8(pid, instance + 0x62)
    base_board = read_u64(pid, instance + 0x30)
    print(f'  _questNodeTuningReady (0x60): {quest_ready}')
    print(f'  _baseNodeTuningReady (0x61): {base_ready}')
    print(f'  _raidTutorialCompleteOnBaseLoad (0x62): {raid_ready}')
    print(f'  _baseBoard (0x30): 0x{base_board:X}')
