with open('work/il2cpp_dump/dump.cs', 'r', encoding='utf-8', errors='ignore') as f:
    dump = f.read()

import re
m = re.search(r'class User\s*:[^{]*\{[\s\S]*?\n\}', dump)
if m:
    print(m.group(0)[:1500])
