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

# Images table
images_offset = 9454432
images_size = 1960
# In v27, Il2CppImageDefinition structure:
# nameIndex: int32
# assemblyIndex: int32
# typeStart: int32
# typeCount: uint32
# exportedTypeStart: int32
# exportedTypeCount: uint32
# entryPointIndex: int32
# token: uint32
# customAttributeStart: int32
# customAttributeCount: uint32
# Size = 10 * 4 = 40 bytes!
image_count = images_size // 40
print(f"Total Images: {image_count}")
images = []
for i in range(image_count):
    entry = struct.unpack("<10i", data[images_offset + i*40 : images_offset + (i+1)*40])
    name = get_string(entry[0])
    type_start = entry[2]
    type_count = entry[3]
    images.append((name, type_start, type_count))
    print(f"  Image {i:2d}: {name:35s} (Types: {type_count:5d}, Start: {type_start:5d})")
