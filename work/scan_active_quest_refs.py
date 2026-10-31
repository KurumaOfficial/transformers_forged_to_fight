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
    if 0 < end - start <= 30 * 1024 * 1024:
        regions.append((start, end))
print("regions", len(regions))
needle = struct.pack("<Q", TARGET)
allhits = []
for start, end in regions:
    size = end - start
    p = subprocess.run([ADB, "exec-out", "su", "0", "dd", f"if=/proc/{PID}/mem",
                        "bs=1", f"count={size}", f"skip={start}"], capture_output=True)
    b = p.stdout
    if len(b) < 8:
        continue
    hits = []
    i = 0
    while True:
        i = b.find(needle, i)
        if i < 0:
            break
        hits.append(start + i)
        i += 1
    if hits:
        print("REGION", hex(start), hex(end), "hits", [hex(x) for x in hits[:20]])
        allhits += hits
print("TOTAL", len(allhits))
