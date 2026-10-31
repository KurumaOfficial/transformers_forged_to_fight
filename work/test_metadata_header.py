import struct
import os

meta_path = r".\work\unpacked\assets\bin\Data\Managed\Metadata\global-metadata.dat"

with open(meta_path, "rb") as f:
    data = f.read()

print(f"File size: {len(data)}")

header = struct.unpack("<28I", data[:112])
magic = header[0]
version = header[1]

print(f"Magic: 0x{magic:08X}")
print(f"Version: {version}")

# Print table offsets and counts
table_names = [
    "stringLiteral", "stringLiteralData", "string", "events", "properties",
    "methods", "parameterDefaultValues", "fieldDefaultValues", "fieldAndParameterDefaultValueData",
    "fieldMarshaledSizes", "parameters", "fields", "genericParameters",
    "genericParameterConstraints", "genericContainers", "nestedTypes", "interfaces",
    "vtableMethods", "interfaceOffsets", "typeDefinitions", "images", "assemblies",
    "fieldRefs", "referencedAssemblies", "attributeData", "attributeDataRange",
    "unresolvedVirtualCallParameterTypes", "unresolvedVirtualCallParameterRanges"
]

idx = 2
for name in table_names:
    if idx + 1 < len(header):
        offset = header[idx]
        size = header[idx+1]
        print(f"  {name:30s}: offset=0x{offset:08X} ({offset:9d}), size=0x{size:08X} ({size:9d})")
        idx += 2
