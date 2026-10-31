import os

unpacked = r'work\unpacked\assets'
tocs = []
for root, dirs, files in os.walk(unpacked):
    for f in files:
        if f == 'toc.txt':
            tocs.append(os.path.join(root, f))

print(f"Total TOCs: {len(tocs)}")

toc_bundles = {}
for t in tocs:
    rel = os.path.relpath(t, unpacked)
    folder = os.path.dirname(rel)
    with open(t, 'r', encoding='utf-8', errors='ignore') as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
    toc_bundles[folder] = lines

bundles = []
for root, dirs, files in os.walk(unpacked):
    for f in files:
        if f.endswith('.assetbundle'):
            rel = os.path.relpath(os.path.join(root, f), unpacked)
            bundles.append(rel)

print(f"Total .assetbundle files: {len(bundles)}")

# Check what each TOC refers to
bundle_basenames = {os.path.basename(b): b for b in bundles}

missing = []
matched = []
empty_tocs = []

for folder, lines in toc_bundles.items():
    if not lines:
        empty_tocs.append(folder)
        continue
    for line in lines:
        # TOC format: bundle_name size hash...
        parts = line.split()
        b_name = parts[0]
        if b_name in bundle_basenames:
            matched.append((folder, b_name, bundle_basenames[b_name]))
        else:
            missing.append((folder, b_name, parts))

print(f"\nMatched bundles from TOC: {len(matched)}")
print(f"Missing bundles from TOC: {len(missing)}")
print(f"Empty TOCs: {len(empty_tocs)}")
if empty_tocs:
    print(f"Empty TOC folders: {empty_tocs}")
if missing:
    print("Missing items:")
    for m in missing[:20]:
        print(" ", m)
