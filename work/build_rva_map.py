import re, json, sys

DUMP = r".\work\il2cpp_dump\dump.cs"
OUT = r".\work\rva_map.json"

lines = open(DUMP, encoding="utf-8", errors="replace").read().splitlines()
m = {}
cur_class = ""
cur_ns = ""
class_re = re.compile(r"^(?:public|private|internal|protected)?\s*(?:sealed\s+|abstract\s+|static\s+)*class\s+([A-Za-z0-9_<>,.`\[\] ]+)")
rva_re = re.compile(r"// RVA: (0x[0-9A-Fa-f]+) Offset:")
for i, line in enumerate(lines):
    s = line.strip()
    cm = class_re.match(s)
    if cm:
        cur_class = cm.group(1).split("//")[0].strip()
    rm = rva_re.search(line)
    if rm:
        addr = int(rm.group(1), 16)
        for j in range(i + 1, min(i + 4, len(lines))):
            d = lines[j].strip()
            if d and not d.startswith("["):
                mm = re.match(r"^(?:public|private|internal|protected|static|virtual|override|sealed|abstract|extern|new|\s)+(.+?)\s*\(([^)]*)\)\s*\{\s*\}$", d)
                name = d.split("(")[0].strip()
                m[str(addr)] = {"class": cur_class, "decl": d, "name": name}
                break

json.dump(m, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
print(f"methods mapped: {len(m)}")
