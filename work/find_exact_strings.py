with open('work/string_literals.txt', 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) >= 2:
            s = parts[1]
            if s in ['user', 'user_id', 'userid', 'userId', 'id', 'token', 'userToken', 'stoken']:
                print(line.strip())
