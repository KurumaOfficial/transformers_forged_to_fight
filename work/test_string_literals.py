import struct

meta_path = r".\work\unpacked\assets\bin\Data\Managed\Metadata\global-metadata.dat"

with open(meta_path, "rb") as f:
    data = f.read()

lit_offset = 256
lit_size = 194968
data_offset = 195224
data_size = 543528

count = lit_size // 8
print(f"Total string literals: {count}")

literals = []
for i in range(count):
    length, off = struct.unpack("<2i", data[lit_offset + i*8 : lit_offset + (i+1)*8])
    if 0 <= off < data_size:
        str_bytes = data[data_offset + off : data_offset + off + length]
        s = str_bytes.decode("utf-8", errors="ignore")
        literals.append(s)

print("First 20 string literals:")
for s in literals[:20]:
    print(f"  {repr(s)}")

# Search for network, api, auth, combat, bot, quest keywords
keywords = ["http", "login", "auth", "request", "response", "combat", "damage", "bot", "roster", "quest", "mission", "cheat", "license", "cert", "pinning"]
print("\nKeyword samples in string literals:")
for kw in keywords:
    matches = [s for s in literals if kw.lower() in s.lower()]
    print(f"  Keyword '{kw}': {len(matches)} matches (e.g. {matches[:3]})")
