import subprocess
import struct

def run_adb(cmd):
    p = subprocess.run(f"work\\android-sdk\\platform-tools\\adb.exe shell \"{cmd}\"",
                       shell=True, capture_output=True, text=True)
    return p.stdout.strip()

def main():
    pid = 5033
    maps_out = run_adb(f"cat /proc/{pid}/maps")
    
    needle_u16 = "Sparx Fatal Error:".encode('utf-16le')
    needle_u8 = "Sparx Fatal Error:".encode('utf-8')
    
    for line in maps_out.splitlines():
        parts = line.split()
        if len(parts) >= 2 and 'rw-p' in parts[1]:
            # skip files that are not heap/anon
            name = parts[-1] if len(parts) >= 6 else ""
            if name.endswith('.so') or name.endswith('.apk') or name.endswith('.dex'):
                continue
            addr_range = parts[0]
            start_hex, end_hex = addr_range.split('-')
            start = int(start_hex, 16)
            end = int(end_hex, 16)
            size = end - start
            if size > 16 * 1024 * 1024:
                continue
            # Search in chunks on the emulator directly!
            # We can use grep on the emulator!
            cmd = f"dd if=/proc/{pid}/mem bs=1 count={size} skip={start} 2>/dev/null | grep -b -a -F 'Sparx Fatal Error'"
            res = run_adb(cmd)
            if res:
                print(f"FOUND in region {start_hex}-{end_hex} ({name}):")
                print(res)
                # Let's dump surrounding bytes
                for match_line in res.splitlines():
                    match_off = match_line.split(':')[0]
                    try:
                        byte_off = int(match_off)
                        exact_mem = start + byte_off
                        dump = run_adb(f"dd if=/proc/{pid}/mem bs=1 count=256 skip={exact_mem} 2>/dev/null | xxd -p")
                        clean = bytes.fromhex("".join(dump.split()))
                        print("UTF-8:", repr(clean.decode('utf-8', errors='replace')[:150]))
                        print("UTF-16LE:", repr(clean.decode('utf-16le', errors='replace')[:150]))
                    except Exception as e:
                        print("Error reading exact:", e)

if __name__ == "__main__":
    main()
