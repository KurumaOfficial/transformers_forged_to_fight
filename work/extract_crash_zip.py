import json
import zipfile
import io

with open('server/requests.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        entry = json.loads(line)
        if entry.get("path") == "/krash":
            body = entry.get("body", "")
            # convert each unicode char to its byte value
            raw_bytes = bytes([ord(c) & 0xFF for c in body])
            pk_idx = raw_bytes.find(b"PK\x03\x04")
            if pk_idx != -1:
                end_idx = raw_bytes.rfind(b"PK\x05\x06")
                if end_idx != -1:
                    zip_data = raw_bytes[pk_idx : end_idx + 22]
                    print(f"Extracted zip candidate length: {len(zip_data)}")
                    try:
                        zf = zipfile.ZipFile(io.BytesIO(zip_data))
                        print("Files in crash zip:", zf.namelist())
                        for name in zf.namelist():
                            print(f"\n==================== {name} ====================")
                            try:
                                data = zf.read(name)
                                print(data.decode('utf-8', errors='replace')[:2000])
                            except Exception as e:
                                print("Read error:", e)
                    except Exception as e:
                        print("Zip decode error:", e)
            break
