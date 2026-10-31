with open('work/logcat_filtered.txt', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

print(f"Total lines in logcat_filtered.txt: {len(lines)}")
for line in lines:
    if any(k in line.lower() for k in ['exception', 'fatal', 'error', 'sparx', 'login', 'krash', 'fail']):
        print(line.strip()[:200])
