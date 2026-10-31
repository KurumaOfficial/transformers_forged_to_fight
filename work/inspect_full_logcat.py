with open('work/logcat_full.txt', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

print(f"Total lines in full logcat: {len(lines)}")
target_idx = -1
for i, l in enumerate(lines):
    if 'LoginManager+<>c__DisplayClass74_1' in l:
        target_idx = i
        break

if target_idx != -1:
    print("Found crash in full logcat! Context:")
    for j in range(max(0, target_idx - 30), min(len(lines), target_idx + 40)):
        print(lines[j], end='')
else:
    print("Crash line not found directly, showing lines with NullReferenceException:")
    for l in lines:
        if 'NullReferenceException' in l:
            print(l.strip())
