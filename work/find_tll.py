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

tll_klass = read_u64(pid, base + 0x2D0F330)
print(f"TransformersLoginListener klass: 0x{tll_klass:X}")

# Let's search the heap / anon mappings for instances of this klass!
# In /proc/pid/maps, get rw-p anonymous regions
maps_out = run_adb(f"grep 'rw-p' /proc/{pid}/maps | grep -v 'libil2cpp' | grep -v 'base.apk'")
regions = []
for line in maps_out.splitlines():
    parts = line.split()
    if len(parts) >= 2 and parts[1] == 'rw-p':
        start, end = [int(x, 16) for x in parts[0].split('-')]
        regions.append((start, end))

print(f"Total rw regions: {len(regions)}")

# Search for 8-byte pointer equal to tll_klass
tll_klass_hex = struct.pack('<Q', tll_klass).hex()
found_instances = []
for start, end in regions:
    size = end - start
    if size > 30 * 1024 * 1024: # skip huge heaps for speed
        continue
    # Use grep -b -a -P inside adb shell
    # grep -b -a -F in binary
    cmd = f"dd if=/proc/{pid}/mem bs=1 count={size} skip={start} 2>/dev/null | grep -b -a -F $(echo '{tll_klass_hex}' | xxd -r -p)"
    # Alternative: use python xxd search
    pass

