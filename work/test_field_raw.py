import struct

meta_path = r".\work\unpacked\assets\bin\Data\Managed\Metadata\global-metadata.dat"

with open(meta_path, "rb") as f:
    data = f.read()

string_offset = 738752
string_size = 1547968

def get_string(idx):
    if idx < 0 or idx >= string_size:
        return ""
    pos = string_offset + idx
    end = data.find(b"\x00", pos)
    if end == -1:
        return ""
    return data[pos:end].decode("utf-8", errors="ignore")

field_offset = 6867340
# Inspect fields 0 to 10
for i in range(10):
    pos = field_offset + i * 12
    vals = struct.unpack("<3I", data[pos:pos+12])
    name = get_string(vals[0])
    print(f"Field {i}: {name}, vals: {vals}")
