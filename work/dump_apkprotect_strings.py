import re

for arch in ['arm64-v8a', 'armeabi-v7a']:
    path = f'work/unpacked/lib/{arch}/libapkprotect.so'
    with open(path, 'rb') as f:
        data = f.read()
    strings = re.findall(b'[\x20-\x7e]{4,}', data)
    print(f"=== {arch} ({len(data)} bytes, {len(strings)} strings) ===")
    for s in strings:
        st = s.decode('ascii', errors='ignore')
        # filter noise
        if len(st) > 5 and not st.startswith('$'):
            print(' ', st)
