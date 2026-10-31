import os
import json

unpacked = r'work\unpacked\assets'
tocs = []
for root, dirs, files in os.walk(unpacked):
    for f in files:
        if f == 'toc.txt':
            tocs.append(os.path.join(root, f))

print(f"Total TOCs: {len(tocs)}")

all_toc_bundles = {}
tocs_without_bundles = []

for t in tocs:
    rel = os.path.relpath(t, unpacked)
    folder = os.path.dirname(rel)
    try:
        with open(t, 'r', encoding='utf-8') as f:
            data = json.load(f)
        bundles = data.get("bundles", {})
        if not bundles:
            tocs_without_bundles.append((folder, data))
        for bname, binfo in bundles.items():
            all_toc_bundles[bname] = {
                "toc_folder": folder,
                "file": binfo.get("file"),
                "crc": binfo.get("crc"),
                "scenes": list(data.get("scenes", {}).keys()),
                "paths_count": len(binfo.get("paths", {}))
            }
    except Exception as e:
        print(f"Error parsing {rel}: {e}")

print(f"Total bundle definitions in all TOCs: {len(all_toc_bundles)}")
print(f"TOCs with no 'bundles' dictionary: {len(tocs_without_bundles)}")
for folder, data in tocs_without_bundles:
    print(f"  Empty TOC folder: {folder}, keys={list(data.keys())}, scenes={list(data.get('scenes', {}).keys())}")

# Now match with actual .assetbundle files on disk
actual_bundles = set()
for root, dirs, files in os.walk(unpacked):
    for f in files:
        if f.endswith('.assetbundle'):
            actual_bundles.add(f)

print(f"Total actual .assetbundle files on disk: {len(actual_bundles)}")

# Find differences
toc_files = set()
for bname, info in all_toc_bundles.items():
    fpath = info.get("file", "")
    fname = os.path.basename(fpath) if fpath else bname + ".assetbundle"
    toc_files.add(fname)

print(f"Unique bundle filenames mentioned across all TOCs: {len(toc_files)}")

in_toc_not_on_disk = toc_files - actual_bundles
on_disk_not_in_toc = actual_bundles - toc_files

print(f"In TOC but not on disk: {len(in_toc_not_on_disk)} -> {in_toc_not_on_disk}")
print(f"On disk but not in TOC: {len(on_disk_not_in_toc)} -> {on_disk_not_in_toc}")

# Check duplicate TOCs (e.g. folder vs folder_odr)
folders = [os.path.dirname(os.path.relpath(t, unpacked)) for t in tocs]
print(f"\nAll 108 TOC folders:")
for fld in sorted(folders):
    print(" ", fld)
