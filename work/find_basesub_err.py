import struct
import capstone

ELF_PATH = 'work/unpacked/lib/arm64-v8a/libil2cpp.so'
with open(ELF_PATH, 'rb') as f:
    elf_data = f.read()

# Let's search for references to 0x2D6B810
# In ARM64:
# adrp xd, page
# add xd, xd, offset  OR  ldr xd, [xd, offset]
target_addr = 0x2D6B810
target_page = target_addr & ~0xFFF
target_off = target_addr & 0xFFF

print(f"Target addr: 0x{target_addr:X}, Page: 0x{target_page:X}, Off: 0x{target_off:X}")

# We can also search in stringliteral.json for which entry has address 0x2D6B810
import json
with open('work/il2cpp_dump/stringliteral.json', 'r', encoding='utf-8') as f:
    sl = json.load(f)

for s in sl:
    if s.get('address') == '0x2D6B810':
        print("Found in stringliteral.json:", s)

with open('work/il2cpp_dump/script.json', 'r', encoding='utf-8') as f:
    script = json.load(f)

for m in script.get('ScriptString', []):
    if m.get('Address') == 0x2D6B810 or m.get('Value') == target_addr:
        print("Found in ScriptString:", m)
