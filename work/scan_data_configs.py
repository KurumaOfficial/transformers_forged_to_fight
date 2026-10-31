import os
import re
import json

data_dir = r".\work\unpacked\assets\bin\Data"

configs = []
for f in os.listdir(data_dir):
    fp = os.path.join(data_dir, f)
    if os.path.isfile(fp) and f not in ["global-metadata.dat", "sharedassets0.resource", "unity default resources", "globalgamemanagers"]:
        try:
            with open(fp, "rb") as fh:
                data = fh.read()
            if b"{" in data and b"}" in data:
                # Look for readable text between braces
                # In Unity TextAsset, format is:
                # int name_len, string name, align, int script_len, bytes script
                # Let's search for JSON text
                for m in re.finditer(rb'\{[\s\S]*?\}', data):
                    snippet = m.group(0)
                    if len(snippet) > 10 and b'"' in snippet:
                        try:
                            # Try decoding as json
                            txt = snippet.decode('utf-8', errors='ignore')
                            # see if valid json
                            parsed = json.loads(txt)
                            configs.append((f, len(data), parsed))
                            break
                        except:
                            pass
        except Exception as e:
            pass

print(f"Total files with valid JSON in Data/: {len(configs)}")
for fname, fsize, parsed in configs:
    keys = list(parsed.keys()) if isinstance(parsed, dict) else len(parsed)
    print(f"{fname} ({fsize} bytes): {keys}")
    # Print sample
    s = json.dumps(parsed)[:200]
    print(f"   {s}")
