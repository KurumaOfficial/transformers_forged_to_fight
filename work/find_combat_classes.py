import re

with open('work/il2cpp_dump/dump.cs', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

classes_to_find = [
    'class FighterInitData',
    'class BCGAttributeDataBase',
    'class BCGAttributeData',
    'class HitData',
    'class CombatEngine',
    'class DamageCalculator',
    'class ArmorCalculator',
    'class CombatFormulas',
    'class Tuning'
]

for c in classes_to_find:
    pos = text.find(c)
    if pos != -1:
        start = max(0, pos - 100)
        end = min(len(text), pos + 1500)
        print(f"==========================================")
        print(f"Found {c}:")
        print(text[start:end])
    else:
        print(f"{c}: NOT FOUND")
