import os, re
root = r'.\work\unpacked\assets\bin\Data'
pat = re.compile(rb'\{"k":"([^"]+)","v":"((?:\\.|[^"\\])*)"')
total = 0
keys = set()
per = {}
for f in os.listdir(root):
    p = os.path.join(root, f)
    if not os.path.isfile(p):
        continue
    b = open(p, 'rb').read()
    ms = pat.findall(b)
    if ms:
        total += len(ms)
        per[f] = len(ms)
        keys.update(k.decode('utf-8', 'replace') for k, v in ms)
print('total occurrences', total, 'unique keys', len(keys), 'files with entries', len(per))
print(sorted(per.items(), key=lambda x: -x[1])[:10])
