import struct

path = r'work\unpacked\assets\bin\Data\e1917cd7a6bdb4492a247b8f758df2ae'
with open(path, 'rb') as f:
    data = f.read()

print("Total file length:", len(data))

# Find 'endpointconfig'
name_pos = data.find(b'endpointconfig')
name_len = struct.unpack('<I', data[name_pos-4:name_pos])[0]
print(f"Name pos: {name_pos}, Name len: {name_len}")

# Aligned index for m_Script
script_idx = name_pos + name_len
script_idx = (script_idx + 3) & ~3
script_len = struct.unpack('<I', data[script_idx:script_idx+4])[0]
script_data = data[script_idx+4 : script_idx+4+script_len]
print(f"Script idx: {script_idx}, Script len: {script_len}")
print(f"Script content: {script_data.decode('utf-8', errors='ignore')}")

# Padding
padded_end = (script_idx + 4 + script_len + 3) & ~3
print(f"Padded end: {padded_end}, File end: {len(data)}")
print(f"Trailer bytes: {data[script_idx+4+script_len:].hex()}")
