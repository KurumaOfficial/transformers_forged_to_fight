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

method_offset = 2571416
# Let's inspect methods 0, 1, 2, 3, 4
for i in range(10):
    pos = method_offset + i * 32
    vals = struct.unpack("<8I", data[pos:pos+32])
    name = get_string(vals[0])
    # print raw vals
    print(f"Method {i}: {name}, vals: {vals}")
