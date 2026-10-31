with open('work/il2cpp_dump/dump.cs', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if any(k in l for k in ['class TcpClientSSL', 'class EndPoint', 'class Request', 'class NetworkConfig', 'class SparxHub', 'class RestClient']):
        if not 'CompilerGenerated' in l:
            print(f"Line {i+1}: {l.strip()}")
