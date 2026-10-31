import subprocess, struct, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ADB = r".\work\platform-tools\adb.exe"
PID = subprocess.run([ADB, "shell", "pidof com.kabam.bigrobot"], capture_output=True, text=True).stdout.strip()
elf = open(r".\work\unpacked\lib\arm64-v8a\libil2cpp.so", "rb").read()
e_phoff = struct.unpack_from("<Q", elf, 32)[0]; e_phentsize = struct.unpack_from("<H", elf, 54)[0]; e_phnum = struct.unpack_from("<H", elf, 56)[0]
wv = None
for i in range(e_phnum):
    o = e_phoff + i * e_phentsize; t, fl, fo, va, pa, fs, ms, al = struct.unpack_from("<IIQQQQQQ", elf, o)
    if t == 1 and (fl & 2): wv = va
maps = subprocess.run([ADB, "shell", f"su 0 cat /proc/{PID}/maps"], capture_output=True, text=True).stdout
BASE = None
for line in maps.splitlines():
    if "libil2cpp.so" in line and "rw-p" in line:
        BASE = int(line.split("-")[0], 16) - wv; break

def mem(a, n=8):
    p = subprocess.run([ADB, "shell", f"su 0 dd if=/proc/{PID}/mem bs=1 count={n} skip={a} 2>/dev/null | xxd -p"], capture_output=True, text=True)
    h = "".join(p.stdout.split())
    return bytes.fromhex(h) if h and re.fullmatch(r"[0-9a-fA-F]+", h) else b""
def cstr(p, n=120):
    b = mem(p, n); return b.split(b"\x00")[0].decode("latin1", "replace") if b else None
def ilstr(p, n=120):
    if not p: return None
    b = mem(p+0x10, 4)
    if len(b)<4: return None
    ln=struct.unpack('<I',b)[0]
    if ln>n: return None
    b=mem(p+0x14, ln*2)
    return b.decode('utf-16-le','replace') if b else None
slot = BASE + 0x2C33650
p1 = struct.unpack('<Q', mem(slot,8))[0]
print('p1',hex(p1))
raw = mem(p1-0x20, 0x140)
for off in range(0, len(raw), 8):
    v=struct.unpack_from('<Q',raw,off)[0]
    addr=p1-0x20+off
    print(f'{addr:#x} (+{addr-p1:+#x}) = {v:#x}')
print('\nobject at p1[0]')
p2 = struct.unpack_from('<Q', raw, 0x20)[0]
raw2 = mem(p2, 0x100)
for off in range(0,len(raw2),8):
    v=struct.unpack_from('<Q',raw2,off)[0]
    print(f'{p2+off:#x} = {v:#x}')
print('\nobject at sf 0x77222dee1f90')
sf=0x77222dee1f90
raw3=mem(sf,0x60)
for off in range(0,len(raw3),8):
    v=struct.unpack_from('<Q',raw3,off)[0]
    print(f'{sf+off:#x} = {v:#x}')
