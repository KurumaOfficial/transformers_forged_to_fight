import json

for path in ['server/data/account_data.json', 'server/data/login_response.json']:
    with open(path, 'r', encoding='utf-8') as f:
        d = json.load(f)
    if 'user' in d and isinstance(d['user'], dict):
        d['user']['level'] = 5
        d['user']['xp'] = 1000
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(d, f, indent=2)
    print(f'Updated {path}')
