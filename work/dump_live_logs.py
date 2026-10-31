import subprocess
import struct
import sys

def run_adb(cmd):
    full_cmd = f"work\\android-sdk\\platform-tools\\adb.exe shell \"{cmd}\""
    p = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    return p.stdout.strip()

pid = run_adb('pidof com.kabam.bigrobot').strip()
print('PID:', pid)
if not pid:
    sys.exit(1)

maps = run_adb(f'grep -E "libil2cpp.so" /proc/{pid}/maps')
rw_base = None
rw_file_offset = None
for line in maps.splitlines():
    parts = line.split()
    if len(parts) >= 6 and 'rw-p' in parts[1]:
        start, end = parts[0].split('-')
        rw_base = int(start, 16)
        rw_file_offset = int(parts[2], 16)
        break

print(f'rw_base: 0x{rw_base:x}, rw_file_offset: 0x{rw_file_offset:x}')
slot_vaddr = rw_base + (0x2c2ea10 - rw_file_offset)

def read_mem(addr, size):
    out = run_adb(f'dd if=/proc/{pid}/mem bs=1 count={size} skip={addr} 2>/dev/null | xxd -p')
    clean = ''.join(out.split())
    if not clean: return b''
    return bytes.fromhex(clean)

raw_ptr = read_mem(slot_vaddr, 8)
ptr1 = struct.unpack('<Q', raw_ptr)[0] if raw_ptr else 0
print(f'ptr1: 0x{ptr1:x}')
mem128 = read_mem(ptr1, 128)
print('mem128 at ptr1:')
for i in range(0, len(mem128), 16):
    chunk = mem128[i:i+16]
    hex_s = ' '.join(f'{b:02x}' for b in chunk)
    print(f'  +0x{i:02x}: {hex_s}')
buf_obj = struct.unpack('<Q', read_mem(sf + 0x30, 8))[0]
print(f'buf_obj: 0x{buf_obj:x}')

arr_obj = struct.unpack('<Q', read_mem(buf_obj + 0x10, 8))[0]
head = struct.unpack('<i', read_mem(buf_obj + 0x18, 4))[0]
tail = struct.unpack('<i', read_mem(buf_obj + 0x1c, 4))[0]
print(f'arr_obj: 0x{arr_obj:x}, head={head}, tail={tail}')

arr_len = struct.unpack('<I', read_mem(arr_obj + 0x18, 4))[0]
print(f'arr_len: {arr_len}')

# Let's inspect the last 50 elements before head
indices = []
for i in range(arr_len):
    idx = (tail + i) % arr_len
    indices.append(idx)

# Let's inspect last 30 entries
for idx in indices[-30:]:
    elem_ptr = struct.unpack('<Q', read_mem(arr_obj + 0x20 + idx * 8, 8))[0]
    if elem_ptr != 0:
        str_hdr = read_mem(elem_ptr, 24)
        if len(str_hdr) >= 24:
            slen = struct.unpack('<I', str_hdr[0x10:0x14])[0]
            if 0 < slen < 1000:
                sdata = read_mem(elem_ptr + 0x14, slen * 2)
                s = sdata.decode('utf-16le', errors='replace')
                print(f'[{idx:03d}] {s}')
