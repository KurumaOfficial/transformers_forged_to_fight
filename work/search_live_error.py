import subprocess
import re

def run_adb(cmd):
    p = subprocess.run(f"work\\android-sdk\\platform-tools\\adb.exe shell \"{cmd}\"",
                       shell=True, capture_output=True, text=True)
    return p.stdout.strip()

def main():
    pid = 5033
    maps = run_adb(f"cat /proc/{pid}/maps")
    
    # We want rw-p pages that are heap, anon, or scudo
    targets = []
    for line in maps.splitlines():
        parts = line.split()
        if len(parts) >= 2 and 'rw-p' in parts[1]:
            addr_range = parts[0]
            start_hex, end_hex = addr_range.split('-')
            start = int(start_hex, 16)
            end = int(end_hex, 16)
            size = end - start
            name = parts[-1] if len(parts) >= 6 else ""
            if 0 < size <= 32 * 1024 * 1024: # max 32MB per region
                targets.append((start, size, name))
                
    print(f"Total rw regions to scan: {len(targets)}")
    
    # Search for "[SparxHub] Sparx Fatal Error:" in utf-16le or ascii
    needle_u16 = "[SparxHub] Sparx Fatal Error:".encode('utf-16le')
    needle_u8 = "[SparxHub] Sparx Fatal Error:".encode('utf-8')
    needle_sub = "Fatal Error".encode('utf-16le')
    
    found = 0
    for start, size, name in targets:
        # Read chunk via adb
        # Use python to grep or adb to search
        # Since reading all mem over adb is slow, let's use python script directly on the emulator via adb shell python? Emulator doesn't have python.
        # But emulator has grep / xxd / strings!
        pass

if __name__ == "__main__":
    main()
