import subprocess
import struct

def run_adb(cmd):
    full_cmd = f"work\\platform-tools\\adb.exe shell \"{cmd}\""
    p = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    return p.stdout.strip()

# Let's inspect maps
maps = run_adb("grep -E 'libil2cpp.so' /proc/7192/maps")
print("Maps:")
print(maps)

# Let's find rw mapping
rw_base = None
rw_file_offset = None
for line in maps.splitlines():
    parts = line.split()
    if len(parts) >= 6 and 'rw-p' in parts[1]:
        start, end = parts[0].split('-')
        rw_base = int(start, 16)
        rw_file_offset = int(parts[2], 16)
        break

print(f"rw_base: 0x{rw_base:x}, rw_file_offset: 0x{rw_file_offset:x}")

# Pointer slot is at file offset 0x2c2ea10
slot_vaddr = rw_base + (0x2c2ea10 - rw_file_offset)
print(f"slot_vaddr: 0x{slot_vaddr:x}")

# Let's read 64 bytes at slot_vaddr via dd
dd_out = run_adb(f"dd if=/proc/7192/mem bs=1 count=16 skip={slot_vaddr} 2>/dev/null | xxd -p")
print("slot hex:", dd_out)

if dd_out:
    raw = bytes.fromhex(dd_out)
    ptr1 = struct.unpack("<Q", raw[:8])[0]
    print(f"ptr1: 0x{ptr1:x}")
    if ptr1:
        dd_out2 = run_adb(f"dd if=/proc/7192/mem bs=1 count=16 skip={ptr1} 2>/dev/null | xxd -p")
        raw2 = bytes.fromhex(dd_out2)
        typeinfo = struct.unpack("<Q", raw2[:8])[0]
        print(f"typeinfo: 0x{typeinfo:x}")
        if typeinfo:
            # static fields is at typeinfo + 0xb8
            dd_sf = run_adb(f"dd if=/proc/7192/mem bs=1 count=16 skip={typeinfo + 0xb8} 2>/dev/null | xxd -p")
            raw_sf = bytes.fromhex(dd_sf)
            sf = struct.unpack("<Q", raw_sf[:8])[0]
            print(f"static_fields: 0x{sf:x}")
            if sf:
                # _buffer is at static_fields + 0x30
                dd_buf = run_adb(f"dd if=/proc/7192/mem bs=1 count=16 skip={sf + 0x30} 2>/dev/null | xxd -p")
                raw_buf = bytes.fromhex(dd_buf)
                buf_obj = struct.unpack("<Q", raw_buf[:8])[0]
                print(f"CircularBuffer obj: 0x{buf_obj:x}")
