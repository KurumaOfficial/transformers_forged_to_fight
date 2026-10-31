import subprocess, struct, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ADB = r".\work\platform-tools\adb.exe"
PID = "7660"
TARGET = 0x7798B7456A20

maps = subprocess.run([ADB, "shell", f"su 0 cat /proc/{PID}/maps"], capture_output=True, text=True).stdout
regions = []
for line in maps.splitlines():
    m = re.match(r"([0-9a-f]+)-([0-9a-f]+) rw-p", line)
    if not m:
        continue
    start, end = int(m.group(1), 16), int(m.group(2), 16)
    if start <= TARGET < end:
        regions.append((start, end, line))

def read_region(start, end):
    size = end - start
    p = subprocess.run([ADB, "exec-out", "su", "0", "dd", f"if=/proc/{PID}/mem",
                        "bs=1", f"count={size}", f"skip={start}"], capture_output=True)
    return p.stdout

def u64buf(buf, off):
    return struct.unpack_from("<Q", buf, off)[0]

def name_of(addr):
    # read class pointer and class name via small adb reads
    def u64(a):
        p = subprocess.run([ADB, "exec-out", "su", "0", "dd", f"if=/proc/{PID}/mem",
                            "bs=1", "count=8", f"skip={a}"], capture_output=True)
        return struct.unpack("<Q", p.stdout)[0] if len(p.stdout) == 8 else 0
    def cstr(a, n=80):
        p = subprocess.run([ADB, "exec-out", "su", "0", "dd", f"if=/proc/{PID}/mem",
                            "bs=1", f"count={n}", f"skip={a}"], capture_output=True)
        return p.stdout.split(b"\x00")[0].decode("latin1", "replace")
    cls = u64(addr)
    if not cls:
        return "?"
    np = u64(cls + 0x10)
    return cstr(np) if np else "?"
for start, end, line in regions:
    print("REGION", hex(start), hex(end), end-start, line)
    buf = read_region(start, end)
    print("read", len(buf))
    needle = struct.pack("<Q", TARGET)
    hits = []
    pos = 0
    while True:
        pos = buf.find(needle, pos)
        if pos < 0:
            break
        hits.append(start + pos)
        pos += 1
    print("pointer hits", len(hits), [hex(h) for h in hits[:20]])
    for h in hits[:40]:
        # PrefightScreenData._activeQuest is at +0x50
        for off in (0x28, 0x30, 0x50):
            obj = h - off
            if obj < start:
                continue
            try:
                nm = name_of(obj)
            except Exception:
                continue
            if nm and nm not in ("?", "System.String"):
                print(f"  candidate obj 0x{obj:x} off -0x{off:x} class {nm}")
