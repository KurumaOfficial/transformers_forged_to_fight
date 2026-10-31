import re, sys

sys.stdout.reconfigure(encoding='utf-8')
with open('work/il2cpp_dump/dump.cs', 'r', encoding='utf-8') as f:
    text = f.read()

classes_to_find = [
    'BCGEvoBlueprintBase',
    'BCGStatModifier',
    'BCGStatModifierAppearance',
    'BCGHeroBase',
    'TFBCGBlueprintBase',
    'BCGBlueprintBase',
    'TFBCGCharacterData',
    'BCGSynergyBonus',
    'BCGAttackValue',
    'BCGBlueprintBonuses',
    'BCGHeroClasses',
    'BCGStaminaRegen',
    'BCGRarityProperty',
    'BCGEvoCosts',
    'BCGCurve',
    'BCGUserData'
]

for c in classes_to_find:
    pattern = rf'(public(?: abstract)? class {c}\b[^\n]*\n\{{.*?\n\}})'
    m = re.search(pattern, text, re.DOTALL)
    if m:
        body = m.group(1)
        # extract fields and methods (.ctor)
        print('='*50)
        print(f'CLASS: {c}')
        lines = body.split('\n')
        for line in lines:
            if 'public' in line or 'private' in line or 'protected' in line:
                if any(k in line for k in ['// Fields', '// Properties', '// Methods', '.ctor', 'get_', 'set_']) or ';' in line:
                    print('  ', line.strip())
    else:
        print(f'NOT FOUND: {c}')
