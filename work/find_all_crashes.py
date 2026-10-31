with open('work/logcat_full.txt', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'NullReferenceException' in l:
        print(f"--- Crash #{i} ---")
        for j in range(max(0, i-10), min(len(lines), i+35)):
            print(lines[j], end='')
        print('\n' + '='*50 + '\n')
