with open('work/il2cpp_dump/dump.cs', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'public class Response' in l or 'class Response :' in l:
        for k in range(i, min(len(lines), i + 40)):
            print(f"{k+1}: {lines[k].rstrip()}")
        break
