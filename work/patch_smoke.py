from pathlib import Path

p = Path("work/smoke_test.py")
s = p.read_text(encoding="utf-8")
old = '''        tap(2097, 1003, 4)
        # START with fewer bots than the roster may prompt "ADD MORE BOTS?".
        # Only tap CONTINUE when the prompt's green buttons are visible;
        # otherwise the tap would hit the map and open NODE INFO.
        for _ in range(3):
            if green_button_in_region(450, 720):
                tap(1339, 550, 8)
                break
            time.sleep(3)
        else:
            time.sleep(4)
        step("06_map")
'''
new = '''        tap(2097, 1003, 4)
        # START may briefly show "ADD MORE BOTS?", then loads the map. Wait for
        # the quest-begin request and a fixed settle time. Do not use the old
        # green-button heuristic here: the map glow false-positives and the
        # extra tap opened NODE INFO instead of the battle tile.
        base_count = len(read_requests())
        deadline = time.time() + 30
        while time.time() < deadline:
            rows = read_requests()[base_count:]
            if any("/quests/quest-begin" in (r.get("path") or "") for r in rows):
                break
            time.sleep(0.5)
        time.sleep(6)
        step("06_map")
'''
if old not in s:
    raise SystemExit("smoke block not found")
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("patched smoke")
