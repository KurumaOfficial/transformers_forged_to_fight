import os

keywords = ['user_base', 'category', 'placement', 'nodes']
found = 0
for root, dirs, files in os.walk('work/unpacked/assets'):
    for f in files:
        if f.endswith(('.json', '.txt', '.bytes', '.xml', '.csv')):
            fp = os.path.join(root, f)
            try:
                with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
                    content = fh.read()
                    matches = [kw for kw in keywords if kw in content]
                    if len(matches) >= 2:
                        print(f"{fp}: {matches}")
                        found += 1
                        if found > 20: break
            except Exception:
                pass
    if found > 20: break
