import os, re, json
root = r'.\work\unpacked\assets\bin\Data'
out = {}
pat = re.compile(rb'\{"k":"([^"]+)","v":"((?:\\.|[^"\\])*)"')
for f in os.listdir(root):
    p = os.path.join(root, f)
    if not os.path.isfile(p):
        continue
    try:
        b = open(p, 'rb').read()
    except Exception:
        continue
    for m in pat.finditer(b):
        try:
            k = m.group(1).decode('utf-8', 'replace')
            v = m.group(2).decode('utf-8', 'replace')
            v = v.replace('\\"', '"').replace('\\n', '\n')
            if k not in out:
                out[k] = v
        except Exception:
            pass
json.dump(out, open(r'.\work\localization_all.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('keys', len(out))
for k, v in out.items():
    if any(x in k.upper() for x in ('ACT', 'CHAPTER', 'STORY', 'QUEST')) and len(v) < 200:
        print(k, '=', v[:160])
