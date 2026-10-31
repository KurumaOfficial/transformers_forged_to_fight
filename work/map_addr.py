import re, sys

DUMP = r".\work\il2cpp_dump\dump.cs"
targets = set()
for a in sys.argv[1:]:
    targets.add(int(a, 0))

# parse "// RVA: 0xADDR Offset: ..." followed by declaration line
cur = None
found = {}
lines = open(DUMP, encoding="utf-8", errors="replace").read().splitlines()
for i, line in enumerate(lines):
    m = re.search(r"// RVA: (0x[0-9A-Fa-f]+) Offset:", line)
    if m:
        cur = int(m.group(1), 16)
        # declaration is the next non-empty, non-attribute line
        for j in range(i + 1, min(i + 4, len(lines))):
            s = lines[j].strip()
            if s and not s.startswith("["):
                if cur in targets:
                    # find enclosing class backwards
                    cls = ""
                    for k in range(i - 1, max(0, i - 400), -1):
                        if re.match(r"^(public|private|internal|protected)?\s*(sealed\s+)?class\s", lines[k].strip()):
                            cls = lines[k].strip()
                            break
                    found[cur] = (cls, s, j + 1)
                break

for a in sorted(targets):
    if a in found:
        cls, decl, ln = found[a]
        print(f"{a:#x}  [{ln}]  {cls}  ::  {decl}")
    else:
        print(f"{a:#x}  NOT FOUND")
