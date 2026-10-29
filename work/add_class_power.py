from pathlib import Path

p = Path("server/stub_server.py")
s = p.read_text(encoding="utf-8")

# Top-level getBaseHeroData fields.
old = '''                    "mana_gain": 1.0,
                    "mana_start": 0,
                    "resist_magic": 0.0,'''
new = '''                    "mana_gain": 1.0,
                    "mana_start": 0,
                    "class_power": 1.0,
                    "resist_magic": 0.0,'''
if old not in s:
    raise SystemExit("getBaseHeroData mana_gain block not found")
s = s.replace(old, new, 1)

# Nested attributeData camelCase.
old = '''                        "manaGain": 1.0,
                        "manaStart": 0,
                        "resistMagic": 0.0,'''
new = '''                        "manaGain": 1.0,
                        "manaStart": 0,
                        "classPower": 1.0,
                        "resistMagic": 0.0,'''
if old not in s:
    raise SystemExit("attributeData block not found")
s = s.replace(old, new, 1)

# quest team_data.
old = '''                        "mana_gain": 1.0,
                        "mana_start": 0.0,
                        "resist_magic": 0.0,'''
new = '''                        "mana_gain": 1.0,
                        "mana_start": 0.0,
                        "class_power": 1.0,
                        "resist_magic": 0.0,'''
if old not in s:
    raise SystemExit("team_data block not found")
s = s.replace(old, new, 1)

# hero_details.
old = '''                    "mana_gain": 1.0, "mana_start": 0.0,
                    "resist_magic": 0.0, "resist_physical": 0.0,'''
new = '''                    "mana_gain": 1.0, "mana_start": 0.0,
                    "class_power": 1.0,
                    "resist_magic": 0.0, "resist_physical": 0.0,'''
if old not in s:
    raise SystemExit("hero_details block not found")
s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("class_power added")
