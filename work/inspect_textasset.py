import struct

path = 'work/unpacked/assets/bin/Data/e1917cd7a6bdb4492a247b8f758df2ae'
with open(path, 'rb') as f:
    data = f.read()

print(f"File size: {len(data)}")

# TextAsset in Unity:
# string m_Name
# string m_Script (bytes)
# Let's find "endpointconfig"
name_idx = data.find(b'endpointconfig')
print("endpointconfig index:", name_idx)
# length before name:
name_len = struct.unpack('<I', data[name_idx-4:name_idx])[0]
print("Name len:", name_len)

# after name: 4-byte aligned
script_idx = name_idx + name_len
script_idx = (script_idx + 3) & ~3
script_len = struct.unpack('<I', data[script_idx:script_idx+4])[0]
print(f"Script idx: {script_idx}, Script len: {script_len}")
script_bytes = data[script_idx+4:script_idx+4+script_len]
print("Script content:", script_bytes.decode('utf-8', errors='ignore'))
print("Bytes after script:", len(data) - (script_idx + 4 + script_len))
