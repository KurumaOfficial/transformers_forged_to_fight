import subprocess
import struct

def run_adb(cmd):
    p = subprocess.run(f"work\\android-sdk\\platform-tools\\adb.exe shell \"{cmd}\"",
                       shell=True, capture_output=True, text=True)
    return p.stdout.strip()

def read_byte(pid, vaddr):
    # rw base is 0x7e9d44c75000 (vaddr 0x2aa7000)
    # anon:.bss base is 0x7e9d4500a000 (vaddr 0x2e3c000)
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
    (0x2e3bf6e, 'PVPManager.<Fetch>b__0'),
    (0x2e3bf6f, 'PVPManager.<Fetch>b__1'),
    (0x2e41075, 'TutorialManager.<Fetch>b__0'),
    (0x2e41076, 'TutorialManager.<Fetch>b__1'),
    (0x2e41322, 'PaymentsManager.OnFetchedPayouts'),
    (0x2e419c0, 'StatsManager.<Fetch>b__0'),
    (0x2e41d5a, 'BCGManagerBase.<Fetch>b__0'),
    (0x2e41d5b, 'BCGManagerBase.<Fetch>b__1'),
    (0x2e4210b, 'AutoRefreshingManager.<CompleteRefresh>b__0'),
    (0x2e423d7, 'TuningManager.OnRefresh'),
    (0x2e43aef, 'AutoRefreshingManager.CompleteRefresh'),
    (0x2e43bfe, 'OffersManager.<Fetch>b__0'),
]

print(f"=== Checking Init Flags for 12 FatalError Callers in PID {pid} ===")
for vaddr, name in flags:
    val = read_byte(pid, vaddr)
    status = " [!] EXECUTED (1)" if val == 1 else (" [ ] Not executed (0)" if val == 0 else f" (?) {val}")
    print(f"0x{vaddr:X} {name:45s} -> {val:02X}{status}")
