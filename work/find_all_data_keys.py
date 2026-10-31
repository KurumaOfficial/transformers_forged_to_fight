import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

data_dir = r".\work\unpacked\assets\bin\Data"

all_keys = {}

for f in os.listdir(data_dir):
    fp = os.path.join(data_dir, f)
    if os.path.isfile(fp) and f not in ["global-metadata.dat", "sharedassets0.resource", "unity default resources", "globalgamemanagers"]:
        try:
            with open(fp, "rb") as fh:
                data = fh.read()
            if b'"k"' in data and b'"v"' in data:
                for m in re.finditer(rb'\"k\"\s*:\s*\"([^\"]+)\"', data):
                    k = m.group(1).decode('utf-8', errors='ignore')
                    all_keys[k] = f
        except:
            pass

print(f"Total unique keys across ALL Data/ files: {len(all_keys)}")

story_keys = [k for k in all_keys if re.match(r'ID_S\d+', k) or "STORY" in k or "DIALOGUE" in k or "CUTSCENE" in k]
print(f"Story / Dialogue keys: {len(story_keys)}")
for sk in sorted(story_keys)[:25]:
    print(f"  {sk}")

quest_keys = [k for k in all_keys if "QUEST" in k or "MISSION" in k or "CHAPTER" in k or "ACT" in k]
print(f"\nQuest / Mission keys: {len(quest_keys)}")
for qk in sorted(quest_keys)[:25]:
    print(f"  {qk}")

bot_keys = [k for k in all_keys if "BIO" in k or "BOT" in k]
print(f"\nBot / Bio keys: {len(bot_keys)}")
for bk in sorted(bot_keys)[:25]:
    print(f"  {bk}")
