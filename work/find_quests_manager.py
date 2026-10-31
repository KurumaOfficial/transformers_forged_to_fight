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

def read_u32(pid, addr):
    d = read_mem(pid, addr, 4)
    return struct.unpack('<I', d)[0] if len(d) == 4 else 0

def read_u8(pid, addr):
    d = read_mem(pid, addr, 1)
    return d[0] if len(d) == 1 else 0

def read_cs_str(pid, addr):
    if not addr: return ""
    slen = read_u32(pid, addr + 0x10)
    if not slen or slen > 128: return ""
    raw = read_mem(pid, addr + 0x14, slen * 2)
    return raw.decode('utf-16le', errors='replace')

pid = 12670

# Search for string literal "story_act_1" in heap
maps = run_adb(f"grep 'rw-p' /proc/{pid}/maps | grep -v 'lib' | grep -v 'apk'").splitlines()
print(f"Scanning {len(maps)} rw-p ranges for 'story_act_1'...")

# "story_act_1" in UTF-16LE:
needle = "story_act_1".encode('utf-16le').hex()

found_addrs = []
for m in maps:
    parts = m.split()
    if not parts: continue
    start, end = [int(x, 16) for x in parts[0].split('-')]
    size = end - start
    if size > 10 * 1024 * 1024: continue # skip giant maps
    # Search with grep or python
    cmd = f"dd if=/proc/{pid}/mem bs=1 count={size} skip={start} 2>/dev/null | grep -b -o -a -F $(printf '{needle}' | sed 's/../\\\\x&/g') | head -n 5"
    res = run_adb(cmd)
    if res:
        for line in res.splitlines():
            offset = int(line.split(':')[0])
            addr = start + offset
            print(f"Found 'story_act_1' at 0x{addr:X}")
            found_addrs.append(addr)

print("Found total:", len(found_addrs))
# Check if any address is inside a QuestSet (which has setId at offset 0x40)
for a in found_addrs:
    # If a is an Il2CppString, string object starts at a - 0x14
    str_obj = a - 0x14
    # Scan memory for pointers to str_obj
    str_obj_hex = struct.pack('<Q', str_obj).hex()
    print(f"Looking for pointers to str_obj 0x{str_obj:X}...")
    # QuestSet has setId at 0x40. So QuestSet would start at ptr_addr - 0x40
    # Let's check with grep
