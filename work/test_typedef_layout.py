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
# Let's inspect first few types of Assembly-CSharp (start = 8132)
print("Assembly-CSharp Sample Types:")
for i in range(8132, 8160):
    pos = typedef_offset + i * 88
    # 22 32-bit ints
    fields = struct.unpack("<22I", data[pos:pos+88])
    name = get_string(fields[0])
    ns = get_string(fields[1])
    field_start = fields[11]
    method_start = fields[12]
    # packed counts:
    m_count = fields[19] & 0xFFFF
    p_count = (fields[19] >> 16) & 0xFFFF
    f_count = fields[20] & 0xFFFF
    e_count = (fields[20] >> 16) & 0xFFFF
    print(f"Type {i:5d}: {ns}.{name} (Methods: {m_count}, Fields: {f_count}, Props: {p_count})")
