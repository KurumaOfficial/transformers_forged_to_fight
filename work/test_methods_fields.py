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
field_offset = 6867340

# Test first 10 methods
print("First 10 methods:")
for i in range(10):
    pos = method_offset + i * 32
    vals = struct.unpack("<6I2H2H", data[pos:pos+32])
    name = get_string(vals[0])
    param_count = vals[7]
    print(f"  Method {i}: {name} (params: {param_count})")

# Test fields:
# Il2CppFieldDefinition in v24-v27 is 12 bytes:
# nameIndex (int32)
# typeIndex (int32)
# token (uint32)
# Let's check field_size: 704676 / 12 = 58723 fields!
field_count = 704676 // 12
print(f"\nTotal fields: {field_count}")
print("First 10 fields:")
for i in range(10):
    pos = field_offset + i * 12
    vals = struct.unpack("<3I", data[pos:pos+12])
    name = get_string(vals[0])
    print(f"  Field {i}: {name}")
