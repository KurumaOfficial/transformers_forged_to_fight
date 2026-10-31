import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

lib_dir = r".\work\unpacked\lib\arm64-v8a"

so_files = ["libapkprotect.so", "libnms.so", "libkrash.so", "libenetlib.so", "libbuffer_pg.so", "libfile_lock_pg.so"]

for so in so_files:
    fp = os.path.join(lib_dir, so)
    if os.path.exists(fp):
        sz = os.path.getsize(fp)
        with open(fp, "rb") as f:
            data = f.read()
        print(f"\n==========================================")
        print(f"{so} ({sz} bytes)")
        # find readable strings >= 6 chars
        strings = re.findall(b'[\x20-\x7e]{6,}', data)
        interesting = []
        for s in strings:
            st = s.decode('ascii', errors='ignore')
            if any(k in st.lower() for k in ["jni", "java", "protect", "check", "root", "hook", "kabam", "krash", "net", "debug", "sig", "hash", "tamper", "verify"]):
                interesting.append(st)
        print(f"Total strings: {len(strings)}, Interesting: {len(interesting)}")
        for st in interesting[:25]:
            print(f"  {st}")
