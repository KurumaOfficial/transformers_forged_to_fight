with open('work/il2cpp_dump/dump.cs', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if any(k in l for k in ['class LoginManager', 'class LoginService', 'class LoginController', 'class SparxHub']):
        print(f"Line {i+1}: {l.strip()}")
