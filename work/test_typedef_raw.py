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

typedef_offset = 8267048

# Let's inspect type 0, 1, 2, ...
for i in range(10):
    pos = typedef_offset + i * 88
    vals = struct.unpack("<22I", data[pos:pos+88])
    name = get_string(vals[0])
    ns = get_string(vals[1])
    print(f"Type {i}: {ns}.{name}")
    print(f"  vals: {vals}")
