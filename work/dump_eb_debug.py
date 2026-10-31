import subprocess
import struct

def run_adb(cmd):
    full_cmd = f"work\\platform-tools\\adb.exe shell \"{cmd}\""
    p = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    return p.stdout.strip()

def read_mem(addr, size):
    hex_str = run_adb(f"xxd -p -s +0x{addr:x} -l {size} /proc/7192/mem")
    clean = "".join(hex_str.split())
    if not clean:
        return b""
    return bytes.fromhex(clean)

buf_obj = 0x75891005e390
raw_obj = read_mem(buf_obj, 32)
array_ptr, head, tail = struct.unpack("<QII", raw_obj[0x10:0x20])
print(f"array_ptr: 0x{array_ptr:x}, head: {head}, tail: {tail}")

raw_arr = read_mem(array_ptr, 40)
arr_len = struct.unpack("<Q", raw_arr[0x18:0x20])[0]
print(f"array max_length: {arr_len}")

# Let's read all element pointers
count_to_read = min(arr_len, 500)
elements_raw = read_mem(array_ptr + 0x20, count_to_read * 8)
ptrs = [struct.unpack("<Q", elements_raw[i*8:(i+1)*8])[0] for i in range(count_to_read)]

print(f"Total element pointers: {len(ptrs)}")

messages = []
for p in ptrs:
    if p != 0:
        str_hdr = read_mem(p, 24)
        if len(str_hdr) >= 24:
            str_len = struct.unpack("<i", str_hdr[0x10:0x14])[0]
            if 0 < str_len < 2000:
                chars_raw = read_mem(p + 0x14, str_len * 2)
                try:
                    s = chars_raw.decode("utf-16le", errors="replace")
                    messages.append(s)
                except Exception:
                    pass

print(f"Extracted {len(messages)} log messages from EB.Debug._buffer:")
for i, m in enumerate(messages):
    print(f"[{i}] {m}")
