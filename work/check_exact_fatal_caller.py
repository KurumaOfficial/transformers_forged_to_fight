import subprocess

def run_adb(cmd):
    p = subprocess.run(f"work\\android-sdk\\platform-tools\\adb.exe shell \"{cmd}\"",
                       shell=True, capture_output=True, text=True)
    return p.stdout.strip()

def read_byte(pid, vaddr):
    if vaddr >= 0x2e3c000:
        mem = 0x7e9d4500a000 + (vaddr - 0x2e3c000)
    else:
        mem = 0x7e9d44c75000 + (vaddr - 0x2aa7000)
        
    cmd = f"dd if=/proc/{pid}/mem bs=1 count=1 skip={mem} 2>/dev/null | xxd -p"
    out = run_adb(cmd)
    clean = "".join(out.split())
    if clean:
        return int(clean, 16)
    return -1

pid = 5033

flags = [
    (0x2e3e4c6, 'HttpEndPoint.OnComplete'),
    (0x2e3e4e0, 'Hub.SubSystemConnecting'),
    (0x2e3e4e8, 'Hub.<Initialize>b__327_0'),
    (0x2e3ff95, 'FTEFight1LoadState.OnEnter'),
    (0x2e3ff99, 'FTEFight1LoadState.OnAttributesReady'),
    (0x2e41981, 'SaveLoadManager.<DoLoadSingle>b__0'),
    (0x2e3e4d9, 'Hub.FatalError'),
]

print(f"=== Checking Init Flags for Fatal Error Callers in PID {pid} ===")
for vaddr, name in flags:
    val = read_byte(pid, vaddr)
    status = " [!] EXECUTED (1)" if val == 1 else (" [ ] Not executed (0)" if val == 0 else f" (?) {val}")
    print(f"0x{vaddr:X} {name:40s} -> {val:02X}{status}")
