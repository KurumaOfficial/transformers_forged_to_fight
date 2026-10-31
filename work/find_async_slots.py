import re

raw = open("work/quests_async.txt", "rb").read()
if raw[:2] == b"\xff\xfe":
    text = raw.decode("utf-16")
else:
    text = raw.decode("utf-8", "replace")
lines = text.splitlines()

slots = []
last_adrp = None
for line in lines:
    m = re.match(r"0x([0-9a-f]+): adrp\s+x(\d+), #0x([0-9a-f]+)", line)
    if m:
        last_adrp = (int(m.group(1), 16), int(m.group(2)), int(m.group(3), 16))
        continue
    m = re.match(r"0x([0-9a-f]+): ldr\s+x(\d+), \[x(\d+), #0x([0-9a-f]+)\]", line)
    if m and last_adrp and m.group(3) == str(last_adrp[1]):
        slot = last_adrp[2] + int(m.group(4), 16)
        slots.append((int(m.group(1), 16), slot))
        continue
    if re.search(r"bl\s+#0x1d61a8c", line):
        pc = int(line.split(":")[0], 16)
        prior = [s for s in slots if s[0] < pc]
        print(hex(pc), hex(prior[-1][1]) if prior else "?")
